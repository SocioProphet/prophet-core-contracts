#!/usr/bin/env python3
"""Validate PROPHET receipt, claim, and evidence examples."""

import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
CASES = [
    ("schemas/action-receipt.schema.json", "examples/prophet/action-receipt-completed.json"),
    ("schemas/claim-record.schema.json", "examples/prophet/claim-record-observation.json"),
    ("schemas/evidence-thread.schema.json", "examples/prophet/evidence-thread-workspace-operation.json"),
]


def load_json(path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main():
    for schema_rel, example_rel in CASES:
        schema_path = ROOT / schema_rel
        example_path = ROOT / example_rel
        schema = load_json(schema_path)
        example = load_json(example_path)
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(example)
        print(f"validated {example_rel} against {schema_rel}")
    print("PROPHET record example validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
