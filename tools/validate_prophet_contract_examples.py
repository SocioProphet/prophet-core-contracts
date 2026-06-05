#!/usr/bin/env python3
"""Validate PROPHET contract examples."""

import json
from pathlib import Path
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "schemas"
EXAMPLES = ROOT / "examples" / "prophet"

PAIRS = {
    "scoped-capability-local-command.json": "scoped-capability.schema.json",
    "action-receipt-completed.json": "action-receipt.schema.json",
    "claim-record-observation.json": "claim-record.schema.json",
    "evidence-thread-demo.json": "evidence-thread.schema.json"
}


def load(path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main():
    for example_name, schema_name in PAIRS.items():
        schema_path = SCHEMAS / schema_name
        example_path = EXAMPLES / example_name
        if not schema_path.exists():
            raise SystemExit(f"missing schema: {schema_path}")
        if not example_path.exists():
            raise SystemExit(f"missing example: {example_path}")
        schema = load(schema_path)
        example = load(example_path)
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(example)
        print(f"validated {example_name} against {schema_name}")
    print("PROPHET contract example validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
