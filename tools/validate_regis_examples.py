#!/usr/bin/env python3
"""Lightweight validator for Regis Semantic Feature Plane examples."""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "schemas" / "regis"
EXAMPLES = ROOT / "examples" / "regis"

EXAMPLE_TO_SCHEMA = {
    "twin-projection-feature.example.json": "twin-projection-feature.schema.json",
    "embedding-card.example.json": "embedding-card.schema.json",
    "promotion-decision.evidence-only.example.json": "promotion-decision.schema.json"
}


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def validate_one(example_name: str, schema_name: str) -> None:
    schema = load_json(SCHEMAS / schema_name)
    example = load_json(EXAMPLES / example_name)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(example)


def main() -> int:
    missing = []
    for example_name, schema_name in EXAMPLE_TO_SCHEMA.items():
        if not (EXAMPLES / example_name).exists():
            missing.append(str(EXAMPLES / example_name))
        if not (SCHEMAS / schema_name).exists():
            missing.append(str(SCHEMAS / schema_name))
    if missing:
        raise SystemExit("Missing Regis validation files:\n" + "\n".join(missing))

    for example_name, schema_name in EXAMPLE_TO_SCHEMA.items():
        validate_one(example_name, schema_name)
        print(f"validated {example_name} against {schema_name}")
    print("Regis example validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
