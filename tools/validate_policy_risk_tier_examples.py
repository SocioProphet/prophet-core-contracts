#!/usr/bin/env python3
"""Validate PolicyDecision risk_tier v0.1 coverage."""

from __future__ import annotations

import copy
import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schemas" / "policy-decision.schema.json"
EXAMPLES = ROOT / "examples" / "policy"
NEG = EXAMPLES / "negative"

DECISION_EXAMPLES = [
    "policy-decision.allow-with-constraints.example.json",
    "policy-decision.allow.example.json",
    "policy-decision.deny.example.json",
    "policy-decision.require-review.example.json",
    "policy-decision.quarantine.example.json",
    "policy-decision.revoke.example.json",
]


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def pointer_tokens(path: str) -> list[str]:
    return [token.replace("~1", "/").replace("~0", "~") for token in path[1:].split("/")]


def resolve_parent(document, path: str):
    tokens = pointer_tokens(path)
    parent = document
    for token in tokens[:-1]:
        parent = parent[int(token)] if isinstance(parent, list) else parent[token]
    return parent, tokens[-1]


def apply_mutation(document, mutation):
    mutated = copy.deepcopy(document)
    parent, token = resolve_parent(mutated, mutation["path"])
    if mutation["op"] == "remove":
        del parent[token]
    else:
        raise AssertionError(f"unsupported mutation op: {mutation['op']}")
    return mutated


def failure_code(error) -> str:
    if error.validator == "required":
        missing = str(error.message).split("'")[1]
        return f"schema_required_{missing}"
    return f"schema_{error.validator}"


def main() -> int:
    schema = load_json(SCHEMA)
    validator = Draft202012Validator(schema)

    for example_name in DECISION_EXAMPLES:
        decision = load_json(EXAMPLES / example_name)
        if decision.get("risk_tier") not in {"low", "medium", "high", "critical"}:
            raise AssertionError(f"{example_name}: invalid or missing risk_tier")
        validator.validate(decision)
        print(f"risk_tier present in {example_name}: {decision['risk_tier']}")

    fixture = load_json(NEG / "policy-decision.missing-risk-tier.invalid.json")
    base = load_json(EXAMPLES / fixture.get("base_example", "policy-decision.allow-with-constraints.example.json"))
    mutated = apply_mutation(base, fixture["mutation"])
    codes = {failure_code(error) for error in validator.iter_errors(mutated)}
    expected = fixture["expected_failure"]
    if expected not in codes:
        raise AssertionError(f"missing risk_tier fixture failed for {sorted(codes)}, expected {expected}")
    print(f"rejected policy-decision.missing-risk-tier.invalid.json: {expected}")
    print("PolicyDecision risk_tier validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
