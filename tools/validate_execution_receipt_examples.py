#!/usr/bin/env python3
"""Validate ExecutionReceipt fixtures for the governed Executions Ledger.

Two-sided by design: the valid fixtures must pass schema + semantic invariants,
and the invalid fixtures must FAIL at least one guard. If an invalid fixture ever
passes, this script exits non-zero -- a guard that can never fire is not a guard.
"""

import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "execution-receipt.schema.json"
VALID_DIR = ROOT / "examples" / "prophet"
INVALID_DIR = VALID_DIR / "invalid"

VALID_FILES = [
    "execution-receipt-verified.json",
    "execution-receipt-approval-required.json",
    "execution-receipt-denied.json",
]
# Each invalid fixture must fail at its INTENDED layer. "schema" fixtures must be
# rejected by JSON Schema; "semantic" fixtures must be schema-VALID yet rejected by
# a semantic invariant -- otherwise the semantic guard is never actually exercised.
INVALID_CASES = {
    "used-not-subset.json": "semantic",
    "verified-not-replayable.json": "semantic",
    "block-not-denied.json": "semantic",
    "bad-receipt-hash.json": "schema",
}


def load_json(path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def check_semantics(receipt, label):
    """Invariants the JSON Schema cannot express. Raise AssertionError on violation."""
    held = set(receipt.get("capabilities_held", []))
    used = set(receipt.get("capabilities_used", []))
    decision_verdict = receipt.get("decision", {}).get("verdict")
    state = receipt.get("verdict", {}).get("state")
    replayable = receipt.get("proof_artifact", {}).get("replayable")

    # INV1: what an agent used must be a subset of what it was granted.
    extra = used - held
    if extra:
        raise AssertionError(f"{label}: capabilities_used not subset of capabilities_held: {sorted(extra)}")

    # INV2: a verified verdict must be backed by a replayable artifact (verify the artifact, not the command).
    if state == "verified" and replayable is not True:
        raise AssertionError(f"{label}: verdict.state=verified requires proof_artifact.replayable=true")

    # INV3: a blocked execution yields a denied verdict, and vice versa.
    if (decision_verdict == "block") != (state == "denied"):
        raise AssertionError(f"{label}: decision.verdict=block iff verdict.state=denied (got {decision_verdict!r}/{state!r})")

    # INV4: an execution awaiting approval is pending.
    if decision_verdict == "require_approval" and state != "pending":
        raise AssertionError(f"{label}: decision.verdict=require_approval requires verdict.state=pending (got {state!r})")


def check(validator, receipt, label):
    """Full gate: schema + semantics. Raises on any failure."""
    validator.validate(receipt)
    check_semantics(receipt, label)


def main():
    schema = load_json(SCHEMA_PATH)
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)

    for name in VALID_FILES:
        receipt = load_json(VALID_DIR / name)
        check(validator, receipt, name)

    # Teeth check: every invalid fixture MUST be rejected at its INTENDED layer.
    # Rejection for the wrong reason (e.g. a stray schema error masking a semantic
    # guard) is treated as a leak -- a guard you cannot prove fired is not a guard.
    problems = []
    for name, layer in INVALID_CASES.items():
        receipt = load_json(INVALID_DIR / name)
        schema_errors = list(validator.iter_errors(receipt))
        if layer == "schema":
            if not schema_errors:
                problems.append(f"{name}: expected a SCHEMA rejection, but schema accepted it")
            continue
        # layer == "semantic": must be schema-valid, then fail a semantic invariant.
        if schema_errors:
            problems.append(
                f"{name}: expected a SEMANTIC rejection but it failed SCHEMA first "
                f"({schema_errors[0].message}) -- the semantic guard was never exercised"
            )
            continue
        try:
            check_semantics(receipt, name)
        except AssertionError:
            continue  # good: the semantic guard fired on a schema-valid fixture
        problems.append(f"{name}: expected a SEMANTIC rejection, but all invariants passed")

    if problems:
        raise SystemExit("ExecutionReceipt teeth check failed:\n  - " + "\n  - ".join(problems))

    print(
        f"ExecutionReceipt validation passed "
        f"({len(VALID_FILES)} valid accepted, {len(INVALID_CASES)} invalid rejected at intended layer)"
    )


if __name__ == "__main__":
    main()
