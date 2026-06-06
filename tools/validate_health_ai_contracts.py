#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
CASES = [
    ("schemas/health-eval-rubric.schema.json", "examples/health-ai/health-eval-rubric.planning.example.json"),
    ("schemas/clinical-value-claim.schema.json", "examples/health-ai/clinical-value-claim.ambience-source.example.json"),
]

FORBIDDEN_STRINGS = [
    "healthbench:",
]

def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))

def main() -> int:
    errors: list[str] = []

    for schema_rel, example_rel in CASES:
        schema_path = ROOT / schema_rel
        example_path = ROOT / example_rel
        try:
            schema = load_json(schema_path)
            example = load_json(example_path)
            Draft202012Validator.check_schema(schema)
            Draft202012Validator(schema).validate(example)
        except Exception as exc:
            errors.append(f"{example_rel} failed schema validation: {exc}")
            continue

        text = example_path.read_text(encoding="utf-8")
        for forbidden in FORBIDDEN_STRINGS:
            if forbidden in text:
                errors.append(f"{example_rel} contains forbidden benchmark leakage marker")

        if example.get("production_ready") is not False:
            errors.append(f"{example_rel}: production_ready must be false")
        if example.get("patient_care_action") is not False:
            errors.append(f"{example_rel}: patient_care_action must be false")

        if example_rel.endswith("clinical-value-claim.ambience-source.example.json"):
            if example.get("source_class") != "external_competitor_claim":
                errors.append("Ambience-derived claim must remain external_competitor_claim")
            if example.get("customer_facing_claim") is not False:
                errors.append("customer_facing_claim must be false")
            for metric in example.get("metric_claims", []):
                if metric.get("validated_by_socioprophet") is not False:
                    errors.append("metric claims must not be SocioProphet validated")

        if example_rel.endswith("health-eval-rubric.planning.example.json"):
            boundary = example.get("benchmark_boundary", {})
            for key in ("protected_examples_reproduced", "answer_keys_reproduced", "canary_reproduced"):
                if boundary.get(key) is not False:
                    errors.append(f"{key} must be false")

    if errors:
        print("ERR: health AI contract validation failed", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 2

    print("Health AI contract examples validate.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
