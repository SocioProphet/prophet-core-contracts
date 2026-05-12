"""Reference AdmissionToken v0.1 type.

This module is intentionally small and dependency-free. It is a reference
implementation for the contract shape, not a production key-management system.

Design rule: consumers may verify AdmissionToken objects, but only the
Operation Plane may construct them through ``AdmissionToken.from_admission``.
Direct construction raises ``TypeError``.
"""

from __future__ import annotations

import hashlib
import hmac
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping, Protocol

AUTHORITY_ORDER = ["observe", "recommend", "represent", "negotiate", "commit"]
TEST_SECRET = b"admission-test-secret-v0.1"


class PolicyFabric(Protocol):
    """Producer of policy decisions consumed by the Operation Plane."""

    def decide(self, action: Mapping[str, Any]) -> Mapping[str, Any]:
        ...


class AgentRegistry(Protocol):
    """Producer of authority decisions consumed by the Operation Plane."""

    def authorize(self, action: Mapping[str, Any]) -> Mapping[str, Any]:
        ...


class OperationPlane(Protocol):
    """Only producer of AdmissionToken objects."""

    def admit(
        self,
        proposed_action: Mapping[str, Any],
        policy_decision: Mapping[str, Any],
        authority_decision: Mapping[str, Any],
    ) -> "AdmissionToken":
        ...


class AdmissionConsumer(Protocol):
    """Consumer that verifies AdmissionToken before side effects."""

    def verify_admission(self, token: "AdmissionToken", request: Mapping[str, str]) -> bool:
        ...


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _sha256_prefixed(value: str | bytes) -> str:
    data = value if isinstance(value, bytes) else value.encode("utf-8")
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _signature_for_payload_hash(payload_hash: str) -> str:
    return "sha256:" + hmac.new(TEST_SECRET, payload_hash.encode("utf-8"), hashlib.sha256).hexdigest()


def _parse_instant(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _authority_rank(value: str) -> int:
    return AUTHORITY_ORDER.index(value)


@dataclass(frozen=True, slots=True, init=False)
class AdmissionToken:
    schema_version: str
    token_id: str
    token_type: str
    issuer_id: str
    issued_at: str
    expires_at: str
    status: str
    proposed_action_ref: Mapping[str, Any]
    policy_decision_ref: Mapping[str, Any]
    authority_decision_ref: Mapping[str, Any]
    sink_restrictions: Mapping[str, Any]
    allowed_operation: Mapping[str, Any]
    evidence_refs: tuple[str, ...]
    nonce: str
    payload_hash: str
    signature: Mapping[str, str]

    def __init__(self, *_: Any, **__: Any) -> None:
        raise TypeError("AdmissionToken cannot be constructed directly; use AdmissionToken.from_admission")

    @classmethod
    def from_admission(
        cls,
        *,
        token_id: str,
        issuer_id: str,
        issued_at: str,
        expires_at: str,
        proposed_action_ref: Mapping[str, Any],
        policy_decision_ref: Mapping[str, Any],
        authority_decision_ref: Mapping[str, Any],
        sink_restrictions: Mapping[str, Any],
        allowed_operation: Mapping[str, Any],
        evidence_refs: tuple[str, ...],
        nonce: str,
    ) -> "AdmissionToken":
        token = object.__new__(cls)
        object.__setattr__(token, "schema_version", "0.1.0")
        object.__setattr__(token, "token_id", token_id)
        object.__setattr__(token, "token_type", "single_use")
        object.__setattr__(token, "issuer_id", issuer_id)
        object.__setattr__(token, "issued_at", issued_at)
        object.__setattr__(token, "expires_at", expires_at)
        object.__setattr__(token, "status", "issued")
        object.__setattr__(token, "proposed_action_ref", dict(proposed_action_ref))
        object.__setattr__(token, "policy_decision_ref", dict(policy_decision_ref))
        object.__setattr__(token, "authority_decision_ref", dict(authority_decision_ref))
        object.__setattr__(token, "sink_restrictions", dict(sink_restrictions))
        object.__setattr__(token, "allowed_operation", dict(allowed_operation))
        object.__setattr__(token, "evidence_refs", tuple(evidence_refs))
        object.__setattr__(token, "nonce", nonce)
        payload_hash = token.compute_payload_hash()
        object.__setattr__(token, "payload_hash", payload_hash)
        object.__setattr__(
            token,
            "signature",
            {
                "algorithm": "hmac-sha256-test-v0.1",
                "key_id": "test-admission-key",
                "value": _signature_for_payload_hash(payload_hash),
            },
        )
        return token

    def payload_material(self) -> dict[str, Any]:
        return {
            "allowed_operation": dict(self.allowed_operation),
            "authority_decision_ref": dict(self.authority_decision_ref),
            "evidence_refs": list(self.evidence_refs),
            "expires_at": self.expires_at,
            "issued_at": self.issued_at,
            "issuer_id": self.issuer_id,
            "nonce": self.nonce,
            "policy_decision_ref": dict(self.policy_decision_ref),
            "proposed_action_ref": dict(self.proposed_action_ref),
            "schema_version": self.schema_version,
            "sink_restrictions": dict(self.sink_restrictions),
            "status": self.status,
            "token_id": self.token_id,
            "token_type": self.token_type,
        }

    def compute_payload_hash(self) -> str:
        return _sha256_prefixed(_canonical_json(self.payload_material()))

    def verify(self, request: Mapping[str, str], *, now: datetime | None = None) -> bool:
        if self.status != "issued":
            return False
        if (now or _now_utc()) > _parse_instant(self.expires_at):
            return False
        if self.payload_hash != self.compute_payload_hash():
            return False
        if self.signature.get("value") != _signature_for_payload_hash(self.payload_hash):
            return False
        if self.proposed_action_ref["action_type"] != request["action_type"]:
            return False
        if self.allowed_operation["operation_type"] != request["action_type"]:
            return False
        if self.proposed_action_ref["target_ref"] != request["resource_ref"]:
            return False
        if self.allowed_operation["resource_ref"] != request["resource_ref"]:
            return False
        if _authority_rank(request["authority_band"]) > _authority_rank(self.allowed_operation["max_authority_band"]):
            return False
        sink = request["sink"]
        if sink in self.sink_restrictions["forbidden_sinks"]:
            return False
        if sink not in self.sink_restrictions["allowed_sinks"]:
            return False
        if sink in {"model_training", "embedding_generation", "durable_memory", "analytics_warehouse"} and self.sink_restrictions.get("do_not_learn") is True:
            return False
        if sink in {"cross_domain_identity_linking", "canonical_entity_merge"} and self.sink_restrictions.get("do_not_link") is True:
            return False
        return True

    def to_dict(self) -> dict[str, Any]:
        result = self.payload_material()
        result["payload_hash"] = self.payload_hash
        result["signature"] = dict(self.signature)
        return result
