# Prophet Core Contracts

Canonical contract and conformance surface for Prophet core systems.

This repository now carries the draft **Workspace Operation Plane v0.1** contract spine plus the root spine and PROPHET scoped-capability contract surface. It remains auditable, provenance-first, and open-only.

## Platform Root Spine v0

The platform root spine establishes the normative layer order that downstream runtime, semantic, governance, and product contracts should reference:

```text
Institutional authority
  -> SourceOS / Socios local-first runtime
  -> WorkspaceOperation plane
  -> PROPHET execution membrane
  -> transparent telemetry and evidence receipts
  -> ontology / KMAAS / SynapseIQ semantics
  -> claim, value, control, and optimization layers
```

Current doctrine file:

- `docs/platform-root-spine-v0.md`

## PROPHET Execution Membrane v0

The PROPHET execution membrane is the deterministic side-effect boundary for SocioProphet systems.

Primary rule:

> No side effect without a scoped capability minted by the execution membrane.

Current files:

- `docs/prophet-execution-membrane-v0.md`
- `schemas/scoped-capability.schema.json`
- `examples/prophet/scoped-capability-local-command.json`

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

## Current contract files

- `docs/platform-root-spine-v0.md`
- `docs/prophet-execution-membrane-v0.md`
- `docs/workspace-operation-plane-v0.1.md`
- `docs/workspace-operation-transition-table-v0.1.md`
- `schemas/scoped-capability.schema.json`
- `schemas/workspace-operation.schema.json`
- `schemas/operation-task-event.schema.json`
- `schemas/artifact-admission.schema.json`
- `schemas/decision-policy-adapter.schema.json`

## Current examples

- `examples/prophet/scoped-capability-local-command.json`
- `examples/workspace-operation/upload-import-happy-path.json`
- `examples/workspace-operation/upload-import-partial-failure.json`
- `examples/workspace-operation/retryable-task-failure.json`
- `examples/workspace-operation/canceled-operation.json`
- `examples/workspace-operation/agent-patch-proposal.json`
- `examples/workspace-operation/memory-ingestion-policy-blocked.json`
- `examples/workspace-operation/terminal-command-completed.json`
- `examples/workspace-operation/repo-import-index.json`
- `examples/workspace-operation/sync-reconciliation-conflict.json`
- `examples/workspace-operation/redacted-diagnostic-export.json`
- `examples/workspace-operation/release-package-evidence.json`
- `examples/workspace-operation/security-exercise-governed.json`

## Validation

Run:

```bash
make validate
```

Current validation uses:

- `tools/validate_workspace_operation_examples.py`
- `tools/validate_regis_examples.py`
- `tools/validate_scoped_capability_example.py`

CI also runs `make validate` through `.github/workflows/validate.yml`.

Full JSON Schema validation should be added by `SourceOS-Linux/sourceos-devtools` as part of the Operation Plane conformance runner.

## Repository boundaries

This repository owns canonical contract vocabulary, schemas, examples, transition guidance, conformance fixtures, root-spine doctrine, and PROPHET scoped-capability contract doctrine.

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

Draft platform root-spine doctrine, PROPHET scoped-capability contract doctrine, Workspace Operation contract spine, schema scaffolding, transition guidance, example fixtures, CI validation, and lightweight validation are present. Schemas and fixtures are intentionally minimal and should be tightened through conformance tests before runtime implementation depends on them as stable APIs.
