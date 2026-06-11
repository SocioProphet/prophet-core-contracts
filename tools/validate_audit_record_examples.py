#!/usr/bin/env python3
"""Validate AuditRecord v0.1 contract schema, positive examples, and negative fixtures."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "audit-record.schema.json"
EXAMPLES_DIR = ROOT / "examples" / "admission-chain"
NEGATIVE_DIR = EXAMPLES_DIR / "negative"

POSITIVE_STEMS = [
    "audit-record.genesis.accepted-executed",
    "audit-record.rejected-not-attempted",
    "audit-record.accepted-failed-effect",
    "audit-record.rollback",
    "audit-record.chained",
]


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def validate_chain_invariants(path: Path, record: dict) -> list[str]:
    errors = []
    if record.get("genesis_record") is True and record.get("hash_chain_prev") is not None:
        errors.append(f"{path.name}: genesis_record=true must not have hash_chain_prev")
    if record.get("genesis_record") is False and not record.get("hash_chain_prev"):
        errors.append(f"{path.name}: genesis_record=false requires hash_chain_prev")
    return errors


def validate_outcome_consistency(path: Path, record: dict) -> list[str]:
    errors = []
    if record.get("admission_outcome") == "rejected" and record.get("execution_outcome") == "executed":
        errors.append(f"{path.name}: rejected admission_outcome cannot have executed execution_outcome")
    return errors


def validate_rollback_ref(path: Path, record: dict) -> list[str]:
    errors = []
    if record.get("record_type") == "rollback_audit" and not record.get("prior_audit_record_ref"):
        errors.append(f"{path.name}: rollback_audit record must reference prior_audit_record_ref")
    return errors


def main() -> int:
    if not SCHEMA_PATH.exists():
        print(f"missing schema: {SCHEMA_PATH}", file=sys.stderr)
        return 1

    schema = load_json(SCHEMA_PATH)
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)

    errors = []

    # Positive examples
    for stem in POSITIVE_STEMS:
        path = EXAMPLES_DIR / f"{stem}.json"
        if not path.exists():
            errors.append(f"missing positive fixture: {path.name}")
            continue
        record = load_json(path)
        for err in validator.iter_errors(record):
            errors.append(f"{path.name}: schema: {err.message}")
        errors.extend(validate_chain_invariants(path, record))
        errors.extend(validate_outcome_consistency(path, record))
        errors.extend(validate_rollback_ref(path, record))

    # Negative fixtures — each must produce at least one validation error
    if NEGATIVE_DIR.exists():
        for path in sorted(NEGATIVE_DIR.glob("*.json")):
            record = load_json(path)
            schema_errors = list(validator.iter_errors(record))
            chain_errors = validate_chain_invariants(path, record)
            outcome_errors = validate_outcome_consistency(path, record)
            rollback_errors = validate_rollback_ref(path, record)
            all_violations = schema_errors + chain_errors + outcome_errors + rollback_errors
            if not all_violations:
                errors.append(f"{path.name}: negative fixture must fail validation but produced no errors")

    if errors:
        print("AuditRecord validation failed:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    n_pos = len(POSITIVE_STEMS)
    n_neg = len(list(NEGATIVE_DIR.glob("*.json"))) if NEGATIVE_DIR.exists() else 0
    print(f"AuditRecord v0.1 validation passed ({n_pos} positive, {n_neg} negative fixtures).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
