# Workspace Control Plane Core v0

Status: draft contract doctrine

Source basis:

- `workspace_control_plane_formalized_update_and_inventory.md`
- Corpus decision `D1` through `D16` in the Workspace Control Plane source document.

## Purpose

This document defines the first contract tranche for the broader Workspace Control Plane. The already-validated `WorkspaceOperation` and PROPHET membrane chain proves the mutation/evidence spine. This contract tranche defines the surrounding control-plane object model: accounts, roots, mounts, assets, attention marks, manifests, catalog entries, discovery policies, and workflow runs.

## Scope

The Workspace Control Plane owns durable local-first state for:

- external accounts and provider roots;
- mirror/live/action rail declarations;
- mounted roots and local projections;
- assets and asset versions;
- attention marks such as pin, watch, revisit, incubate, hold, and forget;
- capability and topic manifests;
- catalog entries and discovery policy;
- workflow runs and outbox-adjacent execution state.

## Root invariant

Canonical state lives in a user-owned, local-first workspace control plane. Vendor assistants and clouds are replaceable interfaces, not the source of truth.

## Relationship to WorkspaceOperation

`WorkspaceOperation` is the mutation/event unit. Workspace Control Plane Core objects provide the stable graph of roots, assets, claims, attention, capabilities, topics, catalogs, discovery rules, and workflow runs that operations mutate.

```text
WorkspaceControlPlaneObject
  -> mutated by WorkspaceOperation
  -> gated by ScopedCapability / PROPHET
  -> evidenced by ActionReceipt / ClaimRecord / EvidenceThread
```

## Contract files

Initial schema bundle:

- `schemas/workspace-control-plane/account.schema.json`
- `schemas/workspace-control-plane/root.schema.json`
- `schemas/workspace-control-plane/mount.schema.json`
- `schemas/workspace-control-plane/asset.schema.json`
- `schemas/workspace-control-plane/attention-mark.schema.json`
- `schemas/workspace-control-plane/capability-manifest.schema.json`
- `schemas/workspace-control-plane/topic-manifest.schema.json`
- `schemas/workspace-control-plane/catalog-entry.schema.json`
- `schemas/workspace-control-plane/discovery-policy.schema.json`
- `schemas/workspace-control-plane/workflow-run.schema.json`

Initial fixture:

- `examples/workspace-control-plane/workspace-control-plane-core.example.json`

Validator:

- `tools/validate_workspace_control_plane_core.py`

## Non-goals

This tranche does not implement sync engines, provider adapters, Temporal workers, Hypercore overlays, ReBAC engines, policy engines, vector stores, or production persistence. It freezes a minimal object vocabulary and validates one synthetic workspace-control-plane core fixture.
