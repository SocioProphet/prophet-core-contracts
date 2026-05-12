#!/usr/bin/env python3
"""Validate contract release manifest and downstream pin examples."""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "schemas"
EXAMPLES = ROOT / "examples" / "releases"

MANIFEST_SCHEMA = SCHEMAS / "release-manifest.schema.json"
PIN_SCHEMA = SCHEMAS / "pinned-prophet-core-contracts.schema.json"
MANIFEST_EXAMPLE = EXAMPLES / "manifest.contracts-v0.1.0-rc.1.example.json"
PIN_EXAMPLE = EXAMPLES / "pinned-prophet-core-contracts.example.json"


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> int:
    missing = [str(path) for path in [MANIFEST_SCHEMA, PIN_SCHEMA, MANIFEST_EXAMPLE, PIN_EXAMPLE] if not path.exists()]
    if missing:
        raise SystemExit("Missing release manifest validation files:\n" + "\n".join(missing))

    manifest_schema = load_json(MANIFEST_SCHEMA)
    pin_schema = load_json(PIN_SCHEMA)
    manifest = load_json(MANIFEST_EXAMPLE)
    pin = load_json(PIN_EXAMPLE)

    Draft202012Validator.check_schema(manifest_schema)
    Draft202012Validator.check_schema(pin_schema)
    Draft202012Validator(manifest_schema).validate(manifest)
    Draft202012Validator(pin_schema).validate(pin)

    if pin["release_tag"] != manifest["release_tag"]:
        raise AssertionError("pin release_tag must match manifest release_tag")
    if pin["release_commit"] != manifest["release_commit"]:
        raise AssertionError("pin release_commit must match manifest release_commit")

    manifest_contracts = {entry["name"] for entry in manifest["contracts_included"]}
    missing_contracts = set(pin["contracts_used"]) - manifest_contracts
    if missing_contracts:
        raise AssertionError(f"pin references contracts absent from manifest: {sorted(missing_contracts)}")

    manifest_schemas = {entry["path"] for entry in manifest["schemas"]}
    missing_schemas = set(pin["schema_paths"]) - manifest_schemas
    if missing_schemas:
        raise AssertionError(f"pin references schemas absent from manifest: {sorted(missing_schemas)}")

    manifest_validators = {entry["path"] for entry in manifest["validators"]}
    missing_validators = set(pin["validator_paths"]) - manifest_validators
    if missing_validators:
        raise AssertionError(f"pin references validators absent from manifest: {sorted(missing_validators)}")

    if manifest["release_status"] == "stable" and "-rc." in manifest["release_tag"]:
        raise AssertionError("stable releases must not use rc tag suffix")
    if manifest["release_status"] == "rc" and "-rc." not in manifest["release_tag"]:
        raise AssertionError("rc releases must use rc tag suffix")

    print("release manifest and downstream pin examples validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
