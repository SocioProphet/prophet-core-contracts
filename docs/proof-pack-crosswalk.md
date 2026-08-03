# ProofPack crosswalk — one canonical contract, five existing implementations

The estate grew ~5 parallel proof/ledger/attestation surfaces. `schemas/proof-pack.schema.json`
(+ `schemas/claim-ledger-entry.schema.json`) is now the **canonical** contract; this crosswalk maps
each existing implementation onto it so consumers can migrate **incrementally** (one PR each) rather
than in a risky simultaneous refactor. No consumer is changed by this PR — it defines the target.

## Canonical fields (ProofPack v0.1.0)
`proof_pack_id` (content-addressed) · `subject_ref` · `claim_mode` (formal_construction | illustrative |
fixture_validated | experimental | independently_reproduced | audited — never mixed silently) ·
`epistemic_level` (rejected<speculative<synthetic<empirical<bounded<proved) · `ledger` {algo, head, prior?}
· `checks[]` · `witnesses[]` · `evidence_refs[]` · `signatures[]` · `provenance`.
`ClaimLedgerEntry` is the append-only recursion unit: `digest = H(state_hash ‖ prior_digest)`.

## Crosswalk

| Estate implementation | Its shape | → canonical mapping | Notes / gap on migration |
|---|---|---|---|
| **identity-is-prime-reference** `ProofArtifact` (`proofs.py`) | `status` (PROVED/VIOLATION/INCONCLUSIVE) + `violations[]` + sha256 | `status`→`claim_mode`/`epistemic_level` (PROVED→proved/audited; VIOLATION→rejected; INCONCLUSIVE→speculative); `violations[]`→`checks[]` (passed=false); sha256→`ledger.head` (algo sha256) | add `subject_ref`, `signatures[]` |
| **ProCybernetica** lawful-learning `ledger.schema.json` (`H_t` recursion) | append-only `H_t = SHA256(θ‖Θ‖…‖H_{t-1})` + claim-mode labels | one `ClaimLedgerEntry` per epoch (algo sha256; `prior_digest`=H_{t-1}; `digest`=H_t); run-level `ProofPack.ledger.head`=final H_t; claim-mode label→`claim_mode` | closest structural match; direct |
| **synapseiq** `intell-agency/proof-pack.ts` | `{policyFingerprint, checks{iri,gci,tci,dpBudget}, witnesses[], signatures[], merkleRoot}` | `merkleRoot`→`ledger.head` (algo sha256); `checks`→`checks[]`; `witnesses`→`witnesses[]`; `signatures`→`signatures[]`; `policyFingerprint`→`provenance.policy_fingerprint` | add `epistemic_level`, `claim_mode` |
| **Noetica** `agent-machine/dispatch-ledger.ts` | dispatch hash-chain (Truth=Law×Evidence) | each dispatch→`ClaimLedgerEntry`; chain head→`ProofPack.ledger.head` | map dispatch verdict→`epistemic_level` |
| **meshrush / sp-attest** compile-attestation | content-addressed (blake2b) attestation {epistemic_level, gates[], boundary} | `attestation_id`→`proof_pack_id`; `epistemic_level`→`epistemic_level`; `gates`→`checks`; blake2b hash→`ledger.head` (algo blake2b) | add explicit `claim_mode` (compile ⇒ fixture_validated/formal_construction) + `signatures[]` |

## Migration order (low-risk, one PR per consumer)
1. **meshrush/sp-attest** (already content-addressed + epistemic) — thinnest delta.
2. **synapseiq proof-pack** (already has checks/witnesses/signatures/merkleRoot).
3. **ProCybernetica ledger** (direct structural match).
4. **identity-is-prime ProofArtifact** (map status→claim_mode/epistemic).
5. **Noetica dispatch-ledger** (map verdict→epistemic).

Each migration = emit/accept the canonical shape at the seam while keeping the internal type; validate
against `proof-pack.schema.json`. The `Truth = Law × Evidence` contract (Noetica) is unchanged — this
gives it one carrier.
