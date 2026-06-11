#!/usr/bin/env python3
"""Admission-chain integration validator skeleton.

Validates fixtures under tests/fixtures/integration/admission_chain/ against
the cross-contract invariants defined in docs/admission-chain-fixtures-v0.1.md.

Skeleton status: invariant bodies are placeholders. The validator is CI-safe:
it exits 0 with an explicit skip message when no integration fixtures exist.
"""

from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = ROOT / "tests" / "fixtures" / "integration" / "admission_chain"
NEGATIVE_DIR = FIXTURE_ROOT / "negative"

CONTRACT_FILES = {
    "policy_request": "01_policy_request.json",
    "policy_decision": "02_policy_decision.json",
    "admission_token": "03_admission_token.json",
    "effect": "04_effect.json",
    "audit_record": "05_audit_record.json",
}
PR11_REQUIRED = ("policy_request", "policy_decision", "admission_token", "effect")


@dataclass(frozen=True, slots=True)
class FixtureBundle:
    directory: Path
    policy_request: Mapping[str, Any] | None
    policy_decision: Mapping[str, Any] | None
    admission_token: Mapping[str, Any] | None
    effect: Mapping[str, Any] | None
    audit_record: Mapping[str, Any] | None
    expected_failure: str | None

    @property
    def name(self) -> str:
        return self.directory.name

    @property
    def is_positive(self) -> bool:
        return self.expected_failure is None


@dataclass(frozen=True, slots=True)
class InvariantResult:
    invariant_id: str
    invariant_number: int
    passed: bool
    detail: str | None = None


@dataclass(frozen=True, slots=True)
class FixtureResult:
    fixture: FixtureBundle
    invariant_results: tuple[InvariantResult, ...]

    @property
    def failure_codes(self) -> tuple[str, ...]:
        return tuple(result.invariant_id for result in self.invariant_results if not result.passed)

    @property
    def accepted(self) -> bool:
        return not self.failure_codes

    @property
    def matches_expectation(self) -> bool:
        if self.fixture.is_positive:
            return self.accepted
        # v0.1: expected code must appear. Additional failures are tolerated.
        # v0.2 may honor a _minimal.txt marker requiring exact failure sets.
        return self.fixture.expected_failure in self.failure_codes


def canonical_json(value: Any, *, contract: str) -> bytes:
    """Contract-specific canonicalization hook.

    PolicyRequest/PolicyDecision use rfc8785-jcs-v0.1. AdmissionToken,
    Effect, and AuditRecord use their own contract docs. PR #11 wires the
    concrete canonicalizers used by invariant checks.
    """
    raise NotImplementedError(f"canonicalization for {contract} not yet wired")


def sha256_prefixed(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _na(invariant_id: str, invariant_number: int) -> InvariantResult:
    return InvariantResult(invariant_id, invariant_number, True, "not applicable")


def _skeleton(invariant_id: str, invariant_number: int) -> InvariantResult:
    return InvariantResult(invariant_id, invariant_number, True, "skeleton: not yet implemented")


def _requires(bundle: FixtureBundle, *names: str) -> bool:
    return all(getattr(bundle, name) is not None for name in names)


def check_required_pr11_files(bundle: FixtureBundle) -> InvariantResult:
    missing = [name for name in PR11_REQUIRED if getattr(bundle, name) is None]
    if missing:
        return InvariantResult("fixture_missing_required_file", 0, False, ",".join(missing))
    return InvariantResult("fixture_missing_required_file", 0, True, None)


def check_policy_decision_input_hash(bundle: FixtureBundle) -> InvariantResult:
    iid = "policy_decision_input_hash_mismatch"
    return _skeleton(iid, 1) if _requires(bundle, "policy_request", "policy_decision") else _na(iid, 1)


def check_policy_decision_request_id(bundle: FixtureBundle) -> InvariantResult:
    iid = "policy_decision_request_id_mismatch"
    return _skeleton(iid, 2) if _requires(bundle, "policy_request", "policy_decision") else _na(iid, 2)


def check_admission_token_decision_id(bundle: FixtureBundle) -> InvariantResult:
    iid = "admission_token_decision_id_mismatch"
    return _skeleton(iid, 3) if _requires(bundle, "admission_token", "policy_decision") else _na(iid, 3)


def check_admission_token_request_id(bundle: FixtureBundle) -> InvariantResult:
    iid = "admission_token_request_id_mismatch"
    return _skeleton(iid, 4) if _requires(bundle, "admission_token", "policy_request") else _na(iid, 4)


def check_admission_token_risk_tier(bundle: FixtureBundle) -> InvariantResult:
    iid = "admission_token_risk_tier_mismatch"
    return _skeleton(iid, 5) if _requires(bundle, "admission_token", "policy_decision") else _na(iid, 5)


def check_admission_token_restrictions_superset(bundle: FixtureBundle) -> InvariantResult:
    iid = "admission_token_restrictions_not_superset"
    return _skeleton(iid, 6) if _requires(bundle, "admission_token", "policy_decision") else _na(iid, 6)


def check_admission_token_ttl(bundle: FixtureBundle) -> InvariantResult:
    iid = "admission_token_ttl_widening"
    return _skeleton(iid, 7) if _requires(bundle, "admission_token", "policy_decision") else _na(iid, 7)


def check_admission_token_action_granted(bundle: FixtureBundle) -> InvariantResult:
    iid = "admission_token_action_not_in_granted_actions"
    return _skeleton(iid, 8) if _requires(bundle, "admission_token", "policy_decision") else _na(iid, 8)


def check_effect_token_id(bundle: FixtureBundle) -> InvariantResult:
    iid = "effect_token_id_mismatch"
    return _skeleton(iid, 9) if _requires(bundle, "effect", "admission_token") else _na(iid, 9)


def check_effect_action_in_token(bundle: FixtureBundle) -> InvariantResult:
    iid = "effect_action_not_in_token"
    return _skeleton(iid, 10) if _requires(bundle, "effect", "admission_token") else _na(iid, 10)


def check_effect_resource_in_token(bundle: FixtureBundle) -> InvariantResult:
    iid = "effect_resource_not_in_token"
    return _skeleton(iid, 11) if _requires(bundle, "effect", "admission_token") else _na(iid, 11)


def check_effect_actor_binding(bundle: FixtureBundle) -> InvariantResult:
    iid = "effect_requesting_actor_mismatch"
    return _skeleton(iid, 12) if _requires(bundle, "effect", "admission_token") else _na(iid, 12)


def check_effect_subject_binding(bundle: FixtureBundle) -> InvariantResult:
    iid = "effect_subject_actor_mismatch"
    return _skeleton(iid, 13) if _requires(bundle, "effect", "admission_token") else _na(iid, 13)


def check_audit_request_ref(bundle: FixtureBundle) -> InvariantResult:
    iid = "audit_record_request_ref_id_mismatch"
    return _skeleton(iid, 14) if bundle.audit_record is not None else _na(iid, 14)


def check_audit_request_ref_version(bundle: FixtureBundle) -> InvariantResult:
    iid = "audit_record_request_ref_missing_schema_version"
    return _skeleton(iid, 15) if bundle.audit_record is not None else _na(iid, 15)


def check_audit_decision_ref(bundle: FixtureBundle) -> InvariantResult:
    iid = "audit_record_decision_ref_id_mismatch"
    return _skeleton(iid, 16) if bundle.audit_record is not None else _na(iid, 16)


def check_audit_token_ref(bundle: FixtureBundle) -> InvariantResult:
    iid = "audit_record_token_ref_id_mismatch"
    return _skeleton(iid, 17) if bundle.audit_record is not None else _na(iid, 17)


def check_audit_effect_ref(bundle: FixtureBundle) -> InvariantResult:
    iid = "audit_record_effect_ref_id_mismatch"
    return _skeleton(iid, 18) if bundle.audit_record is not None else _na(iid, 18)


def check_audit_verification_risk_tier(bundle: FixtureBundle) -> InvariantResult:
    iid = "audit_record_verification_risk_tier_drift"
    return _skeleton(iid, 19) if bundle.audit_record is not None else _na(iid, 19)


def check_audit_verification_restrictions(bundle: FixtureBundle) -> InvariantResult:
    iid = "audit_record_verification_restrictions_drift"
    return _skeleton(iid, 20) if bundle.audit_record is not None else _na(iid, 20)


def check_audit_outcome_consistency(bundle: FixtureBundle) -> InvariantResult:
    """Rejected admissions imply not_attempted; accepted admissions imply attempted outcomes."""
    iid = "audit_record_admission_execution_inconsistency"
    return _skeleton(iid, 21) if bundle.audit_record is not None else _na(iid, 21)


def check_audit_prior_hash_chain(bundle: FixtureBundle) -> InvariantResult:
    iid = "audit_record_prior_hash_mismatch"
    return _skeleton(iid, 23) if bundle.audit_record is not None else _na(iid, 23)


def check_audit_payload_hash(bundle: FixtureBundle) -> InvariantResult:
    iid = "audit_record_payload_hash_mismatch"
    return _skeleton(iid, 24) if bundle.audit_record is not None else _na(iid, 24)


INVARIANTS: tuple[Callable[[FixtureBundle], InvariantResult], ...] = (
    check_required_pr11_files,
    check_policy_decision_input_hash,
    check_policy_decision_request_id,
    check_admission_token_decision_id,
    check_admission_token_request_id,
    check_admission_token_risk_tier,
    check_admission_token_restrictions_superset,
    check_admission_token_ttl,
    check_admission_token_action_granted,
    check_effect_token_id,
    check_effect_action_in_token,
    check_effect_resource_in_token,
    check_effect_actor_binding,
    check_effect_subject_binding,
    check_audit_request_ref,
    check_audit_request_ref_version,
    check_audit_decision_ref,
    check_audit_token_ref,
    check_audit_effect_ref,
    check_audit_verification_risk_tier,
    check_audit_verification_restrictions,
    check_audit_outcome_consistency,
    check_audit_prior_hash_chain,
    check_audit_payload_hash,
)


def _load_json(directory: Path, filename: str) -> Mapping[str, Any] | None:
    path = directory / filename
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_fixture(directory: Path, expected_failure: str | None) -> FixtureBundle:
    return FixtureBundle(
        directory=directory,
        policy_request=_load_json(directory, CONTRACT_FILES["policy_request"]),
        policy_decision=_load_json(directory, CONTRACT_FILES["policy_decision"]),
        admission_token=_load_json(directory, CONTRACT_FILES["admission_token"]),
        effect=_load_json(directory, CONTRACT_FILES["effect"]),
        audit_record=_load_json(directory, CONTRACT_FILES["audit_record"]),
        expected_failure=expected_failure,
    )


def discover_positive_fixtures() -> list[FixtureBundle]:
    if not FIXTURE_ROOT.exists():
        return []
    return [load_fixture(child, None) for child in sorted(FIXTURE_ROOT.iterdir()) if child.is_dir() and child.name != "negative"]


def discover_negative_fixtures() -> list[FixtureBundle]:
    if not NEGATIVE_DIR.exists():
        return []
    fixtures: list[FixtureBundle] = []
    for child in sorted(NEGATIVE_DIR.iterdir()):
        if not child.is_dir():
            continue
        marker = child / "_expected_failure.txt"
        if not marker.exists():
            raise ValueError(f"negative fixture {child} missing _expected_failure.txt")
        expected = marker.read_text(encoding="utf-8").strip()
        if not expected:
            raise ValueError(f"negative fixture {child} has empty _expected_failure.txt")
        fixtures.append(load_fixture(child, expected))
    return fixtures


def validate_per_contract_schemas(bundle: FixtureBundle) -> tuple[InvariantResult, ...]:
    # TODO(PR #11): delegate to per-contract validators for files 1-4.
    # TODO(PR #12): add AuditRecord per-contract validation.
    return ()


def evaluate_fixture(bundle: FixtureBundle) -> FixtureResult:
    results = validate_per_contract_schemas(bundle) + tuple(invariant(bundle) for invariant in INVARIANTS)
    return FixtureResult(bundle, results)


def main(argv: Sequence[str]) -> int:
    if not FIXTURE_ROOT.exists():
        print(f"no integration fixtures found at {FIXTURE_ROOT}; skipping")
        return 0
    try:
        fixtures = discover_positive_fixtures() + discover_negative_fixtures()
    except ValueError as exc:
        print(f"validator setup error: {exc}", file=sys.stderr)
        return 2
    if not fixtures:
        print(f"no integration fixtures found under {FIXTURE_ROOT}; skipping")
        return 0

    failed = [result for result in (evaluate_fixture(fixture) for fixture in fixtures) if not result.matches_expectation]
    if failed:
        print(f"FAIL: {len(failed)} of {len(fixtures)} fixtures did not match expectation")
        for result in failed:
            print(f"  {result.fixture.name}:")
            print(f"    expected: {result.fixture.expected_failure or '(no failures)'}")
            print(f"    actual:   {list(result.failure_codes) or '(no failures)'}")
        return 1

    print(f"PASS: {len(fixtures)} fixtures matched expectations")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
