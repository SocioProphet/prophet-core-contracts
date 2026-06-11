#!/usr/bin/env python3
"""Validate Regis Semantic Feature Plane examples and negative fixtures."""

from __future__ import annotations

import copy
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, ValidationError

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "schemas" / "regis"
EXAMPLES = ROOT / "examples" / "regis"
NEG = EXAMPLES / "negative"

EXAMPLE_TO_SCHEMA = {
    "twin-projection-feature.example.json": "twin-projection-feature.schema.json",
    "twin-projection-feature.string.example.json": "twin-projection-feature.schema.json",
    "twin-projection-feature.boolean.example.json": "twin-projection-feature.schema.json",
    "twin-projection-feature.number.example.json": "twin-projection-feature.schema.json",
    "twin-projection-feature.array.example.json": "twin-projection-feature.schema.json",
    "embedding-card.example.json": "embedding-card.schema.json",
    "promotion-decision.evidence-only.example.json": "promotion-decision.schema.json",
}

NEGATIVE_FIXTURES = [
    "twin-projection-feature.denied-field-emitted.invalid.json",
    "twin-projection-feature.unsafe-reason-leak.invalid.json",
    "twin-projection-feature.raw-twin-payload.invalid.json",
    "twin-projection-feature.missing-do-not-learn.invalid.json",
    "twin-projection-feature.do-not-learn-false.invalid.json",
    "twin-projection-feature.do-not-link-false.invalid.json",
    "twin-projection-feature.unknown-feature-family.invalid.json",
    "twin-projection-feature.unsafe-authority-band.invalid.json",
    "twin-projection-feature.bad-content-hash.invalid.json",
    "twin-projection-feature.bad-lineage-hash.invalid.json",
    "twin-projection-feature.replay-after-revocation.invalid.json",
    "twin-projection-feature.expired-consent-allowed.invalid.json",
    "twin-projection-feature.authority-downgrade-missed.invalid.json",
    "twin-projection-feature.null-feature-value.invalid.json",
]

AUTHORITY_ORDER = ["observe", "recommend", "represent", "negotiate", "commit"]
AUTHORITY_FIELDS = {"effective_authority_band", "authority_band", "approval_band", "max_authority_band"}


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_prefixed(value: str) -> str:
    return "sha256:" + hashlib.sha256(value.encode("utf-8")).hexdigest()


def parse_instant(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def min_authority(values: list[str | None]) -> str:
    present = [value for value in values if value]
    if not present:
        return "observe"
    return min(present, key=AUTHORITY_ORDER.index)


def code_value(value: Any) -> str:
    if isinstance(value, bool):
        return str(value).lower()
    if value is None:
        return "null"
    return str(value)


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


def apply_mutations(document: dict[str, Any], mutations: list[dict[str, Any]]) -> dict[str, Any]:
    mutated = copy.deepcopy(document)
    for mutation in mutations:
        parent, token = resolve_parent(mutated, mutation["path"])
        op = mutation["op"]
        if op == "replace":
            if isinstance(parent, list):
                parent[int(token)] = mutation["value"]
            else:
                if token not in parent:
                    raise AssertionError(f"cannot replace missing path: {mutation['path']}")
                parent[token] = mutation["value"]
        elif op == "add":
            if isinstance(parent, list):
                parent.append(mutation["value"]) if token == "-" else parent.insert(int(token), mutation["value"])
            else:
                parent[token] = mutation["value"]
        elif op == "remove":
            if isinstance(parent, list):
                del parent[int(token)]
            else:
                del parent[token]
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
        return f"schema_const_{field}_{code_value(error.validator_value)}"
    if error.validator == "enum" and field in AUTHORITY_FIELDS:
        return "schema_enum_authority_band"
    if error.validator == "enum" and field:
        return f"schema_enum_{field}"
    if error.validator == "additionalProperties":
        return "schema_additional_property_forbidden"
    if error.validator == "type" and field:
        return f"schema_type_{field}"
    return f"schema_{error.validator}_{field or 'root'}"


def semantic_failure_codes(example: dict[str, Any]) -> set[str]:
    codes: set[str] = set()
    try:
        expected_content_hash = sha256_prefixed(canonical_json(example["feature_value"]))
        if example["content_hash"] != expected_content_hash:
            codes.add("semantic_content_hash_mismatch")

        lineage_material = "||".join([
            example["projection_id"],
            example["decision_log_id"],
            example["policy_id"],
            example["schema_version"],
            example["created_at"],
        ])
        expected_lineage_hash = sha256_prefixed(lineage_material)
        if example["lineage_hash"] != expected_lineage_hash:
            codes.add("semantic_lineage_hash_mismatch")

        decision_log_ref = example["projection_decision_log_ref"]
        for key in ["projection_id", "decision_log_id", "twin_id", "subject_id", "mission_id", "recipient_id", "policy_id"]:
            if example[key] != decision_log_ref[key]:
                codes.add(f"semantic_decision_log_ref_{key}_mismatch")

        consent_scope = example["consent_scope_snapshot"]
        for key in ["policy_id", "subject_id", "recipient_id"]:
            if example[key] != consent_scope[key]:
                codes.add(f"semantic_consent_scope_{key}_mismatch")

        mission_governance = example["mission_governance_snapshot"]
        if example["mission_id"] != mission_governance["mission_id"]:
            codes.add("semantic_mission_id_mismatch")

        if parse_instant(example["created_at"]) > parse_instant(consent_scope["expires_at"]):
            if example["revocation_state"] != "expired" or example["policy_state"] not in {"blocked", "restricted"}:
                codes.add("semantic_expired_consent_not_allowed")

        if example.get("revocation_state") in {"revoked", "expired"} and example.get("policy_state") == "allowed":
            codes.add("schema_revoked_requires_blocked_or_restricted")

        upstream = [consent_scope["delegation"]["max_authority_band"], mission_governance["authority_band"]]
        receipt = example.get("transition_receipt_ref")
        if receipt:
            upstream.append(receipt.get("approval_band"))
        expected_authority = min_authority(upstream)
        if example["effective_authority_band"] != expected_authority:
            codes.add("semantic_effective_authority_not_glb")

        if example["source_field_decision"] != "allow":
            codes.add("semantic_source_field_decision_not_allow")
    except Exception:
        # Schema validation owns malformed-shape failures. Semantic checks should not mask them.
        pass
    return codes


def validate_twin_projection_feature_semantics(example: dict[str, Any]) -> None:
    codes = semantic_failure_codes(example)
    if codes:
        raise AssertionError(sorted(codes)[0])


def validate_one(example_name: str, schema_name: str) -> None:
    schema = load_json(SCHEMAS / schema_name)
    example = load_json(EXAMPLES / example_name)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(example)
    if schema_name == "twin-projection-feature.schema.json":
        validate_twin_projection_feature_semantics(example)


def validate_negative_fixture(fixture_name: str) -> None:
    schema = load_json(SCHEMAS / "twin-projection-feature.schema.json")
    base = load_json(EXAMPLES / "twin-projection-feature.example.json")
    fixture = load_json(NEG / fixture_name)
    mutated = apply_mutations(base, fixture["mutations"])
    expected = fixture["expected_failure"]

    failure_codes = {schema_failure_code(error) for error in Draft202012Validator(schema).iter_errors(mutated)}
    failure_codes |= semantic_failure_codes(mutated)

    if not failure_codes:
        raise AssertionError(f"negative fixture unexpectedly passed: {fixture_name}")
    if expected not in failure_codes:
        raise AssertionError(f"negative fixture {fixture_name} failed for {sorted(failure_codes)}, expected {expected}")
    print(f"rejected {fixture_name}: {expected}")


def main() -> int:
    missing = []
    for example_name, schema_name in EXAMPLE_TO_SCHEMA.items():
        if not (EXAMPLES / example_name).exists():
            missing.append(str(EXAMPLES / example_name))
        if not (SCHEMAS / schema_name).exists():
            missing.append(str(SCHEMAS / schema_name))
    for fixture_name in NEGATIVE_FIXTURES:
        if not (NEG / fixture_name).exists():
            missing.append(str(NEG / fixture_name))
    if missing:
        raise SystemExit("Missing Regis validation files:\n" + "\n".join(missing))

    for example_name, schema_name in EXAMPLE_TO_SCHEMA.items():
        validate_one(example_name, schema_name)
        print(f"validated {example_name} against {schema_name}")
    for fixture_name in NEGATIVE_FIXTURES:
        validate_negative_fixture(fixture_name)
    print("Regis example validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
