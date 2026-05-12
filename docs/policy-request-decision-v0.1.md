# PolicyRequest and PolicyDecision v0.1

`PolicyRequest` and `PolicyDecision` define the canonical Policy Fabric input/output pair used by the Operation Plane.

`PolicyRequest` is the deterministic request bundle sent to Policy Fabric. `PolicyDecision` is the immutable decision artifact emitted by Policy Fabric and referenced by `AdmissionToken`.

## Why these land together

`PolicyDecision.input_hash` is only meaningful if the request bundle and canonicalization rule are defined. Therefore v0.1 defines request and decision together.

## Canonicalization and hash posture

v0.1 uses:

```text
rfc8785-jcs-v0.1
```

This is the Policy Fabric canonicalization profile for request and decision payloads. Hashes use SHA-256 with the `sha256:` prefix and 64 lowercase hexadecimal characters.

`PolicyRequest.request_hash` is computed over the canonical request payload excluding `request_hash`.

`PolicyDecision.input_hash` must equal the referenced `PolicyRequest.request_hash`.

`PolicyDecision.payload_hash` is computed over the canonical decision payload excluding `payload_hash` and `signatures`.

## PolicyRequest contents

The request carries:

- request identity and timestamp;
- requesting actor;
- subject actor;
- purpose;
- requested actions;
- requested resources;
- requested authority;
- requested sinks and forbidden sinks;
- requested restrictions;
- context and evidence references;
- canonical request hash.

Both `requesting_actor` and `subject_actor` are present because agentic systems often distinguish the principal asking from the subject on whose behalf an action is requested.

## PolicyDecision statuses

v0.1 statuses:

- `allow`
- `allow_with_constraints`
- `deny`
- `require_review`
- `quarantine`
- `revoke`

`deny`, `require_review`, `quarantine`, and `revoke` are first-class immutable decisions. Denial is not represented by absence.

## Revoke semantics

`revoke` is modeled as a new immutable decision that references the prior decision through `revokes_decision_ref`.

The prior decision is not mutated. Downstream consumers that need current-state validation must check the revocation index or decision registry. That registry check is a runtime concern and is not implemented in this contract repository.

## Restriction composition

Restrictions compose toward stricter posture.

A downstream `AdmissionToken` must carry at least the restrictions imposed by the `PolicyDecision`. It may add stricter restrictions, but it must not drop or weaken decision restrictions.

`allow` is an unconstrained grant and must not carry restrictions.

`allow_with_constraints` must carry at least one restriction.

## Reason codes

v0.1 reason codes:

- `purpose_bound_release`
- `do_not_learn_required`
- `do_not_link_required`
- `policy_violation`
- `authority_exceeded`
- `insufficient_evidence`
- `rate_limited`
- `human_review_required`
- `safety_quarantine`
- `revoked_by_authority`
- `unknown`

Non-grant decisions must include at least one reason code.

## Signatures and quorum

`PolicyDecision.signatures` is an array even though v0.1 requires only `min_signatures = 1`.

This keeps the shape compatible with future quorum admission without a flag-day migration.

v0.1 uses `hmac-sha256-test-v0.1` with `test-policy-key` as a deterministic reference signature only. Production successors must reject `*-test-*` algorithms in production verification mode.

## Validation

Run:

```bash
make validate-policy
```

or the full contract suite:

```bash
make validate
```

The validator checks:

- request schema;
- request hash;
- self-contradictory requested sinks;
- decision schema;
- decision binding to request hash;
- decision validity window;
- decision payload hash;
- signature quorum and signature value;
- grant/non-grant status semantics;
- non-grant reason-code requirement;
- constrained allow restriction requirement;
- revoke reference requirement;
- restriction/sink coherence.
