# Effect v0.1 Stub

Status: read-ahead target for PR #11.

`Effect` is the fourth position in the v0.1 admission chain:

```text
PolicyRequest -> PolicyDecision -> AdmissionToken -> Effect -> AuditRecord
```

## Purpose

Effect v0.1 is a static record-shape contract for integration fixtures. It is not a runtime engine and has no production execution semantics.

It exists so PR #11 can validate the link between an admitted token and the side effect that token authorizes.

## Minimal schema target

| Field | Required | Meaning |
|---|---:|---|
| `schema_version` | yes | must be `0.1.0` |
| `effect_id` | yes | stable identifier, e.g. `eff_<id>` |
| `admission_token_id` | yes | token authorizing the effect |
| `action_type` | yes | action performed or attempted |
| `resource_ref` | yes | resource targeted by the effect |
| `requesting_actor_id` | yes | actor consuming the token |
| `subject_actor_id` | yes | subject on whose behalf the action acts |
| `attempted_at` | yes | timestamp of attempted effect |
| `outcome` | yes | `executed`, `failed`, `not_attempted`, `rolled_back`, or `partial` |
| `error_ref` | no | pointer to error evidence |
| `rollback_of_effect_ref` | no | prior effect this effect rolls back |

## Invariants for PR #11

The integration validator should check:

- `effect.admission_token_id == admission_token.token_id`
- `effect.action_type == admission_token.granted_action.action_type`
- `effect.resource_ref == admission_token.granted_action.resource_ref`
- `effect.requesting_actor_id == admission_token.requesting_actor_id`
- `effect.subject_actor_id == admission_token.subject_actor_id`

## v0.2 expansion path

v0.2 may add:

- runtime-generated effect receipts;
- effect-family-specific payloads;
- partial-effect accounting;
- compensation and rollback details;
- AgentPlane execution refs;
- richer error and recovery records.

v0.1 effects should remain valid as a minimal subset under v0.2.

## Non-goals

- No runtime execution.
- No database contract.
- No production receipt format.
- No AgentPlane runtime integration.
- No effect-family-specific semantics.
