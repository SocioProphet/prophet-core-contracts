#!/usr/bin/env python3
"""Validate PolicyRequest and PolicyDecision v0.1 examples and fixtures."""

from __future__ import annotations

import copy
import hashlib
import hmac
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, ValidationError

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "schemas"
EXAMPLES = ROOT / "examples" / "policy"
NEG = EXAMPLES / "negative"
VALIDATION_TIME = "2026-05-12T04:30:00Z"
TEST_SECRET = b"policy-test-secret-v0.1"

REQUEST_SCHEMA = SCHEMAS / "policy-request.schema.json"
DECISION_SCHEMA = SCHEMAS / "policy-decision.schema.json"
REQUEST_EXAMPLE = EXAMPLES / "policy-request.example.json"
DECISION_EXAMPLES = [
    "policy-decision.allow-with-constraints.example.json",
    "policy-decision.allow.example.json",
    "policy-decision.deny.example.json",
    "policy-decision.require-review.example.json",
    "policy-decision.quarantine.example.json",
    "policy-decision.revoke.example.json",
]
NEGATIVE_FIXTURES = [
    "policy-request.missing-request-id.invalid.json",
    "policy-request.bad-hash.invalid.json",
    "policy-request.self-contradictory.invalid.json",
    "policy-decision.missing-decision-id.invalid.json",
    "policy-decision.input-hash-mismatch.invalid.json",
    "policy-decision.expired-window.invalid.json",
    "policy-decision.deny-with-grant.invalid.json",
    "policy-decision.contradictory-restrictions.invalid.json",
    "policy-decision.non-grant-no-reason.invalid.json",
    "policy-decision.payload-tamper.invalid.json",
    "policy-decision.invalid-signature.invalid.json",
    "policy-decision.empty-signatures.invalid.json",
    "policy-decision.revoke-missing-ref.invalid.json",
    "policy-decision.allow-with-constraints-empty.invalid.json",
]

GRANT_STATUSES = {"allow", "allow_with_constraints"}
NON_GRANT_STATUSES = {"deny", "require_review", "quarantine", "revoke"}
LEARNING_SINKS = {"model_training", "embedding_generation", "durable_memory", "analytics_warehouse"}
LINKING_SINKS = {"cross_domain_identity_linking", "canonical_entity_merge"}


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_prefixed(value: str | bytes) -> str:
    data = value if isinstance(value, bytes) else value.encode("utf-8")
    return "sha256:" + hashlib.sha256(data).hexdigest()


def signature_for_payload_hash(payload_hash: str) -> str:
    return "sha256:" + hmac.new(TEST_SECRET, payload_hash.encode("utf-8"), hashlib.sha256).hexdigest()


def parse_instant(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def request_payload_material(request: dict[str, Any]) -> dict[str, Any]:
    material = copy.deepcopy(request)
    material.pop("request_hash", None)
    return material


def expected_request_hash(request: dict[str, Any]) -> str:
    return sha256_prefixed(canonical_json(request_payload_material(request)))


def decision_payload_material(decision: dict[str, Any]) -> dict[str, Any]:
    material = copy.deepcopy(decision)
    material.pop("payload_hash", None)
    material.pop("signatures", None)
    return material


def expected_decision_payload_hash(decision: dict[str, Any]) -> str:
    return sha256_prefixed(canonical_json(decision_payload_material(decision)))


def pointer_tokens(path: str) -> list[str]:
    if not path.startswith("/"):
        raise AssertionError(f"JSON pointer must start with /: {path}")
    return [token.replace("~1", "/").replace("~0", "~") for token in path[1:].split("/")]


def resolve_parent(document: Any, path: str) -> tuple[Any, str]:
    tokens = pointer_tokens(path)
    parent = document
    for token in tokens[:-1]:
        parent = parent[int(token)] if isinstance(parent, list) else parent[token]
    return parent, tokens[-1]


def apply_mutation(document: dict[str, Any], mutation: dict[str, Any] | None) -> dict[str, Any]:
    mutated = copy.deepcopy(document)
    if not mutation:
        return mutated
    parent, token = resolve_parent(mutated, mutation["path"])
    op = mutation["op"]
    if op == "replace":
        if isinstance(parent, list):
            parent[int(token)] = mutation["value"]
        else:
            if token not in parent:
                raise AssertionError(f"cannot replace missing path: {mutation['path']}")
            parent[token] = mutation["value"]
    elif op == "remove":
        if isinstance(parent, list):
            del parent[int(token)]
        else:
            del parent[token]
    elif op == "add":
        if isinstance(parent, list):
            parent.append(mutation["value"]) if token == "-" else parent.insert(int(token), mutation["value"])
        else:
            parent[token] = mutation["value"]
    else:
        raise AssertionError(f"unsupported mutation op: {op}")
    return mutated


def schema_failure_code(error: ValidationError) -> str:
    path = list(error.path)
    field = path[-1] if path else None
    if error.validator == "required":
        missing = str(error.message).split("'")[1]
        return f"schema_required_{missing}"
    if error.validator == "const" and field:
        return f"schema_const_{field}_{error.validator_value}"
    if error.validator == "enum" and field:
        return f"schema_enum_{field}"
    if error.validator == "pattern" and field:
        return f"schema_pattern_{field}"
    return f"schema_{error.validator}_{field or 'root'}"


def request_failure_codes(request: dict[str, Any]) -> set[str]:
    codes: set[str] = set()
    try:
        if request.get("request_hash") != expected_request_hash(request):
            codes.add("semantic_request_hash_mismatch")
        for action in request.get("requested_actions", []):
            requested = set(action.get("requested_sinks", []))
            forbidden = set(action.get("requested_forbidden_sinks", []))
            if requested & forbidden:
                codes.add("semantic_request_self_contradictory_sink")
    except Exception:
        pass
    return codes


def decision_failure_codes(decision: dict[str, Any], request: dict[str, Any]) -> set[str]:
    codes: set[str] = set()
    try:
        if decision.get("input_hash") != request.get("request_hash"):
            codes.add("semantic_input_hash_mismatch")
        ref = decision.get("policy_request_ref", {})
        if ref.get("request_id") != request.get("request_id") or ref.get("request_hash") != request.get("request_hash"):
            codes.add("semantic_policy_request_ref_mismatch")
        if parse_instant(VALIDATION_TIME) > parse_instant(decision["decision_valid_until"]):
            codes.add("semantic_decision_expired")
        expected_hash = expected_decision_payload_hash(decision)
        if decision.get("payload_hash") != expected_hash:
            codes.add("semantic_payload_hash_mismatch")
        signatures = decision.get("signatures", [])
        if len(signatures) < int(decision.get("min_signatures", 1)):
            codes.add("semantic_quorum_not_satisfied")
        valid_signature_count = 0
        for signature in signatures:
            if signature.get("algorithm") == "hmac-sha256-test-v0.1" and signature.get("key_id") == "test-policy-key" and signature.get("value") == signature_for_payload_hash(decision.get("payload_hash", "")):
                valid_signature_count += 1
        if signatures and valid_signature_count == 0:
            codes.add("semantic_signature_mismatch")
        if valid_signature_count < int(decision.get("min_signatures", 1)):
            codes.add("semantic_quorum_not_satisfied")

        status = decision.get("decision_status")
        granted_actions = decision.get("granted_actions", [])
        restrictions = set(decision.get("restrictions", []))
        reason_codes = set(decision.get("reason_codes", []))

        if status in GRANT_STATUSES and not granted_actions:
            codes.add("semantic_grant_missing_granted_actions")
        if status in NON_GRANT_STATUSES and granted_actions:
            codes.add("semantic_non_grant_has_granted_actions")
        if status in NON_GRANT_STATUSES and not reason_codes:
            codes.add("semantic_non_grant_missing_reason_code")
        if status == "allow" and restrictions:
            codes.add("semantic_plain_allow_has_restrictions")
        if status == "allow_with_constraints" and not restrictions:
            codes.add("semantic_constrained_allow_missing_restrictions")
        if status == "revoke" and not decision.get("revokes_decision_ref"):
            codes.add("semantic_revoke_missing_ref")
        if status == "require_review" and "human_review_required" not in reason_codes:
            codes.add("semantic_require_review_missing_reason")
        if status == "quarantine" and "safety_quarantine" not in reason_codes:
            codes.add("semantic_quarantine_missing_reason")
        if status == "revoke" and "revoked_by_authority" not in reason_codes:
            codes.add("semantic_revoke_missing_reason")

        for action in granted_actions:
            allowed = set(action.get("allowed_sinks", []))
            forbidden = set(action.get("forbidden_sinks", []))
            if allowed & forbidden:
                codes.add("semantic_action_sink_conflict")
            if "DoNotLearn" in restrictions and (allowed & LEARNING_SINKS):
                codes.add("semantic_contradictory_restrictions")
            if "DoNotLink" in restrictions and (allowed & LINKING_SINKS):
                codes.add("semantic_contradictory_restrictions")
    except Exception:
        pass
    return codes


def validate_positive() -> None:
    request_schema = load_json(REQUEST_SCHEMA)
    decision_schema = load_json(DECISION_SCHEMA)
    request = load_json(REQUEST_EXAMPLE)
    Draft202012Validator.check_schema(request_schema)
    Draft202012Validator.check_schema(decision_schema)
    Draft202012Validator(request_schema).validate(request)
    request_codes = request_failure_codes(request)
    if request_codes:
        raise AssertionError(f"positive PolicyRequest failed semantic validation: {sorted(request_codes)}")
    for example_name in DECISION_EXAMPLES:
        decision = load_json(EXAMPLES / example_name)
        Draft202012Validator(decision_schema).validate(decision)
        codes = decision_failure_codes(decision, request)
        if codes:
            raise AssertionError(f"positive PolicyDecision {example_name} failed semantic validation: {sorted(codes)}")
        print(f"validated {example_name}")
    print("validated policy-request.example.json")


def validate_negative(fixture_name: str) -> None:
    request_schema = load_json(REQUEST_SCHEMA)
    decision_schema = load_json(DECISION_SCHEMA)
    request = load_json(REQUEST_EXAMPLE)
    fixture = load_json(NEG / fixture_name)
    target = fixture["target"]
    expected = fixture["expected_failure"]

    if target == "request":
        mutated = apply_mutation(request, fixture.get("mutation"))
        failure_codes = {schema_failure_code(error) for error in Draft202012Validator(request_schema).iter_errors(mutated)}
        failure_codes |= request_failure_codes(mutated)
    elif target == "decision":
        base_name = fixture.get("base_example", "policy-decision.allow-with-constraints.example.json")
        decision = load_json(EXAMPLES / base_name)
        mutated = apply_mutation(decision, fixture.get("mutation"))
        failure_codes = {schema_failure_code(error) for error in Draft202012Validator(decision_schema).iter_errors(mutated)}
        failure_codes |= decision_failure_codes(mutated, request)
    else:
        raise AssertionError(f"unknown negative fixture target: {target}")

    if not failure_codes:
        raise AssertionError(f"negative fixture unexpectedly passed: {fixture_name}")
    if expected not in failure_codes:
        raise AssertionError(f"negative fixture {fixture_name} failed for {sorted(failure_codes)}, expected {expected}")
    print(f"rejected {fixture_name}: {expected}")


def main() -> int:
    missing = []
    for path in [REQUEST_SCHEMA, DECISION_SCHEMA, REQUEST_EXAMPLE]:
        if not path.exists():
            missing.append(str(path))
    for example in DECISION_EXAMPLES:
        if not (EXAMPLES / example).exists():
            missing.append(str(EXAMPLES / example))
    for fixture in NEGATIVE_FIXTURES:
        if not (NEG / fixture).exists():
            missing.append(str(NEG / fixture))
    if missing:
        raise SystemExit("Missing policy validation files:\n" + "\n".join(missing))

    validate_positive()
    for fixture in NEGATIVE_FIXTURES:
        validate_negative(fixture)
    print("PolicyRequest/PolicyDecision validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
