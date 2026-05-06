# Decision-Grade World Signal Contracts v0.1

Status: draft contract spine
Owning repo: Prophet Core Contracts
Related repos: `SocioProphet/gaia-world-model`, `SocioProphet/prophet-core-ledger`, `SocioProphet/prophet-platform-fabric-mlops-ts-suite`, `SocioProphet/prophet-domain-gaia-ontology`

## Purpose

This document defines the shared contract vocabulary for governed world-signal ingestion, entity concordance, energy-resolution ledgers, and proof artifacts.

The design rule is simple:

> No derived world signal, entity-resolution output, model assessment, or proof claim becomes operationally usable without an explicit contract, provenance, policy decision, and replay/admission path.

These contracts are intended to support GAIA world-model ingestion, Prophet ledger evidence, MLOps evaluation gates, and agent/action policy admission.

## Contract family

### 1. FeatureRegistryEntry

A registry entry describes a provisionable signal feature, such as a weather variable, foot-traffic index, derived index, mobility signal, or model-produced feature.

Required fields:

- `feature_id`: stable namespaced ID.
- `feature_name`: human-readable name.
- `category`: domain grouping.
- `description`: semantic description.
- `coverage`: geographic/domain coverage.
- `file_formats`: supported representations.
- `temporal_grain`: nullable, e.g. `15min`, `hourly`, `daily`.
- `horizon`: nullable forecast/history horizon.
- `update_cadence`: nullable freshness expectation.
- `spatial_type`: nullable, e.g. `point`, `grid`, `polygon`, `tile_raster`, `tile_vector`.
- `resolution`: nullable spatial resolution.
- `units`: nullable units.
- `nullability`: nullable missingness semantics.
- `provenance_requirements`: minimum evidence required for use.

Example use cases:

- weather forecast features;
- FTI daily features;
- derived lifestyle or decision indices;
- ML feature-store registration.

### 2. EnergyLedgerEntry

An EnergyLedgerEntry records ambiguity, separation, stability, and promotion gating for extracted evidence or entity-resolution outputs.

Required fields:

- `doc_id` or `source_artifact_id`;
- `extraction_run_id`;
- `policy_id`;
- `candidate_set_id`;
- `top_entity_id`;
- `top_score`;
- `runnerup_entity_id`;
- `runnerup_score`;
- `margin_delta`;
- `perturbation_flip_rate`;
- `promotion_decision`;
- `decision_reason_codes`;
- `provenance_offsets` where available.

Promotion decisions:

- `REJECT`;
- `REVIEW`;
- `INSERT_EVIDENCE_ONLY`;
- `PROMOTE_CANONICAL`.

Invariant:

> Low-margin or unstable evidence must not auto-promote to canonical state.

### 3. ConcordanceLink

A ConcordanceLink is the crosswalk from a source record to a canonical entity.

Required fields:

- `source_system`;
- `source_native_id`;
- `source_record_id`;
- `canonical_entity_id`;
- `resolver_run_id`;
- `policy_id`;
- `confidence`;
- `status`;
- `decision_ledger_id`.

Statuses:

- `ACTIVE`;
- `PENDING_REVIEW`;
- `REJECTED`;
- `SUPERSEDED`.

Invariant:

> The crosswalk is a first-class integration artifact, not an incidental byproduct of golden-record projection.

### 4. DecisionLedgerEntry

A DecisionLedgerEntry records a policy-governed survivorship, promotion, merge, split, or attribute-selection decision.

Required fields:

- `decision_id`;
- `decision_type`;
- `policy_id`;
- `input_artifact_hashes`;
- `candidate_ids`;
- `selected_id` or `selected_value`;
- `rule_trace`;
- `confidence`;
- `responsible_actor`;
- `created_at`;
- `replay_instructions`.

Decision types:

- `MATCH`;
- `MERGE`;
- `SPLIT`;
- `ATTRIBUTE_SURVIVORSHIP`;
- `FEATURE_PROMOTION`;
- `ACTION_ADMISSION`;
- `POLICY_BLOCK`.

### 5. ProofArtifact

A ProofArtifact is a replayable evidence pack for claims used by policy, security, or action admission.

Required fields:

- `claim_name`;
- `claim_version`;
- `input_hashes`;
- `analyzer`;
- `analysis_domains`;
- `budget`;
- `precision_notes`;
- `result_status`;
- `witness` or `counterexample`;
- `replay_instructions`;
- `signature` or provenance hook.

Result statuses:

- `PROVED`;
- `VIOLATED`;
- `UNKNOWN`;
- `TIMEOUT`;
- `PRECISION_LOSS_REVIEW_REQUIRED`.

## Admission membrane

Any feature, concordance result, extracted evidence item, model assessment, or proof claim moves through this state path:

```text
OBSERVED -> CONTRACT_VALIDATED -> LEDGERED -> POLICY_EVALUATED -> PROMOTED | REVIEW | REJECTED | EVIDENCE_ONLY
```

The state path is intentionally compatible with the Workspace Operation Plane: no artifact becomes usable without admission, idempotency, failure classification, and responsible actor attribution.

## Implementation backlog

1. Add JSON Schemas for each contract family.
2. Add examples for:
   - FTI daily feature;
   - 15-minute weather forecast feature;
   - ACR concordance link;
   - EUTC-style energy ledger entry;
   - no-escape proof artifact.
3. Add validation fixtures and a lightweight contract validator.
4. Register integration ownership in the GAIA and MLOps repos.

## Non-goals

- These contracts do not implement the resolver or model runtime.
- These contracts do not bless any specific vendor feature catalog.
- These contracts do not permit automated high-stakes personality, interview, or leadership assessment without human-in-the-loop review and fairness evaluation.
