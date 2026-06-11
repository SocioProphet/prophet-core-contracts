# AdmissionToken v0.1

`AdmissionToken` is the Operation Plane proof that a proposed action was admitted by policy and authority gates before execution, graph materialization, learning, linking, or other side effects.

## Purpose

The primary invariant is:

```text
No canonical mutation or side effect is valid unless it references an AdmissionToken produced by the Operation Plane.
```

A schema-valid artifact is not sufficient. Admission is a separate control object.

## Scope

v0.1 defines a single-use token only. Multi-use tokens are intentionally deferred because they require replay accounting, lease refresh, and broader consumption tracking.

A single-use token is bound to one admitted action and one admitted resource. v0.1 assumes the consumer set for a token is effectively one side-effecting consumer for that action/resource pair. Cross-consumer single-use enforcement requires a consumed-token registry; that registry is a production Operation Plane concern and is not implemented in this contract repository.

## Producers and consumers

| Object | Producer | Consumer |
|---|---|---|
| `ActionProposal` | agent, UI, runtime, or system | Operation Plane |
| `PolicyDecision` | Policy Fabric | Operation Plane |
| `AuthorityDecision` | Agent Registry / HolographMe delegation | Operation Plane |
| `AdmissionToken` | Operation Plane only | AgentPlane, Regis, HolographMe, other side-effecting runtimes |
| `RuntimeReceipt` | AgentPlane / runtime | ledger, Regis, SocioSphere |

## Token contents

Minimum v0.1 fields:

- token identity and issuer;
- issue and expiry timestamps;
- single-use status;
- proposed action reference;
- policy decision reference;
- authority decision reference;
- sink restrictions including `DoNotLearn`, `DoNotLink`, and `NoRawTwinExport`;
- allowed operation and resource;
- evidence references;
- nonce;
- payload hash;
- test signature.

## Verification rule

Consumers must verify:

1. schema validation passes;
2. token status is `issued`;
3. token is not expired beyond clock-skew allowance;
4. token is not used before `issued_at` beyond clock-skew allowance;
5. payload hash matches canonical token payload;
6. signature profile and value match the v0.1 test signing rule;
7. requested action type matches the admitted action;
8. requested resource matches the admitted resource;
9. requested authority does not exceed the token authority;
10. requested sink is allowed;
11. requested sink does not violate `DoNotLearn` or `DoNotLink` restrictions.

## Clock skew

v0.1 allows 60 seconds of clock skew on `issued_at` and `expires_at`.

A consumer may accept a token no earlier than:

```text
issued_at - 60 seconds
```

and no later than:

```text
expires_at + 60 seconds
```

This allowance is for distributed clock drift only. It is not a lease extension mechanism.

## Signing posture

v0.1 uses `hmac-sha256-test-v0.1` with `test-admission-key` as a deterministic reference signature. This is not production key management.

Production successors must reject `*-test-*` algorithms in production verification mode, even if a test HMAC verifies. Production profiles should replace this with a real Operation Plane signing profile, such as asymmetric signatures or a managed verification service.

## Payload hash

`payload_hash` is SHA-256 over the canonical JSON token payload excluding `payload_hash` and `signature`.

The validator uses:

```python
json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
```

## Python reference type

`reference/admission_token.py` provides a frozen, slotted dataclass with `init=False`.

Direct construction raises `TypeError`:

```python
AdmissionToken()
```

The only valid construction path is:

```python
AdmissionToken.from_admission(...)
```

Pickle-style reconstruction is also blocked through `__reduce__`; this prevents pickle/deepcopy from becoming a second public construction channel in the reference type.

The type exposes:

- `to_dict()` for schema-shaped serialization;
- `compute_payload_hash()` for deterministic hash calculation;
- `verify(request, now=...)` for consumer-side checks.

## Negative fixtures

Negative fixtures cover:

- schema-only failure before semantic or crypto checks;
- expired token;
- missing policy decision;
- action mismatch;
- invalid signature;
- payload-hash tampering;
- consumed-token replay;
- authority ceiling violation;
- forbidden sink under `DoNotLearn` / sink restrictions.

Each fixture declares `expected_failure`, and the validator requires that specific failure code to appear.

## v0.2 candidates

- Production signing profile, likely asymmetric.
- Multi-use tokens with explicit use-count and use-count-limit.
- Quorum-signed admissions for high-authority actions.
- Attenuated delegation tokens where token B is strictly weaker than token A.
- Shared consumed-token registry semantics for cross-consumer replay prevention.
- Boundary fixtures around clock-skew edges.

## Validation

Run:

```bash
make validate-admission-token
```

or the full contract suite:

```bash
make validate
```
