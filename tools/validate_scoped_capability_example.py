#!/usr/bin/env python3
"""Validate scoped capability and E2E membrane fixtures."""

import json
from datetime import datetime, timezone
from pathlib import Path
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "scoped-capability.schema.json"
EXAMPLE_PATH = ROOT / "examples" / "prophet" / "scoped-capability-local-command.json"
E2E_DIR = ROOT / "examples" / "e2e"
E2E_FILES = [
    "workspace-operation-with-scoped-capability.json",
    "workspace-operation-blocked-missing-capability.json",
    "workspace-operation-expired-capability.json",
]
NOW = datetime(2026, 6, 4, 0, 0, 0, tzinfo=timezone.utc)


def load_json(path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def parse_time(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def validate_capability_schema(schema, capability, label):
    Draft202012Validator(schema).validate(capability)
    if not capability.get("fail_closed"):
        raise AssertionError(f"{label}: scoped capability must fail closed")
    binding = capability.get("workspace_operation_binding", {})
    if binding.get("required") is not True:
        raise AssertionError(f"{label}: workspace operation binding is required")


def validate_happy_path(schema, fixture):
    capability = fixture["scoped_capability"]
    operation = fixture["operation"]
    validate_capability_schema(schema, capability, fixture["scenario_id"])
    binding = capability["workspace_operation_binding"]
    if binding.get("operation_id") != operation.get("operation_id"):
        raise AssertionError("happy path: capability operation_id must match operation")
    if binding.get("operation_type") != operation.get("operation_type"):
        raise AssertionError("happy path: capability operation_type must match operation")
    if operation.get("capability_profile_id") != capability.get("capability_id"):
        raise AssertionError("happy path: operation capability_profile_id must match capability_id")
    actor = operation.get("actor", {})
    subject = capability.get("subject", {})
    if actor.get("actor_id") != subject.get("actor_id") or actor.get("actor_type") != subject.get("actor_type"):
        raise AssertionError("happy path: operation actor must match capability subject")
    if "export_diagnostics" not in capability.get("verbs", []):
        raise AssertionError("happy path: capability must include export_diagnostics verb")
    if not (parse_time(capability["valid_from"]) <= NOW <= parse_time(capability["expires_at"])):
        raise AssertionError("happy path: capability must be valid at fixture NOW")
    if fixture.get("expected_result") != "allowed":
        raise AssertionError("happy path: expected_result must be allowed")


def validate_missing_capability(fixture):
    operation = fixture["operation"]
    if "scoped_capability" in fixture:
        raise AssertionError("missing capability fixture must not include scoped_capability")
    if operation.get("status") != "blocked":
        raise AssertionError("missing capability operation must be blocked")
    if operation.get("capability_profile_id"):
        raise AssertionError("missing capability operation must not reference capability_profile_id")
    gate = fixture.get("policy_gate", {})
    if gate.get("decision") != "block":
        raise AssertionError("missing capability gate must block")
    if "missing_scoped_capability" not in gate.get("reason_codes", []):
        raise AssertionError("missing capability reason code is required")


def validate_expired_capability(schema, fixture):
    capability = fixture["scoped_capability"]
    operation = fixture["operation"]
    validate_capability_schema(schema, capability, fixture["scenario_id"])
    if operation.get("status") != "blocked":
        raise AssertionError("expired capability operation must be blocked")
    if parse_time(capability["expires_at"]) >= NOW:
        raise AssertionError("expired capability fixture must expire before fixture NOW")
    gate = fixture.get("policy_gate", {})
    if gate.get("decision") != "block":
        raise AssertionError("expired capability gate must block")
    if "expired_scoped_capability" not in gate.get("reason_codes", []):
        raise AssertionError("expired capability reason code is required")


schema = load_json(SCHEMA_PATH)
Draft202012Validator.check_schema(schema)
example = load_json(EXAMPLE_PATH)
validate_capability_schema(schema, example, "standalone example")

for name in E2E_FILES:
    path = E2E_DIR / name
    fixture = load_json(path)
    if name == "workspace-operation-with-scoped-capability.json":
        validate_happy_path(schema, fixture)
    elif name == "workspace-operation-blocked-missing-capability.json":
        validate_missing_capability(fixture)
    elif name == "workspace-operation-expired-capability.json":
        validate_expired_capability(schema, fixture)

print("Scoped capability and E2E membrane fixture validation passed")
