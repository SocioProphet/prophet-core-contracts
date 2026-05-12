# Admission Chain Integration Fixtures v0.1

This document defines the canonical end-to-end fixture plan for the v0.1 admission spine:

```text
PolicyRequest -> PolicyDecision -> AdmissionToken -> Effect -> AuditRecord
```

It is the shared acceptance target for the AdmissionToken binding tranche and the AuditRecord tranche.

## Locked decisions

1. `Effect` is included as a minimal v0.1 stub.
2. The integration validator lives in `tools/validate_admission_chain_examples.py`.
3. `make validate` runs integration checks by default through `validate-integration`.
4. PR #11 does not include AuditRecord files. It stops at `PolicyRequest -> PolicyDecision -> AdmissionToken -> Effect`.
5. PR #12 adds AuditRecord schema, fixtures, and audit-side integration checks.

## Fixture root

```text
tests/fixtures/integration/admission_chain/
```

The canonical happy path eventually contains:

```text
canonical_happy_path/
  01_policy_request.json
  02_policy_decision.json
  03_admission_token.json
  04_effect.json
  05_audit_record.json
```

For PR #11, the fixture stops at `04_effect.json`. PR #12 adds `05_audit_record.json`.

## Effect v0.1 stub

Minimum fields:

| Field | Meaning |
|---|---|
| `schema_version` | Effect schema version |
| `effect_id` | effect identifier |
| `admission_token_id` | token authorizing the effect |
| `action_type` | attempted action |
| `resource_ref` | attempted target resource |
| `requesting_actor_id` | actor attempting effect |
| `subject_actor_id` | subject on whose behalf effect occurs |
| `attempted_at` | timestamp |
| `outcome` | `executed`, `failed`, `not_attempted`, `rolled_back`, or `partial` |
| `error_ref` | optional failure reference |
| `rollback_of_effect_ref` | optional rollback target |

The `outcome` vocabulary must match AuditRecord `execution_outcome`.

## Cross-reference invariants

The integration validator enforces:

| # | Invariant |
|---:|---|
| 1 | `policy_decision.input_hash == hash(canonical_form(policy_request))` |
| 2 | `policy_decision.policy_request_ref.request_id == policy_request.request_id` |
| 3 | `admission_token.policy_decision_ref.decision_id == policy_decision.decision_id` |
| 4 | `admission_token.policy_request_ref.request_id == policy_request.request_id` |
| 5 | `admission_token.risk_tier == policy_decision.risk_tier` |
| 6 | `admission_token.restrictions ⊇ policy_decision.restrictions` |
| 7 | `admission_token.expires_at <= policy_decision.decision_valid_until` |
| 8 | `admission_token.selected_action_id ∈ policy_decision.granted_actions` |
| 9 | `effect.admission_token_id == admission_token.token_id` |
| 10 | `effect.action_type == admission_token.granted_action.action_type` |
| 11 | `effect.resource_ref == admission_token.granted_action.resource_ref` |
| 12 | `effect.requesting_actor_id == admission_token.requesting_actor_id` |
| 13 | `effect.subject_actor_id == admission_token.subject_actor_id` |
| 14 | `audit_record.policy_request_ref.id == policy_request.request_id` |
| 15 | `audit_record.policy_request_ref.schema_version == policy_request.schema_version` |
| 16 | `audit_record.policy_decision_ref.id == policy_decision.decision_id` |
| 17 | `audit_record.admission_token_ref.id == admission_token.token_id` |
| 18 | `audit_record.effect_ref.id == effect.effect_id` |
| 19 | `audit_record.verification_result.risk_tier == admission_token.risk_tier` |
| 20 | `audit_record.verification_result.restrictions == admission_token.restrictions` |
| 21 | `audit_record.admission_outcome == "accepted"` for happy path |
| 22 | `audit_record.execution_outcome == "executed"` for happy path |
| 23 | `audit_record.prior_record_hash == null` for genesis or matches prior record |
| 24 | `audit_record.payload_hash == hash(canonical_form(audit_record_without_payload_hash))` |

## Positive fixtures

| Fixture | PR | Purpose |
|---|---:|---|
| `canonical_happy_path/` | #11 then #12 | Reference fixture; PR #11 validates through Effect, PR #12 adds AuditRecord |
| `allow_with_constraints/` | #11 then #12 | Constrained allow; token carries decision restrictions and may add stricter restrictions |
| `chained_record/` | #12 | AuditRecord with non-null prior hash referencing a prior record |
| `genesis_record/` | #12 | AuditRecord with null prior hash and genesis semantics |
| `rejected_at_admission/` | #12 | Deny decision; no token minted; audit shows rejected / not_attempted |
| `failed_execution/` | #12 | Token minted; effect failed; audit shows accepted / failed |
| `rollback_chain/` | #12 | Original execution plus rollback record referencing original |
| `revocation_deferred/` | #12 | High-risk token with deferred v0.2 revocation check recorded faithfully |

## Negative fixtures: PR #11 scope

These fixtures validate binding from PolicyRequest / PolicyDecision into AdmissionToken and Effect.

| Fixture | Expected failure | Invariant |
|---|---|---:|
| `decision_request_hash_mismatch/` | `policy_decision_input_hash_mismatch` | 1 |
| `decision_request_id_mismatch/` | `policy_decision_request_id_mismatch` | 2 |
| `token_decision_id_mismatch/` | `admission_token_decision_id_mismatch` | 3 |
| `token_request_id_mismatch/` | `admission_token_request_id_mismatch` | 4 |
| `token_risk_tier_mismatch/` | `admission_token_risk_tier_mismatch` | 5 |
| `token_restrictions_weakened/` | `admission_token_restrictions_not_superset` | 6 |
| `token_expires_after_decision/` | `admission_token_ttl_widening` | 7 |
| `token_action_not_granted/` | `admission_token_action_not_in_granted_actions` | 8 |
| `effect_token_id_mismatch/` | `effect_token_id_mismatch` | 9 |
| `effect_action_widens_token/` | `effect_action_not_in_token` | 10 |
| `effect_resource_widens_token/` | `effect_resource_not_in_token` | 11 |
| `effect_actor_mismatch/` | `effect_requesting_actor_mismatch` | 12 |
| `effect_subject_mismatch/` | `effect_subject_actor_mismatch` | 13 |

## Negative fixtures: PR #12 scope

These fixtures validate AuditRecord binding, outcome model, and chain integrity.

| Fixture | Expected failure | Invariant |
|---|---|---:|
| `audit_request_ref_mismatch/` | `audit_record_request_ref_id_mismatch` | 14 |
| `audit_request_ref_missing_version/` | `audit_record_request_ref_missing_schema_version` | 15 |
| `audit_decision_ref_mismatch/` | `audit_record_decision_ref_id_mismatch` | 16 |
| `audit_token_ref_mismatch/` | `audit_record_token_ref_id_mismatch` | 17 |
| `audit_effect_ref_mismatch/` | `audit_record_effect_ref_id_mismatch` | 18 |
| `audit_verification_risk_tier_drift/` | `audit_record_verification_risk_tier_drift` | 19 |
| `audit_verification_restrictions_drift/` | `audit_record_verification_restrictions_drift` | 20 |
| `audit_rejected_but_executed/` | `audit_record_admission_execution_inconsistency` | semantic |
| `audit_chain_hash_mismatch/` | `audit_record_prior_hash_mismatch` | 23 |
| `audit_payload_hash_mismatch/` | `audit_record_payload_hash_mismatch` | 24 |
| `audit_rejected_with_executed/` | `audit_record_rejected_but_execution_attempted` | semantic |
| `audit_accepted_with_not_attempted/` | `audit_record_accepted_but_not_attempted` | semantic |
| `audit_rollback_missing_prior/` | `audit_record_rollback_missing_target_ref` | semantic |
| `audit_genesis_with_prior_hash/` | `audit_record_genesis_with_prior_hash` | semantic |
| `audit_non_genesis_without_prior/` | `audit_record_non_genesis_missing_prior_hash` | semantic |

## Validator behavior

`tools/validate_admission_chain_examples.py` must:

1. load each fixture directory;
2. run each file against its own schema;
3. run cross-reference invariants;
4. compare failure codes against `expected_failure` for negative fixtures;
5. require positive fixtures to produce zero failures;
6. return nonzero on unexpected pass or unexpected failure.

Add:

```bash
make validate-integration
```

and include it in:

```bash
make validate
```

## PR #11 acceptance criteria

PR #11 is complete when:

1. the 8 admission binding failure fixtures pass with expected failure codes;
2. the 5 effect binding failure fixtures pass with expected failure codes;
3. `canonical_happy_path/` and `allow_with_constraints/` pass through Effect with zero failures;
4. `make validate-integration` is green;
5. AdmissionToken schema/reference changes needed for these fixtures are included;
6. Effect stub schema is included;
7. no AuditRecord schema is added;
8. no revocation-index implementation is added.

## PR #12 acceptance criteria

PR #12 is complete when:

1. the 10 audit binding failure fixtures pass with expected failure codes;
2. the 5 outcome model failure fixtures pass with expected failure codes;
3. remaining positive fixtures pass with zero failures;
4. `make validate-integration` is green;
5. AuditRecord schema, validator, and integration validator updates are included.

## Non-goals

- No runtime execution.
- No production signing.
- No revocation-index integration.
- No querying or storage semantics.
- No WORM storage implementation.
- No chain reorganization. Chains are monotonic and append-only.
