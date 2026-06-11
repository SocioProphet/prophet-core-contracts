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


_RESTRICTION_MAP: dict[str, str] = {
    "DoNotLearn": "do_not_learn",
    "DoNotLink": "do_not_link",
    "NoRawTwinExport": "no_raw_twin_export",
}


def check_policy_decision_input_hash(bundle: FixtureBundle) -> InvariantResult:
    iid = "policy_decision_input_hash_mismatch"
    if not _requires(bundle, "policy_request", "policy_decision"):
        return _na(iid, 1)
    expected = bundle.policy_decision.get("policy_request_ref", {}).get("request_hash")
    actual = bundle.policy_decision.get("input_hash")
    if expected and actual and expected != actual:
        return InvariantResult(iid, 1, False, f"input_hash {actual!r} != policy_request_ref.request_hash {expected!r}")
    return InvariantResult(iid, 1, True, None)


def check_policy_decision_request_id(bundle: FixtureBundle) -> InvariantResult:
    iid = "policy_decision_request_id_mismatch"
    if not _requires(bundle, "policy_request", "policy_decision"):
        return _na(iid, 2)
    pr_id = bundle.policy_request.get("request_id")
    pd_ref_id = bundle.policy_decision.get("policy_request_ref", {}).get("request_id")
    if pr_id and pd_ref_id and pr_id != pd_ref_id:
        return InvariantResult(iid, 2, False, f"policy_decision.policy_request_ref.request_id {pd_ref_id!r} != policy_request.request_id {pr_id!r}")
    return InvariantResult(iid, 2, True, None)


def check_admission_token_decision_id(bundle: FixtureBundle) -> InvariantResult:
    iid = "admission_token_decision_id_mismatch"
    if not _requires(bundle, "admission_token", "policy_decision"):
        return _na(iid, 3)
    pd_id = bundle.policy_decision.get("decision_id")
    at_ref_id = bundle.admission_token.get("policy_decision_ref", {}).get("decision_id")
    if pd_id and at_ref_id and pd_id != at_ref_id:
        return InvariantResult(iid, 3, False, f"admission_token.policy_decision_ref.decision_id {at_ref_id!r} != policy_decision.decision_id {pd_id!r}")
    return InvariantResult(iid, 3, True, None)


def check_admission_token_request_id(bundle: FixtureBundle) -> InvariantResult:
    iid = "admission_token_request_id_mismatch"
    if not _requires(bundle, "admission_token", "policy_request"):
        return _na(iid, 4)
    action_id = bundle.admission_token.get("proposed_action_ref", {}).get("action_id")
    pr_action_ids = {a.get("action_id") for a in bundle.policy_request.get("requested_actions", [])}
    if action_id and pr_action_ids and action_id not in pr_action_ids:
        return InvariantResult(iid, 4, False, f"admission_token.proposed_action_ref.action_id {action_id!r} not in policy_request.requested_actions")
    return InvariantResult(iid, 4, True, None)


def check_admission_token_risk_tier(bundle: FixtureBundle) -> InvariantResult:
    iid = "admission_token_risk_tier_mismatch"
    return _skeleton(iid, 5) if _requires(bundle, "admission_token", "policy_decision") else _na(iid, 5)


def check_admission_token_restrictions_superset(bundle: FixtureBundle) -> InvariantResult:
    iid = "admission_token_restrictions_not_superset"
    if not _requires(bundle, "admission_token", "policy_decision"):
        return _na(iid, 6)
    pd_restrictions = bundle.policy_decision.get("restrictions", [])
    sink = bundle.admission_token.get("sink_restrictions", {})
    missing = [r for r in pd_restrictions if not sink.get(_RESTRICTION_MAP.get(r, ""), False)]
    if missing:
        return InvariantResult(iid, 6, False, f"policy_decision restrictions not in token.sink_restrictions: {missing}")
    return InvariantResult(iid, 6, True, None)


def check_admission_token_ttl(bundle: FixtureBundle) -> InvariantResult:
    iid = "admission_token_ttl_widening"
    if not _requires(bundle, "admission_token", "policy_decision"):
        return _na(iid, 7)
    expires_at = bundle.admission_token.get("expires_at")
    valid_until = bundle.policy_decision.get("decision_valid_until")
    if expires_at and valid_until and expires_at > valid_until:
        return InvariantResult(iid, 7, False, f"token.expires_at {expires_at!r} > decision.decision_valid_until {valid_until!r}")
    return InvariantResult(iid, 7, True, None)


def check_admission_token_action_granted(bundle: FixtureBundle) -> InvariantResult:
    iid = "admission_token_action_not_in_granted_actions"
    if not _requires(bundle, "admission_token", "policy_decision"):
        return _na(iid, 8)
    op = bundle.admission_token.get("allowed_operation", {})
    op_type = op.get("operation_type")
    op_resource = op.get("resource_ref")
    granted = bundle.policy_decision.get("granted_actions", [])
    match = any(g.get("action_type") == op_type and g.get("resource_ref") == op_resource for g in granted)
    if op_type and op_resource and not match:
        return InvariantResult(iid, 8, False, f"token.allowed_operation ({op_type!r}, {op_resource!r}) not in policy_decision.granted_actions")
    return InvariantResult(iid, 8, True, None)


def check_effect_token_id(bundle: FixtureBundle) -> InvariantResult:
    iid = "effect_token_id_mismatch"
    if not _requires(bundle, "effect", "admission_token"):
        return _na(iid, 9)
    token_id = bundle.admission_token.get("token_id")
    eff_token_id = bundle.effect.get("admission_token_id")
    if token_id and eff_token_id and token_id != eff_token_id:
        return InvariantResult(iid, 9, False, f"effect.admission_token_id {eff_token_id!r} != admission_token.token_id {token_id!r}")
    return InvariantResult(iid, 9, True, None)


def check_effect_action_in_token(bundle: FixtureBundle) -> InvariantResult:
    iid = "effect_action_not_in_token"
    if not _requires(bundle, "effect", "admission_token"):
        return _na(iid, 10)
    allowed_type = bundle.admission_token.get("allowed_operation", {}).get("operation_type")
    eff_type = bundle.effect.get("action_type")
    if allowed_type and eff_type and eff_type != allowed_type:
        return InvariantResult(iid, 10, False, f"effect.action_type {eff_type!r} != token.allowed_operation.operation_type {allowed_type!r}")
    return InvariantResult(iid, 10, True, None)


def check_effect_resource_in_token(bundle: FixtureBundle) -> InvariantResult:
    iid = "effect_resource_not_in_token"
    if not _requires(bundle, "effect", "admission_token"):
        return _na(iid, 11)
    allowed_resource = bundle.admission_token.get("allowed_operation", {}).get("resource_ref")
    eff_resource = bundle.effect.get("resource_ref")
    if allowed_resource and eff_resource and eff_resource != allowed_resource:
        return InvariantResult(iid, 11, False, f"effect.resource_ref {eff_resource!r} != token.allowed_operation.resource_ref {allowed_resource!r}")
    return InvariantResult(iid, 11, True, None)


def check_effect_actor_binding(bundle: FixtureBundle) -> InvariantResult:
    iid = "effect_requesting_actor_mismatch"
    if not _requires(bundle, "effect", "admission_token"):
        return _na(iid, 12)
    token_actor = bundle.admission_token.get("authority_decision_ref", {}).get("actor_id")
    eff_actor = bundle.effect.get("requesting_actor_id")
    if token_actor and eff_actor and eff_actor != token_actor:
        return InvariantResult(iid, 12, False, f"effect.requesting_actor_id {eff_actor!r} != token.authority_decision_ref.actor_id {token_actor!r}")
    return InvariantResult(iid, 12, True, None)


def check_effect_subject_binding(bundle: FixtureBundle) -> InvariantResult:
    iid = "effect_subject_actor_mismatch"
    if not _requires(bundle, "effect", "admission_token"):
        return _na(iid, 13)
    token_subject = bundle.admission_token.get("authority_decision_ref", {}).get("subject_id")
    eff_subject = bundle.effect.get("subject_actor_id")
    if token_subject and eff_subject and eff_subject != token_subject:
        return InvariantResult(iid, 13, False, f"effect.subject_actor_id {eff_subject!r} != token.authority_decision_ref.subject_id {token_subject!r}")
    return InvariantResult(iid, 13, True, None)


def check_audit_request_ref(bundle: FixtureBundle) -> InvariantResult:
    iid = "audit_record_request_ref_id_mismatch"
    if bundle.audit_record is None or bundle.policy_request is None:
        return _na(iid, 14)
    ar_id = bundle.audit_record.get("policy_request_ref", {}).get("request_id")
    pr_id = bundle.policy_request.get("request_id")
    if ar_id and pr_id and ar_id != pr_id:
        return InvariantResult(iid, 14, False, f"audit_record.policy_request_ref.request_id {ar_id!r} != policy_request.request_id {pr_id!r}")
    return InvariantResult(iid, 14, True, None)


def check_audit_request_ref_version(bundle: FixtureBundle) -> InvariantResult:
    iid = "audit_record_request_ref_missing_schema_version"
    if bundle.audit_record is None:
        return _na(iid, 15)
    ref = bundle.audit_record.get("policy_request_ref", {})
    if ref and "schema_version" not in ref:
        return InvariantResult(iid, 15, False, "audit_record.policy_request_ref missing schema_version")
    return InvariantResult(iid, 15, True, None)


def check_audit_decision_ref(bundle: FixtureBundle) -> InvariantResult:
    iid = "audit_record_decision_ref_id_mismatch"
    if bundle.audit_record is None or bundle.policy_decision is None:
        return _na(iid, 16)
    ar_id = bundle.audit_record.get("policy_decision_ref", {}).get("decision_id")
    pd_id = bundle.policy_decision.get("decision_id")
    if ar_id and pd_id and ar_id != pd_id:
        return InvariantResult(iid, 16, False, f"audit_record.policy_decision_ref.decision_id {ar_id!r} != policy_decision.decision_id {pd_id!r}")
    return InvariantResult(iid, 16, True, None)


def check_audit_token_ref(bundle: FixtureBundle) -> InvariantResult:
    iid = "audit_record_token_ref_id_mismatch"
    if bundle.audit_record is None or bundle.admission_token is None:
        return _na(iid, 17)
    ar_id = bundle.audit_record.get("admission_token_ref", {}).get("token_id")
    at_id = bundle.admission_token.get("token_id")
    if ar_id and at_id and ar_id != at_id:
        return InvariantResult(iid, 17, False, f"audit_record.admission_token_ref.token_id {ar_id!r} != admission_token.token_id {at_id!r}")
    return InvariantResult(iid, 17, True, None)


def check_audit_effect_ref(bundle: FixtureBundle) -> InvariantResult:
    iid = "audit_record_effect_ref_id_mismatch"
    if bundle.audit_record is None or bundle.effect is None:
        return _na(iid, 18)
    ar_id = bundle.audit_record.get("effect_ref", {}).get("effect_id")
    eff_id = bundle.effect.get("effect_id")
    if ar_id and eff_id and ar_id != eff_id:
        return InvariantResult(iid, 18, False, f"audit_record.effect_ref.effect_id {ar_id!r} != effect.effect_id {eff_id!r}")
    return InvariantResult(iid, 18, True, None)


def check_audit_verification_risk_tier(bundle: FixtureBundle) -> InvariantResult:
    iid = "audit_record_verification_risk_tier_drift"
    return _skeleton(iid, 19) if bundle.audit_record is not None else _na(iid, 19)


def check_audit_verification_restrictions(bundle: FixtureBundle) -> InvariantResult:
    iid = "audit_record_verification_restrictions_drift"
    return _skeleton(iid, 20) if bundle.audit_record is not None else _na(iid, 20)


def check_audit_outcome_consistency(bundle: FixtureBundle) -> InvariantResult:
    """Rejected admissions may not produce executed or partial outcomes."""
    iid = "audit_record_admission_execution_inconsistency"
    if bundle.audit_record is None:
        return _na(iid, 21)
    admission = bundle.audit_record.get("admission_outcome")
    execution = bundle.audit_record.get("execution_outcome")
    if admission == "rejected" and execution in ("executed", "partial"):
        return InvariantResult(iid, 21, False, f"admission_outcome=rejected but execution_outcome={execution!r}")
    return InvariantResult(iid, 21, True, None)


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
