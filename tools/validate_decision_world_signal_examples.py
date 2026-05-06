#!/usr/bin/env python3
"""Validate decision-grade world signal examples.

This validator is intentionally lightweight and dependency-free. It checks the
contract-level invariants we care about before full JSON Schema validation is
moved into the conformance runner.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples" / "decision-world-signals"

PROMOTION_DECISIONS = {"REJECT", "REVIEW", "INSERT_EVIDENCE_ONLY", "PROMOTE_CANONICAL"}
CONCORDANCE_STATUSES = {"ACTIVE", "PENDING_REVIEW", "REJECTED", "SUPERSEDED"}
DECISION_TYPES = {
    "MATCH",
    "MERGE",
    "SPLIT",
    "ATTRIBUTE_SURVIVORSHIP",
    "FEATURE_PROMOTION",
    "ACTION_ADMISSION",
    "POLICY_BLOCK",
}
PROOF_STATUSES = {"PROVED", "VIOLATED", "UNKNOWN", "TIMEOUT", "PRECISION_LOSS_REVIEW_REQUIRED"}


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError("top-level JSON value must be an object")
    return data


def require(path: Path, data: dict[str, Any], field: str, errors: list[str]) -> Any:
    value = data.get(field)
    if value in (None, "", []):
        errors.append(f"{path}: missing required field {field}")
    return value


def validate_feature(path: Path, data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for field in ["feature_id", "feature_name", "category", "description", "coverage", "file_formats", "provenance_requirements"]:
        require(path, data, field, errors)
    if isinstance(data.get("file_formats"), list) and len(set(data["file_formats"])) != len(data["file_formats"]):
        errors.append(f"{path}: file_formats must be unique")
    if isinstance(data.get("provenance_requirements"), list) and len(set(data["provenance_requirements"])) != len(data["provenance_requirements"]):
        errors.append(f"{path}: provenance_requirements must be unique")
    return errors


def validate_energy(path: Path, data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = [
        "source_artifact_id",
        "extraction_run_id",
        "policy_id",
        "candidate_set_id",
        "top_entity_id",
        "top_score",
        "runnerup_entity_id",
        "runnerup_score",
        "margin_delta",
        "perturbation_flip_rate",
        "promotion_decision",
        "decision_reason_codes",
    ]
    for field in required:
        require(path, data, field, errors)
    if data.get("promotion_decision") not in PROMOTION_DECISIONS:
        errors.append(f"{path}: invalid promotion_decision {data.get('promotion_decision')!r}")
    flip_rate = data.get("perturbation_flip_rate")
    if isinstance(flip_rate, (int, float)) and not 0 <= flip_rate <= 1:
        errors.append(f"{path}: perturbation_flip_rate must be between 0 and 1")
    if isinstance(data.get("top_score"), (int, float)) and isinstance(data.get("runnerup_score"), (int, float)):
        expected = data["top_score"] - data["runnerup_score"]
        actual = data.get("margin_delta")
        if isinstance(actual, (int, float)) and abs(expected - actual) > 1e-9:
            errors.append(f"{path}: margin_delta must equal top_score - runnerup_score")
    if data.get("promotion_decision") == "PROMOTE_CANONICAL":
        margin = data.get("margin_delta")
        if isinstance(margin, (int, float)) and margin <= 0:
            errors.append(f"{path}: PROMOTE_CANONICAL requires positive margin_delta")
    return errors


def validate_concordance(path: Path, data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for field in ["source_system", "source_native_id", "source_record_id", "canonical_entity_id", "resolver_run_id", "policy_id", "confidence", "status", "decision_ledger_id"]:
        require(path, data, field, errors)
    confidence = data.get("confidence")
    if isinstance(confidence, (int, float)) and not 0 <= confidence <= 1:
        errors.append(f"{path}: confidence must be between 0 and 1")
    if data.get("status") not in CONCORDANCE_STATUSES:
        errors.append(f"{path}: invalid status {data.get('status')!r}")
    return errors


def validate_decision(path: Path, data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for field in ["decision_id", "decision_type", "policy_id", "input_artifact_hashes", "candidate_ids", "rule_trace", "confidence", "responsible_actor", "created_at", "replay_instructions"]:
        require(path, data, field, errors)
    if data.get("decision_type") not in DECISION_TYPES:
        errors.append(f"{path}: invalid decision_type {data.get('decision_type')!r}")
    confidence = data.get("confidence")
    if isinstance(confidence, (int, float)) and not 0 <= confidence <= 1:
        errors.append(f"{path}: confidence must be between 0 and 1")
    trace = data.get("rule_trace")
    if isinstance(trace, list):
        for idx, rule in enumerate(trace):
            if not isinstance(rule, dict) or not rule.get("rule_id") or not rule.get("outcome"):
                errors.append(f"{path}: rule_trace[{idx}] requires rule_id and outcome")
    return errors


def validate_proof(path: Path, data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for field in ["claim_name", "claim_version", "input_hashes", "analyzer", "analysis_domains", "budget", "precision_notes", "result_status", "replay_instructions"]:
        require(path, data, field, errors)
    if data.get("result_status") not in PROOF_STATUSES:
        errors.append(f"{path}: invalid result_status {data.get('result_status')!r}")
    if data.get("result_status") == "PROVED" and "witness" not in data:
        errors.append(f"{path}: PROVED result requires witness")
    if data.get("result_status") == "VIOLATED" and "violation_evidence" not in data:
        errors.append(f"{path}: VIOLATED result requires violation_evidence")
    analyzer = data.get("analyzer")
    if isinstance(analyzer, dict) and (not analyzer.get("name") or not analyzer.get("version")):
        errors.append(f"{path}: analyzer requires name and version")
    return errors


VALIDATORS = {
    "feature-registry-entry": validate_feature,
    "energy-ledger-entry": validate_energy,
    "concordance-link": validate_concordance,
    "decision-ledger-entry": validate_decision,
    "proof-artifact": validate_proof,
}


def infer_kind(path: Path) -> str | None:
    for kind in VALIDATORS:
        if path.name.startswith(kind):
            return kind
    return None


def main() -> int:
    if not EXAMPLES.exists():
        print(f"missing examples directory: {EXAMPLES}", file=sys.stderr)
        return 1

    files = sorted(EXAMPLES.glob("*.json"))
    if not files:
        print(f"no example files found in {EXAMPLES}", file=sys.stderr)
        return 1

    errors: list[str] = []
    seen_kinds: set[str] = set()
    for path in files:
        kind = infer_kind(path)
        if not kind:
            errors.append(f"{path}: filename does not identify a known decision-world-signal contract kind")
            continue
        seen_kinds.add(kind)
        try:
            data = load_json(path)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{path}: failed to parse JSON: {exc}")
            continue
        errors.extend(VALIDATORS[kind](path, data))

    missing = sorted(set(VALIDATORS) - seen_kinds)
    if missing:
        errors.append(f"missing example coverage for contract kinds: {', '.join(missing)}")

    if errors:
        print("Decision world signal example validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"Validated {len(files)} decision world signal example(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
