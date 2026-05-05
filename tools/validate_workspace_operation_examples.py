#!/usr/bin/env python3
"""Validate Workspace Operation Plane v0.1 examples.

This is intentionally lightweight: it validates core object references and
state-machine invariants without requiring third-party Python packages.
JSON Schema validation can be added later in sourceos-devtools.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples" / "workspace-operation"

TERMINAL_OPERATION_STATES = {"completed", "completed_with_warnings", "compensated"}
RETRYABLE_EVENT_TYPES = {"workspace.operation.task_failed"}


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def validate_operation(path: Path, data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    operation = data.get("operation")
    if not isinstance(operation, dict):
        return [f"{path}: missing operation object"]

    op_id = operation.get("operation_id")
    if not op_id:
        errors.append(f"{path}: operation.operation_id is required")

    if operation.get("schema_version") != "0.1.0":
        errors.append(f"{path}: operation.schema_version must be 0.1.0")

    if not operation.get("idempotency_key"):
        errors.append(f"{path}: operation.idempotency_key is required")

    task_ids = set(operation.get("task_ids", []))
    artifact_ids = set(operation.get("artifact_ids", []))
    decision_ids = set(operation.get("decision_ids", []))
    policy_gate_ids = set(operation.get("policy_gate_ids", []))

    for task in as_list(data.get("task")) + list(data.get("tasks", [])):
        if not isinstance(task, dict):
            continue
        if task.get("operation_id") != op_id:
            errors.append(f"{path}: task {task.get('task_id')} operation_id mismatch")
        if task.get("task_id") and task_ids and task.get("task_id") not in task_ids:
            errors.append(f"{path}: task {task.get('task_id')} not listed in operation.task_ids")
        if task.get("retryable") and not task.get("idempotency_key"):
            errors.append(f"{path}: retryable task {task.get('task_id')} lacks idempotency_key")
        if task.get("status") == "failed" and task.get("retryable") and not task.get("idempotency_key"):
            errors.append(f"{path}: failed retryable task {task.get('task_id')} lacks idempotency_key")

    for artifact in as_list(data.get("artifact")) + list(data.get("artifacts", [])):
        if not isinstance(artifact, dict):
            continue
        artifact_id = artifact.get("artifact_id")
        if artifact_id and artifact_ids and artifact_id not in artifact_ids:
            errors.append(f"{path}: artifact {artifact_id} not listed in operation.artifact_ids")
        if artifact.get("admission_state") == "activated" and artifact.get("activation_state") != "active":
            errors.append(f"{path}: artifact {artifact_id} admission_state activated but activation_state not active")
        if artifact.get("activation_state") == "active" and artifact.get("admission_state") not in {"admitted", "activated"}:
            errors.append(f"{path}: artifact {artifact_id} active before admission")

    for decision in as_list(data.get("decision")) + list(data.get("decisions", [])):
        if not isinstance(decision, dict):
            continue
        decision_id = decision.get("decision_id")
        if decision_id and decision_ids and decision_id not in decision_ids:
            errors.append(f"{path}: decision {decision_id} not listed in operation.decision_ids")
        if decision.get("status") == "pending" and not decision.get("options"):
            errors.append(f"{path}: pending decision {decision_id} has no options")

    for gate in as_list(data.get("policy_gate")) + list(data.get("policy_gates", [])):
        if not isinstance(gate, dict):
            continue
        gate_id = gate.get("gate_id")
        if gate_id and policy_gate_ids and gate_id not in policy_gate_ids:
            errors.append(f"{path}: policy gate {gate_id} not listed in operation.policy_gate_ids")
        if gate.get("status") in {"blocking", "requires_decision", "requires_admin"}:
            if not gate.get("responsible_actor"):
                errors.append(f"{path}: blocking gate {gate_id} lacks responsible_actor")
            if not gate.get("remediation_options"):
                errors.append(f"{path}: blocking gate {gate_id} lacks remediation_options")

    if operation.get("status") == "awaiting_decision" and not decision_ids:
        errors.append(f"{path}: awaiting_decision operation lacks decision_ids")

    if operation.get("status") == "blocked" and not policy_gate_ids:
        errors.append(f"{path}: blocked operation lacks policy_gate_ids")

    return errors


def main() -> int:
    if not EXAMPLES.exists():
        print(f"missing examples directory: {EXAMPLES}", file=sys.stderr)
        return 1

    errors: list[str] = []
    files = sorted(EXAMPLES.glob("*.json"))
    if not files:
        print(f"no example files found in {EXAMPLES}", file=sys.stderr)
        return 1

    for path in files:
        try:
            data = load_json(path)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{path}: failed to parse JSON: {exc}")
            continue
        errors.extend(validate_operation(path, data))

    if errors:
        print("Workspace Operation example validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"Validated {len(files)} Workspace Operation example(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
