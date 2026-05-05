# Workspace Operation Plane v0.1 Transition Table

Status: draft conformance guidance

This table constrains the state transitions used by `WorkspaceOperation`, `OperationTask`, and artifact admission records. Runtime code must enforce these transitions before emitting immutable `OperationEvent` records.

## Operation state transitions

| From | Allowed to | Notes |
|---|---|---|
| `queued` | `preflighting`, `running`, `canceled`, `failed` | Direct `running` allowed only for adapters with no preflight stage. |
| `preflighting` | `running`, `blocked`, `awaiting_decision`, `failed`, `canceled` | Policy and capability checks happen here. |
| `awaiting_decision` | `running`, `blocked`, `canceled`, `failed` | Requires a resolved `DecisionCard`. |
| `blocked` | `awaiting_decision`, `running`, `failed`, `canceled` | Must include responsible actor and remediation path. |
| `running` | `paused`, `retrying`, `canceling`, `failed`, `completed`, `completed_with_warnings`, `blocked`, `awaiting_decision` | Long-running operations may be interrupted by policy/auth/metadata gates. |
| `paused` | `running`, `canceling`, `failed` | Resume requires capability and authorization check. |
| `retrying` | `running`, `failed`, `blocked`, `awaiting_decision` | Requires retryable task and idempotency key. |
| `canceling` | `canceled`, `completed_with_warnings`, `compensated` | Some tasks may complete or require compensation while canceling. |
| `failed` | `retrying`, `compensated` | Retry requires retryable failure and idempotency key. |
| `completed` | none | Terminal state. New work requires new operation or child operation. |
| `completed_with_warnings` | none | Terminal state. Warnings remain inspectable. |
| `canceled` | `compensated` | Only compensation/recovery events may follow. |
| `compensated` | none | Terminal state. |

## Task state transitions

| From | Allowed to | Notes |
|---|---|---|
| `queued` | `preflighting`, `running`, `canceled`, `failed` | Task may be queued under an already running operation. |
| `preflighting` | `running`, `blocked`, `awaiting_decision`, `failed`, `canceled` | Adapter-specific preflight. |
| `awaiting_decision` | `running`, `blocked`, `canceled`, `failed` | Decision must name consequences. |
| `blocked` | `awaiting_decision`, `running`, `failed`, `canceled` | Must name responsible actor. |
| `running` | `paused`, `retrying`, `canceling`, `failed`, `completed`, `completed_with_warnings`, `blocked`, `awaiting_decision`, `stale` | Stale means lease/heartbeat failure, not task failure. |
| `paused` | `running`, `canceling`, `failed` | Resume may require renewed lease. |
| `retrying` | `running`, `failed`, `blocked`, `awaiting_decision` | Must reuse idempotency scope unless explicitly forked. |
| `canceling` | `canceled`, `completed_with_warnings`, `compensated` | Cancel may be compensating. |
| `stale` | `running`, `failed`, `canceled` | Recovery worker may resume if safe. |
| `failed` | `retrying`, `compensated` | Retry only when retryable. |
| `completed` | none | Terminal. |
| `completed_with_warnings` | none | Terminal. |
| `canceled` | `compensated` | Only compensation/recovery may follow. |
| `compensated` | none | Terminal. |

## Artifact admission transitions

| From | Allowed to | Notes |
|---|---|---|
| `not_stored` | `stored`, `rejected` | No preview/indexing allowed. |
| `stored` | `quarantined`, `pending_metadata`, `pending_policy`, `pending_encryption`, `pending_scan`, `admitted`, `rejected`, `archived` | Storage does not imply usability. |
| `quarantined` | `pending_metadata`, `pending_policy`, `pending_encryption`, `pending_scan`, `admitted`, `rejected`, `archived` | Quarantined artifacts cannot be read by agents unless policy permits. |
| `pending_metadata` | `pending_policy`, `admitted`, `rejected`, `archived` | Required fields must be completed. |
| `pending_policy` | `admitted`, `rejected`, `archived`, `pending_metadata`, `pending_encryption`, `pending_scan` | Policy can require other gates. |
| `pending_encryption` | `pending_policy`, `admitted`, `rejected`, `archived` | Key/IdP resolution required. |
| `pending_scan` | `pending_policy`, `admitted`, `rejected`, `archived` | Scans include malware/secrets/PII where enabled. |
| `admitted` | `activated`, `archived` | Activation may require indexing/preview steps. |
| `activated` | `archived` | Active usable artifact. |
| `rejected` | `archived` | Rejected artifact may remain for audit. |
| `archived` | none | Terminal for active use. |

## Global invariants

1. `completed`, `completed_with_warnings`, and `compensated` are terminal operation states.
2. `completed` task states are terminal.
3. Retrying a failed task requires `retryable=true` and a non-empty `idempotency_key`.
4. A blocked state must carry `responsible_actor` and at least one remediation option.
5. `awaiting_decision` requires at least one pending `DecisionCard`.
6. An artifact cannot become `activated` before it is `admitted`.
7. Quarantined artifacts cannot be previewed, indexed, published, or read by agents unless policy explicitly permits that action.
8. Compensation must reference the operation, task, or artifact being compensated.
