#!/usr/bin/env python3
"""Validate the scoped capability contract example."""

import json
from pathlib import Path
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "scoped-capability.schema.json"
EXAMPLE_PATH = ROOT / "examples" / "prophet" / "scoped-capability-local-command.json"

with SCHEMA_PATH.open("r", encoding="utf-8") as schema_file:
    schema = json.load(schema_file)
with EXAMPLE_PATH.open("r", encoding="utf-8") as example_file:
    example = json.load(example_file)

Draft202012Validator.check_schema(schema)
Draft202012Validator(schema).validate(example)
print("Scoped capability example validation passed")
