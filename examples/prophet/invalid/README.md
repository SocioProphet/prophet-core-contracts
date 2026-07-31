# Invalid ExecutionReceipt fixtures

These fixtures are intentionally invalid. `tools/validate_execution_receipt_examples.py`
asserts each one is rejected **at its intended layer** — a guard you cannot prove fired
is not a guard. The schema is `additionalProperties: false`, so the rationale lives here
rather than inline in each fixture.

| Fixture | Layer | What it violates |
|---|---|---|
| `bad-receipt-hash.json` | schema | `receipt_hash` does not match `^sha256:...`. |
| `used-not-subset.json` | semantic (INV1) | `capabilities_used` contains a capability not in `capabilities_held`. |
| `verified-not-replayable.json` | semantic (INV2) | `verdict.state = verified` but `proof_artifact.replayable = false` (verify the artifact, not the command). |
| `block-not-denied.json` | semantic (INV3) | `decision.verdict = block` but `verdict.state = verified` (a blocked run must be denied). |

A "semantic" fixture must be **schema-valid** yet fail a semantic invariant; if it fails
schema first, the semantic guard was never exercised and the validator flags it as a leak.
