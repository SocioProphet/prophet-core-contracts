#!/usr/bin/env python3
"""Validate value claim examples."""

import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schemas" / "value-claim.schema.json"
EXAMPLE = ROOT / "examples" / "prophet" / "value-claim-workspace-prophet.json"


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    try:
        schema = load_json(SCHEMA)
        example = load_json(EXAMPLE)
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(example)
    except Exception as exc:
        print(f"ERR: value claim validation failed: {exc}", file=sys.stderr)
        return 2

    errors = []
    if example.get("claim_type") != "value_claim":
        errors.append("claim_type must be value_claim")
    if example.get("production_ready") is not False:
        errors.append("production_ready must be false")
    if "production" in example.get("falsification_plan", {}).get("observation_window", ""):
        errors.append("fixture example must not claim production observation")
    kq = example.get("knowledge_quality", {})
    expected_k = round(kq.get("coverage", 0) * kq.get("coherence", 0) * kq.get("stability", 0) * kq.get("provenance", 0), 3)
    if round(kq.get("k", -1), 3) != expected_k:
        errors.append(f"knowledge_quality.k must equal rounded component product {expected_k}")
    if not example.get("evidence_ids"):
        errors.append("evidence_ids are required")
    if not example.get("kpi_mappings"):
        errors.append("kpi_mappings are required")

    if errors:
        print("ERR: value claim semantic checks failed", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 2

    print("Value claim example validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
