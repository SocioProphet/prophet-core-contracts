# Workspace Operation Plane v0.1

Status: draft contract spine

Issue: SocioProphet/prophet-core-contracts#1

## Purpose

The Workspace Operation Plane defines the canonical lifecycle vocabulary for meaningful workspace mutations across SocioProphet, SourceOS, and SociOS surfaces. Uploads, imports, sync, terminal commands, browser captures, agent actions, memory ingestion, repo indexing, release packaging, security exercises, and cognition-loop outputs must use a common operation model instead of feature-local state machines.

## Primary rule

No feature bypasses the Operation Plane. No agent writes side effects outside an OperationContract. No artifact becomes usable without admission. No retry executes without idempotency. No failure is emitted without classification and responsible actor. No diagnostic export ships without redaction.

## Core objects

- `WorkspaceOperation`: aggregate unit of work.
- `OperationTask`: executable child task within an operation.
- `OperationCommand`: validated intent issued by UI, agent, worker, or system.
- `OperationEvent`: immutable lifecycle event emitted after command validation.
- `OperationSnapshot`: materialized current operation state.
- `TaskSnapshot`: materialized current task state.
- `Artifact`: typed object produced, consumed, imported, generated, or transformed by an operation.
- `ArtifactTypeRegistryEntry`: declarative artifact-type capabilities and limits.
- `ArtifactAdmissionGate`: artifact gate verdict and remediation guidance.
- `DecisionCard`: human or agent decision request with consequences.
- `PolicyGateRecord`: policy evaluation result persisted with the operation.
- `ConflictResolution`: conflict record with resolution options and selected outcome.
- `RemediationAction`: tracked action to clear blocked/failed operation conditions.
- `TrustBoundary`: external/internal trust seam metadata used in operation policy.
- `CapabilityProfile`: operation and artifact capabilities granted to an actor.
- `DiagnosticBundleMetadata`: redaction and evidence metadata for diagnostic exports.
- `AdapterContract`: declaration for operation-type adapters.

## Operation states

`queued`, `preflighting`, `awaiting_decision`, `blocked`, `running`, `paused`, `retrying`, `canceling`, `canceled`, `failed`, `completed`, `completed_with_warnings`, `compensated`.

## Artifact admission states

`not_stored`, `stored`, `quarantined`, `pending_metadata`, `pending_policy`, `pending_encryption`, `pending_scan`, `admitted`, `activated`, `rejected`, `archived`.

## Required invariants

1. A completed operation cannot return to `running` without creating a new retry attempt or child operation.
2. A canceled operation cannot emit new artifact-admitted events except through a compensation or recovery operation.
3. A failed task can retry only if `retryable=true` and an `idempotency_key` is present.
4. A blocked operation must identify a responsible actor and at least one remediation path.
5. A decision-required operation must include a DecisionCard with allowed options and consequences.
6. An artifact cannot become `activated` before it is `admitted`.
7. A quarantined artifact cannot be indexed, previewed, read by agents, or published unless policy explicitly permits that action.
8. A compensation event must reference the operation, task, or artifact it compensates.

## Command/event boundary

UI, agents, workers, and local daemons issue `OperationCommand` records. The runtime validates authorization, policy, state transition, idempotency, and adapter contract rules before emitting `OperationEvent` records. Consumers must not write lifecycle events directly.

## v0.1 scope

This first slice defines machine-readable schema scaffolding and examples. Runtime behavior belongs in `SocioProphet/prophet-platform`. Policy evaluation belongs in `SocioProphet/policy-fabric`. Ledger/evidence records belong in `SocioProphet/prophet-core-ledger`. Workstation/local-first contracts belong in `SociOS-Linux/workstation-contracts` and `SourceOS-Linux/sourceos-spec`.
