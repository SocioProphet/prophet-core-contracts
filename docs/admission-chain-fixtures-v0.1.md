# Admission Chain Integration Fixtures v0.1

Status: read-ahead specification for PR #11 and PR #12.

This document defines the v0.1 fixture plan for the admission spine:

```text
PolicyRequest -> PolicyDecision -> AdmissionToken -> Effect -> AuditRecord
```

It is the versioned companion to `prophet-core-contracts#12`.

## Locked decisions

1. `Effect` is included as a minimal v0.1 stub, not deferred to v0.2.
2. The integration validator lives at `tools/validate_admission_chain_examples.py`.
3. `make validate` runs integration by default through `validate-integration`.
4. Failure codes are stable string identifiers. Invariant numbers are descriptive only.
5. v0.1 keeps flat failure codes; scoped codes may be introduced in v0.2 if needed.

## Fixture root

```text
tests/fixtures/integration/admission_chain/
```

Final canonical happy path shape:

```text
canonical_happy_path/
  01_policy_request.json
  02_policy_decision.json
  03_admission_token.json
  04_effect.json
  05_audit_record.json
```

PR #11 lands files 1-4 for AdmissionToken/Effect binding. PR #12 adds `05_audit_record.json` and audit-specific fixtures.

## PR #11 fixture scope

Positive fixtures:

- `canonical_happy_path/` with files 1-4.
- `allow_with_constraints/` with files 1-4 and restrictions carried forward.

Negative fixtures:

- `decision_request_hash_mismatch` -> `policy_decision_input_hash_mismatch`
- `decision_request_id_mismatch` -> `policy_decision_request_id_mismatch`
- `token_decision_id_mismatch` -> `admission_token_decision_id_mismatch`
- `token_request_id_mismatch` -> `admission_token_request_id_mismatch`
- `token_risk_tier_mismatch` -> `admission_token_risk_tier_mismatch`
- `token_restrictions_weakened` -> `admission_token_restrictions_not_superset`
- `token_expires_after_decision` -> `admission_token_ttl_widening`
- `token_action_not_granted` -> `admission_token_action_not_in_granted_actions`
- `effect_token_id_mismatch` -> `effect_token_id_mismatch`
- `effect_action_widens_token` -> `effect_action_not_in_token`
- `effect_resource_widens_token` -> `effect_resource_not_in_token`
- `effect_actor_mismatch` -> `effect_requesting_actor_mismatch`
- `effect_subject_mismatch` -> `effect_subject_actor_mismatch`

## PR #12 fixture scope

Positive fixtures:

- `canonical_happy_path/` with all five files.
- `genesis_record/`
- `chained_record/`
- `rejected_at_admission/`
- `failed_execution/`
- `rollback_chain/`
- `revocation_deferred/`

Negative fixtures:

- `audit_request_ref_mismatch` -> `audit_record_request_ref_id_mismatch`
- `audit_request_ref_missing_version` -> `audit_record_request_ref_missing_schema_version`
- `audit_decision_ref_mismatch` -> `audit_record_decision_ref_id_mismatch`
- `audit_token_ref_mismatch` -> `audit_record_token_ref_id_mismatch`
- `audit_effect_ref_mismatch` -> `audit_record_effect_ref_id_mismatch`
- `audit_verification_risk_tier_drift` -> `audit_record_verification_risk_tier_drift`
- `audit_verification_restrictions_drift` -> `audit_record_verification_restrictions_drift`
- `audit_rejected_with_executed` -> `audit_record_rejected_but_execution_attempted`
- `audit_accepted_with_not_attempted` -> `audit_record_accepted_but_not_attempted`
- `audit_rollback_missing_prior` -> `audit_record_rollback_missing_target_ref`
- `audit_genesis_with_prior_hash` -> `audit_record_genesis_with_prior_hash`
- `audit_non_genesis_without_prior` -> `audit_record_non_genesis_missing_prior_hash`
- `audit_chain_hash_mismatch` -> `audit_record_prior_hash_mismatch`
- `audit_payload_hash_mismatch` -> `audit_record_payload_hash_mismatch`

## Validator requirements

`tools/validate_admission_chain_examples.py` must:

1. load each fixture directory;
2. validate available files against their contract schemas;
3. check cross-document references for the files present;
4. require expected failure codes for negative fixtures;
5. require zero failures for positive fixtures;
6. return nonzero on unexpected pass or unexpected failure.

## Non-goals

- No runtime execution.
- No production signing.
- No revocation-index integration.
- No database/storage semantics.
- No WORM storage implementation.
- No chain reorganization.
