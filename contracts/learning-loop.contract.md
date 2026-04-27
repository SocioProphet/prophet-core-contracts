# Learning Loop Platform Contract

Status: draft
Owner: Prophet Core Contracts
Depends on:
- SocioProphet/socioprophet-standards-knowledge: `standards/learning-loop-standard.v1.md`
- SocioProphet/socioprophet-standards-storage: `standards/evidence-bundle-standard.v1.md`

## Purpose

This contract defines how Prophet Platform, Sociosphere, MLOps repositories, Atlas orchestration, Alexandrian Academy, SourceOS/SociOS lifecycle work, and ontology repositories consume systems learning-loop standards.

The contract turns learning-loop research into platform primitives with explicit evidence, validation, governance, and transition gates.

## Contract objects

### LearningLoopContract

```yaml
id: stable identifier
standard_ref: standards/learning-loop-standard.v1.md
loop_record_ref: canonical corpus or ontology record
consumer_repo: repository consuming the loop
consumer_context: platform | mlops | academy | atlas | os_lifecycle | ontology | governance | agent
required_evidence_bundle: EvidenceBundle reference
local_adapter: path to local alignment doc, schema, workflow, or code adapter
validation_gate: Sociosphere, Delivery Excellence, CI, or standards review gate
status: proposed | active | implemented | deprecated
```

### CapabilityTransitionContract

```yaml
id: stable identifier
capability: named platform, model, OS, agent, or ontology capability
source_learning_loop: LearningLoop reference
transition_gate: criteria for promotion, deployment, curriculum inclusion, or platform adoption
evidence_bundle: EvidenceBundle reference
owner_repo: canonical implementation repo
consumer_repos: repositories consuming the capability
rollback_or_deprecation: required fallback path
```

### AgentLearningContract

```yaml
id: stable identifier
agent_role: michael_agent | socioprophet_agent | prophet_platform_agent | mlops_agent | sourceos_agent | atlas_agent | other
allowed_inputs: standards, corpus paths, ontology paths, evidence bundles
allowed_outputs: summaries, extracted entities, proposed ontology updates, platform primitive proposals, curriculum drafts, implementation issues
forbidden_outputs: unsupported claims, operational extrapolation, hidden tasking, unreviewed strategic conclusions
evidence_required: true
review_gate: required review owner
```

## Required local adapter

Every consuming repo MUST include a local alignment document with:

```yaml
standard_consumed: path or URI
local_scope: what this repo implements or teaches
objects_consumed: LearningLoop, EvidenceBundle, ProgramProfile, etc.
objects_emitted: repo-specific outputs
validation_path: CI, review, Sociosphere, Delivery Excellence, or standards gate
owner: team, repo, or agent steward
```

## Integration gates

A repo is not considered integrated unless all of the following are true:

1. It references the canonical standard.
2. It contains a local adapter or alignment document.
3. It contains at least one schema, example, ontology mapping, workflow, or implementation artifact.
4. It has an evidence/review gate.

## Platform primitive mapping

Learning loops map into Prophet Platform primitives as follows:

```text
Need or Signal -> Challenge
Challenge -> Workstream or Initiative
Funding/Resource Allocation -> ResourceGrant or SupportVehicle
Prototype -> CapabilityCandidate
Test Environment -> EvaluationContext
Feedback Signal -> FeedbackArtifact
Evidence Artifact -> EvidenceBundle
Transition Gate -> CapabilityTransition
Doctrine Update -> PolicyUpdate, OntologyUpdate, CurriculumUpdate, or RuntimeUpdate
```

## MLOps serving correction

New model-serving loop work MUST default to modern serving substrates. Ray Serve and KubeRay are the preferred primary serving substrate. KServe, Seldon, Triton, BentoML, MLflow, TorchServe, and TensorFlow Serving are compatibility or specialized integration lanes. Clipper is legacy-reference only.

Any repo that still contains Clipper-era serving material MUST mark it as:

```yaml
runtime_status: legacy_reference
active_default: false
```

## Public-sector case-study boundary

Public-sector and national-security innovation programs may inform institutional learning-loop extraction, challenge design, evidence-gate design, and capability-transition modeling. They MUST NOT be represented as operational instructions, procurement endorsements, or unsourced strategic claims.
