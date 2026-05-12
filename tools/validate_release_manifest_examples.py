#!/usr/bin/env python3
"""Validate contract release manifest and downstream pin examples."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "schemas"
EXAMPLES = ROOT / "examples" / "releases"

MANIFEST_SCHEMA = SCHEMAS / "release-manifest.schema.json"
PIN_SCHEMA = SCHEMAS / "pinned-prophet-core-contracts.schema.json"
MANIFEST_EXAMPLE = EXAMPLES / "contracts-v0.1.0-rc.1" / "manifest.example.json"
PIN_EXAMPLE = EXAMPLES / "pinned-prophet-core-contracts.example.json"


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def canonical_json(value) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_prefixed(value: str | bytes) -> str:
    data = value if isinstance(value, bytes) else value.encode("utf-8")
    return "sha256:" + hashlib.sha256(data).hexdigest()


def manifest_self_hash(manifest: dict) -> str:
    material = copy.deepcopy(manifest)
    material.pop("manifest_sha256", None)
    return sha256_prefixed(canonical_json(material))


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

    expected_manifest_hash = manifest_self_hash(manifest)
    if manifest["manifest_sha256"] != expected_manifest_hash:
        raise AssertionError(f"manifest_sha256 mismatch: expected {expected_manifest_hash}, got {manifest['manifest_sha256']}")
    if pin["manifest_sha256"] != manifest["manifest_sha256"]:
        raise AssertionError("pin manifest_sha256 must match manifest manifest_sha256")
    if pin["manifest_path"] != manifest["manifest_path"]:
        raise AssertionError("pin manifest_path must match manifest manifest_path")
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
    if manifest["signature"]["status"] == "unsigned_v0_1" and manifest["signature"]["algorithm"] != "none":
        raise AssertionError("unsigned_v0_1 manifests must use signature algorithm 'none'")

    print("release manifest and downstream pin examples validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
