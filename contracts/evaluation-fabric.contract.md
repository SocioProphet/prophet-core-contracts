# Evaluation Fabric Platform Contract

Status: draft
Owner: Prophet Core Contracts
Depends on:
- SocioProphet/socioprophet-standards-knowledge: `standards/evaluation-fabric-standard.v1.md`
- SocioProphet/socioprophet-standards-storage: `standards/evaluation-record-standard.v1.md`
- SocioProphet/sociosphere: `standards/angel-of-the-lord/README.md`

## Purpose

This contract defines how Prophet Platform, Sociosphere, Alexandrian Academy, MLOps repositories, Atlas orchestration, ontology repositories, and SourceOS/SociOS lifecycle repositories consume the SocioProphet evaluation fabric.

The contract makes evaluation a platform primitive. Evaluation records are not optional commentary. They are required evidence for education completion, model readiness, ontology updates, OS lifecycle claims, platform transition, release readiness, and agent capability claims.

## Contract objects

### EvaluationFabricContract

```yaml
id: stable identifier
standard_ref: SocioProphet/socioprophet-standards-knowledge:standards/evaluation-fabric-standard.v1.md
storage_standard_ref: SocioProphet/socioprophet-standards-storage:standards/evaluation-record-standard.v1.md
consumer_repo: repository consuming the contract
consumer_context: platform | academy | mlops | ontology | sourceos | socios | atlas | governance | agent
local_alignment_doc: path to local adapter document
evaluation_tracks: list of EvaluationTrack references or planned tracks
evidence_bundle_refs: list of EvidenceBundle references
angel_required: true | false | conditional
validation_gate: Sociosphere | Delivery Excellence | standards review | CI | human review | other
status: proposed | active | implemented | deprecated
```

### EvaluationGateContract

```yaml
id: stable identifier
gate_name: human readable name
gate_scope: education_epoch | model_deployment | model_retraining | ontology_update | os_release | boot_release | platform_capability | atlas_bundle | curriculum_module | other
required_inputs:
  - EvaluationRecord
  - EvidenceBundle
  - Rubric or Metric
  - RemediationRecord when findings exist
  - AngelEpochGrade when required
pass_rule: precise acceptance rule
fail_rule: precise rejection or remediation rule
transition_allowed: true | false | conditional
rollback_or_remediation: required action when gate fails
```

## Required downstream behavior

A consuming repository MUST:

1. reference the evaluation fabric standard;
2. define the local evaluation tracks it owns;
3. identify where evaluation records are stored;
4. identify whether Angel of the Lord grading is required;
5. define pass, fail, remediation, and blocked states;
6. provide at least one example evaluation record or schema adapter before claiming implementation.

## Canonical mappings

### Alexandrian Academy

```text
course/module -> assignment/lab/exam/project -> rubric -> evidence -> Angel epoch grade where agent education is involved -> completion/remediation
```

### Michael-agent

```text
public courseware corpus -> assessment attempt -> evidence bundle -> Angel epoch grade -> transfer task -> education ledger update
```

### MLOps

```text
dataset -> experiment -> model -> evaluation -> deployment -> feedback -> retraining/rollback -> evidence record
```

### Model serving

```text
serving runtime -> deployment manifest -> latency/quality/safety/cost metrics -> feedback capture -> rollback/retraining gate
```

Ray Serve and KubeRay are the preferred primary serving substrate. Clipper is `legacy_reference` only.

### SourceOS/SociOS

```text
build -> boot -> install -> update -> rollback -> device/fleet fingerprint -> compliance evaluation -> Angel review where required
```

### Ontology

```text
source -> extraction -> ontology diff -> SHACL/consistency validation -> query regression -> review -> graph update
```

### Atlas

```text
learning-loop objective -> bundle -> run -> evidence -> replay -> Angel review where required -> transition/remediation
```

## Non-hand-waving acceptance rule

A downstream repo cannot claim compliance with this contract unless it contains:

- a local alignment document;
- a declared evaluation track;
- a storage/evidence reference;
- a review or validation gate;
- a remediation path.

## Block conditions

A transition MUST be blocked when:

- required evidence is missing;
- evaluation tasks are undefined;
- metrics or rubrics are absent;
- required Angel grading has unresolved blocker findings;
- required Angel grading has unresolved material high findings;
- source/corpus usage is unproven or violates source constraints;
- model serving runtime is misclassified, such as treating Clipper as active primary runtime.
