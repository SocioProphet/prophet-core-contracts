# Platform Root Spine v0

Status: draft contract doctrine

Corpus packet: `PKT-0001`

Source basis:

- `SRC-0001` — Integrated Design Doc: SynapseIQ Workspace Control Plane, Industry Intelligence Fabric, and Company-by-Industry Optimization Harness.
- `SRC-0004` — Workspace Control Plane — Formalized Update and Adjacent Design Inventory.
- `SRC-0006` — PROPHET v0.1 Draft.
- `SRC-0007` — SourceOS / SocioProphet Linux Image Generation and Validation Corpus.
- `SRC-0014` — SocioProphet Ecosystem Rewrite.

Claim basis:

- `CLM-0001` — Canonical state lives in a user-owned, local-first workspace control plane.
- `CLM-0004` — No external side effect is permitted without a scoped capability minted by the PROPHET execution membrane.
- `CLM-0005` — SourceOS/Socios runtime must enforce local-first as hard law with host/user/agent plane separation.
- `CLM-0010` — Every meaningful workspace mutation is a `WorkspaceOperation`.
- `CLM-0016` — The optimization harness ranks next packages, experiments, data sources, surfaces, and bounded actions under evidence, policy, value, runtime, and authority constraints.

Decision basis:

- `DEC-0001` — Adopt local-first Workspace Control Plane as canonical state layer.
- `DEC-0002` — Adopt SourceOS/Socios runtime as sovereign host/user/agent substrate.
- `DEC-0003` — Adopt PROPHET as deterministic side-effect membrane.
- `DEC-0004` — Adopt WorkspaceOperation for all meaningful mutations.
- `DEC-0006` — Use Drive for durable context and Git for executable truth.
- `DEC-0007` — Create corpus registry as control index for all source/claim/decision routing.

## Purpose

This document freezes the root spine for SocioProphet core contracts. It is intentionally smaller than the full platform thesis. Its job is to identify the layers that must exist before runtime services, semantic packages, user interfaces, agents, optimization harnesses, or product workrooms can safely execute.

## Root spine

```text
Institutional authority
  -> SourceOS / Socios local-first runtime
  -> WorkspaceOperation plane
  -> PROPHET execution membrane
  -> transparent telemetry and evidence receipts
  -> ontology / KMAAS / SynapseIQ semantics
  -> claim, value, control, and optimization layers
```

This order is normative. Later layers may depend on earlier layers; earlier layers must not depend on later product surfaces.

## Layer responsibilities

### 1. Institutional authority

Institutional authority defines where a source, package, model, standard, public-good artifact, commercial feature, or restricted evidence object belongs. Technical artifacts must not erase the difference between commercial, commons, legal, IP, treasury, nonprofit, public-good, and restricted evidence contexts.

Contract implication: portable artifacts need a `home`, `authority`, or `governance_context` field when promotion or execution depends on ownership, license, consent, public-good posture, or restricted handling.

### 2. SourceOS / Socios local-first runtime

SourceOS and Socios supply the sovereign runtime substrate:

- host plane;
- user plane;
- agent plane;
- local-first default;
- smallest-eligible worker first;
- explicit policy gate for cloud burst;
- typed objects;
- registered transforms/views with lineage;
- service lifecycle and explainability surfaces.

Contract implication: execution contracts must be able to distinguish local, private-cluster, attested-fog, and explicit cloud-burst contexts without treating cloud execution as ambient default.

### 3. WorkspaceOperation plane

The Workspace Operation Plane defines the canonical lifecycle vocabulary for meaningful workspace mutations. Uploads, imports, sync, terminal commands, browser captures, agent patches, memory ingestion, repo indexing, release packaging, security exercises, and cognition-loop outputs must use a common operation model instead of feature-local state machines.

Contract implication: no implementation repo should invent a competing mutation lifecycle. This repository owns the canonical operation vocabulary and conformance fixtures.

### 4. PROPHET execution membrane

PROPHET is the deterministic side-effect membrane. Probabilistic, hybrid, or agentic reasoning may happen upstream, but every external side effect must cross a typed, scoped, fail-closed execution boundary.

Primary invariant:

> No side effect without a scoped capability minted by the execution membrane.

Contract implication: action-capable systems must carry scoped capability, actor, resource, purpose, policy, evidence, authority, expected mutation, rollback/compensation, and receipt metadata.

### 5. Transparent telemetry and evidence receipts

The platform must be able to prove what happened. Meaningful runtime events must be manifest-bound, policy-evaluated, receipt-bearing, and retention/deletion-aware.

Contract implication: action, operation, package, claim, and model governance contracts must reserve fields for telemetry plane, policy outcome, receipt reference, retention class, and evidence reference.

### 6. Ontology / KMAAS / SynapseIQ semantics

Semantic systems give meaning to assets, observations, claims, package outputs, internal org vertices, industry cartridges, and decision jobs. SynapseIQ compiles governed signals into semantic enrichments and package outputs, but it is not the root platform. It sits inside the sovereign substrate.

Contract implication: semantic outputs must reference source contracts, evidence, claim type, confidence, policy boundary, and package purpose.

### 7. Claim, value, control, and optimization layers

Higher layers generate claims, run argument hygiene, map package outputs to value, govern bounded control, and rank next actions through the optimization harness.

Contract implication: recommendations are not actions. A recommendation must still pass through evidence, value, policy, authority, and PROPHET execution gates before mutation.

## Non-goals

This document does not define:

- the full Workspace Operation schema;
- the full PROPHET scoped capability schema;
- SynapseIQ package schemas;
- SourceOS image validation logic;
- product UI behavior;
- legal entity formation advice;
- medical, labor, or forensic restricted-data handling in detail.

Those are downstream contract or implementation packets.

## Acceptance criteria

The root spine is usable when:

1. Core contract docs and schemas can reference this layering without ambiguity.
2. WorkspaceOperation, PROPHET, telemetry, and SynapseIQ contracts can identify which layer owns each responsibility.
3. Runtime repos do not define competing operation lifecycles or side-effect authority models.
4. Product repos can reference the root spine without importing restricted source evidence.
5. The corpus registry can link source IDs, claim IDs, decision IDs, work packets, and promoted Git artifacts.
