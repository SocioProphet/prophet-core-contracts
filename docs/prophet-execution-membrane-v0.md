# PROPHET Execution Membrane v0

Status: draft contract doctrine

Corpus packet: `PKT-0003`

Source basis:

- `SRC-0006` — PROPHET v0.1 Draft.
- `SRC-0001` — Integrated Design Doc and platform root-spine amendments.
- `SRC-0004` — Workspace Control Plane formalized update.

Claim basis:

- `CLM-0004` — No external side effect is permitted without a scoped capability minted by the PROPHET execution membrane.

Decision basis:

- `DEC-0003` — Adopt PROPHET as deterministic side-effect membrane.

## Purpose

The PROPHET execution membrane is the fail-closed side-effect boundary for SocioProphet systems. Agentic, probabilistic, or hybrid reasoning may happen before the membrane. External mutation must cross the membrane through explicit, typed, scoped capability records.

## Primary invariant

> No side effect without a scoped capability minted by the execution membrane.

## Membrane responsibilities

The membrane must bind:

- actor identity;
- role or delegated authority;
- resource scope;
- allowed verbs;
- purpose;
- policy basis;
- evidence basis;
- expiration;
- idempotency expectations;
- approval state;
- expected mutation;
- rollback or compensation path;
- telemetry and receipt requirements.

## Non-goals

The membrane does not decide product strategy, write UI state, execute policy internally, or bypass WorkspaceOperation. It provides the contract vocabulary for safe execution. Policy engines, AgentPlane, SourceOS, Sociosphere, and runtime services consume the contract.

## Required downstream behavior

A runtime that performs an action must be able to answer:

1. Which actor requested the action?
2. Which capability authorized it?
3. Which resource and verb were allowed?
4. Which policy version evaluated the action?
5. Which evidence justified the action?
6. Which workspace operation or runtime run bound the action?
7. Which receipt proves the action outcome?
8. Which rollback or compensation path applies?

## Relationship to WorkspaceOperation

WorkspaceOperation is the durable mutation lifecycle. PROPHET is the side-effect authority membrane.

A mutation is valid only when both conditions hold:

```text
WorkspaceOperation state permits the mutation.
ScopedCapability permits the actor/resource/verb/purpose under policy.
```

Neither is sufficient alone.

## Initial contract files

- `schemas/scoped-capability.schema.json`
- `examples/prophet/scoped-capability-local-command.json`

## Acceptance criteria

The v0 membrane contract is usable when:

1. Scoped capabilities can be represented as machine-checkable JSON objects.
2. Examples include actor, resource, verb, purpose, policy, evidence, expiration, and receipt requirements.
3. Runtime repos can reference this contract without inventing a competing authority vocabulary.
4. Missing or expired scoped capability records are treated as fail-closed by downstream runtimes.
