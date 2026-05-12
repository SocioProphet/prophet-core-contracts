# Prophet Core Contracts

Canonical contract and conformance surface for Prophet core systems.

This repository now carries the draft **Workspace Operation Plane v0.1** contract spine. It remains auditable, provenance-first, and open-only.

## Workspace Operation Plane v0.1

The Workspace Operation Plane defines the common lifecycle vocabulary for meaningful workspace mutations across SocioProphet, SourceOS, and SociOS surfaces.

Examples of operation-governed mutations:

- upload/import
- repo import/index
- memory ingestion
- terminal command
- browser capture/download/upload
- agent patch/report/remediation
- local sync/reconciliation
- release/package evidence
- cyber range exercise evidence
- governed cognition/reflection outputs

Primary rule:

> No feature bypasses the Operation Plane. No agent writes side effects outside an OperationContract. No artifact becomes usable without admission. No retry executes without idempotency. No failure is emitted without classification and responsible actor. No diagnostic export ships without redaction.

## PolicyRequest / PolicyDecision v0.1

`PolicyRequest` and `PolicyDecision` define the canonical Policy Fabric input/output pair used by the Operation Plane.

- `PolicyRequest` is the deterministic input bundle sent to Policy Fabric.
- `PolicyDecision` is the immutable policy artifact referenced by `AdmissionToken`.
- Deny, review, quarantine, and revoke are first-class immutable decisions, not silent absence.
- Revoke is modeled as a new decision referencing a prior decision through `revokes_decision_ref`.

## Current contract files

- `docs/workspace-operation-plane-v0.1.md`
- `docs/workspace-operation-transition-table-v0.1.md`
- `docs/policy-request-decision-v0.1.md`
- `schemas/workspace-operation.schema.json`
- `schemas/operation-task-event.schema.json`
- `schemas/artifact-admission.schema.json`
- `schemas/decision-policy-adapter.schema.json`
- `schemas/policy-request.schema.json`
- `schemas/policy-decision.schema.json`

## Current examples

- `examples/workspace-operation/upload-import-happy-path.json`
- `examples/workspace-operation/upload-import-partial-failure.json`
- `examples/workspace-operation/canceled-operation.json`
- `examples/workspace-operation/agent-patch-proposal.json`
- `examples/workspace-operation/memory-ingestion-policy-blocked.json`
- `examples/workspace-operation/terminal-command-completed.json`
- `examples/workspace-operation/repo-import-index.json`
- `examples/workspace-operation/sync-reconciliation-conflict.json`
- `examples/workspace-operation/redacted-diagnostic-export.json`
- `examples/workspace-operation/release-package-evidence.json`
- `examples/workspace-operation/security-exercise-governed.json`
- `examples/policy/policy-request.example.json`
- `examples/policy/policy-decision.*.example.json`
- `examples/policy/negative/*.invalid.json`

## Validation

Run:

```bash
make validate
```

Current validation includes:

- `tools/validate_workspace_operation_examples.py` for operation-centered fixtures, retry/idempotency rules, artifact activation/admission consistency, pending decisions, blocking policy gate remediation, and blocked/awaiting-decision operation references.
- `tools/validate_regis_examples.py` for Regis Semantic Feature Plane examples.
- `tools/validate_policy_examples.py` for PolicyRequest and PolicyDecision schema and semantic fixtures.

CI also runs `make validate` through `.github/workflows/validate.yml`.

Full JSON Schema validation should be added by `SourceOS-Linux/sourceos-devtools` as part of the Operation Plane conformance runner.

## Repository boundaries

This repository owns canonical contract vocabulary, schemas, examples, transition guidance, and conformance fixtures.

It does **not** own runtime services, policy execution, UI state, local sync daemons, browser behavior, terminal behavior, or agent runtime authority.

Integration ownership:

- Runtime: `SocioProphet/prophet-platform`
- Policy: `SocioProphet/policy-fabric` and `SocioProphet/prophet-core-policy`
- Ledger/evidence: `SocioProphet/prophet-core-ledger`
- Agent execution: `SocioProphet/agentplane`
- Agent identity/authority: `SocioProphet/agent-registry`
- Workspace controller/UI: `SocioProphet/sociosphere`
- Workstation contracts: `SociOS-Linux/workstation-contracts`
- SourceOS local-first contracts: `SourceOS-Linux/sourceos-spec`
- SourceOS sync daemon: `SourceOS-Linux/sourceos-syncd`
- SourceOS shell: `SourceOS-Linux/sourceos-shell`
- SourceOS local tooling: `SourceOS-Linux/sourceos-devtools`
- SourceOS terminal surface: `SourceOS-Linux/TurtleTerm`
- SourceOS browser surface: `SourceOS-Linux/BearBrowser`
- SourceOS local agent machine: `SourceOS-Linux/agent-machine`

## v0.1 implementation status

Draft contract spine, schema scaffolding, transition guidance, example fixtures, CI validation, and lightweight validation are present. Schemas and fixtures are intentionally minimal and should be tightened through conformance tests before runtime implementation depends on them as stable APIs.
