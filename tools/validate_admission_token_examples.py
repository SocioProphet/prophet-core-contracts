#!/usr/bin/env python3
"""Validate Operation Plane AdmissionToken v0.1 examples and negative fixtures."""

from __future__ import annotations

import copy
import hashlib
import hmac
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, ValidationError

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schemas" / "admission-token.schema.json"
EXAMPLES = ROOT / "examples" / "admission-token"
NEG = EXAMPLES / "negative"
VALIDATION_TIME = "2026-05-12T04:05:00Z"
CLOCK_SKEW_SECONDS = 60
TEST_SECRET = b"admission-test-secret-v0.1"

NEGATIVE_FIXTURES = [
    "admission-token.schema-missing-token-id.invalid.json",
    "admission-token.expired.invalid.json",
    "admission-token.missing-policy-decision.invalid.json",
    "admission-token.action-mismatch.invalid.json",
    "admission-token.invalid-signature.invalid.json",
    "admission-token.payload-hash-tampered.invalid.json",
    "admission-token.consumed-replay.invalid.json",
    "admission-token.authority-ceiling.invalid.json",
    "admission-token.forbidden-sink.invalid.json",
]

AUTHORITY_ORDER = ["observe", "recommend", "represent", "negotiate", "commit"]


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


def authority_rank(value: str) -> int:
    return AUTHORITY_ORDER.index(value)


def token_payload_material(token: dict[str, Any]) -> dict[str, Any]:
    material = copy.deepcopy(token)
    material.pop("payload_hash", None)
    material.pop("signature", None)
    return material


def expected_payload_hash(token: dict[str, Any]) -> str:
    return sha256_prefixed(canonical_json(token_payload_material(token)))


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


def semantic_failure_codes(token: dict[str, Any], request: dict[str, str]) -> set[str]:
    codes: set[str] = set()
    try:
        if token.get("status") != "issued":
            codes.add("semantic_token_not_issued")

        check_time = parse_instant(VALIDATION_TIME)
        if check_time < parse_instant(token["issued_at"]) - timedelta(seconds=CLOCK_SKEW_SECONDS):
            codes.add("semantic_token_not_yet_valid")
        if check_time > parse_instant(token["expires_at"]) + timedelta(seconds=CLOCK_SKEW_SECONDS):
            codes.add("semantic_token_expired")

        expected_hash = expected_payload_hash(token)
        if token.get("payload_hash") != expected_hash:
            codes.add("semantic_payload_hash_mismatch")

        signature = token.get("signature", {})
        if signature.get("algorithm") != "hmac-sha256-test-v0.1" or signature.get("key_id") != "test-admission-key":
            codes.add("semantic_signature_profile_mismatch")
        if signature.get("value") != signature_for_payload_hash(token.get("payload_hash", "")):
            codes.add("semantic_signature_mismatch")

        action = token["proposed_action_ref"]
        allowed = token["allowed_operation"]
        if action["action_type"] != request["action_type"] or allowed["operation_type"] != request["action_type"]:
            codes.add("semantic_action_mismatch")
        if allowed["resource_ref"] != request["resource_ref"] or action["target_ref"] != request["resource_ref"]:
            codes.add("semantic_resource_mismatch")
        if authority_rank(request["authority_band"]) > authority_rank(allowed["max_authority_band"]):
            codes.add("semantic_authority_exceeds_token")

        restrictions = token["sink_restrictions"]
        sink = request["sink"]
        if sink in restrictions["forbidden_sinks"] or sink not in restrictions["allowed_sinks"]:
            codes.add("semantic_forbidden_sink")
        if sink in {"model_training", "embedding_generation", "durable_memory", "analytics_warehouse"} and restrictions.get("do_not_learn") is True:
            codes.add("semantic_do_not_learn_sink")
        if sink in {"cross_domain_identity_linking", "canonical_entity_merge"} and restrictions.get("do_not_link") is True:
            codes.add("semantic_do_not_link_sink")
    except Exception:
        # Schema validation owns malformed-shape failures.
        pass
    return codes


def default_request(token: dict[str, Any]) -> dict[str, str]:
    return {
        "action_type": token["allowed_operation"]["operation_type"],
        "resource_ref": token["allowed_operation"]["resource_ref"],
        "authority_band": token["allowed_operation"]["max_authority_band"],
        "sink": token["sink_restrictions"]["allowed_sinks"][0],
    }


def validate_positive() -> None:
    schema = load_json(SCHEMA)
    token = load_json(EXAMPLES / "admission-token.single-use.example.json")
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(token)
    codes = semantic_failure_codes(token, default_request(token))
    if codes:
        raise AssertionError(f"positive AdmissionToken failed semantic validation: {sorted(codes)}")
    print("validated admission-token.single-use.example.json")


def validate_negative(fixture_name: str) -> None:
    schema = load_json(SCHEMA)
    base = load_json(EXAMPLES / "admission-token.single-use.example.json")
    fixture = load_json(NEG / fixture_name)
    token = apply_mutation(base, fixture.get("mutation"))
    request = default_request(base)
    request.update(fixture.get("request_override", {}))
    expected = fixture["expected_failure"]

    failure_codes = {schema_failure_code(error) for error in Draft202012Validator(schema).iter_errors(token)}
    failure_codes |= semantic_failure_codes(token, request)

    if not failure_codes:
        raise AssertionError(f"negative fixture unexpectedly passed: {fixture_name}")
    if expected not in failure_codes:
        raise AssertionError(f"negative fixture {fixture_name} failed for {sorted(failure_codes)}, expected {expected}")
    print(f"rejected {fixture_name}: {expected}")


def main() -> int:
    missing = []
    for path in [SCHEMA, EXAMPLES / "admission-token.single-use.example.json"]:
        if not path.exists():
            missing.append(str(path))
    for fixture in NEGATIVE_FIXTURES:
        if not (NEG / fixture).exists():
            missing.append(str(NEG / fixture))
    if missing:
        raise SystemExit("Missing AdmissionToken validation files:\n" + "\n".join(missing))

    validate_positive()
    for fixture in NEGATIVE_FIXTURES:
        validate_negative(fixture)
    print("AdmissionToken example validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
