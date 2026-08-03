#!/usr/bin/env python3
"""Validate the canonical ProofPack + ClaimLedgerEntry examples and their cross-consistency.

Beyond schema validation: a ProofPack's ledger.head MUST equal the paired ledger entry's digest
(the pack points at a real ledger head), and the genesis entry's digest MUST equal
H(state_hash || prior_digest) under its declared algo (the recursion is real, not asserted).
"""
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "schemas"
EXAMPLES = ROOT / "examples" / "prophet"

PAIRS = {
    "proof-pack.example.json": "proof-pack.schema.json",
    "claim-ledger-entry.example.json": "claim-ledger-entry.schema.json",
}

_HASH = {"sha256": hashlib.sha256}


def load(path):
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def main() -> int:
    docs = {}
    for example_name, schema_name in PAIRS.items():
        schema = load(SCHEMAS / schema_name)
        doc = load(EXAMPLES / example_name)
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(doc)
        docs[example_name] = doc

    pack = docs["proof-pack.example.json"]
    entry = docs["claim-ledger-entry.example.json"]

    # 1. the pack points at a real ledger head
    if pack["ledger"]["head"] != entry["digest"]:
        raise SystemExit("proof-pack ledger.head must equal the ledger entry digest")
    if pack["ledger"]["algo"] != entry["algo"]:
        raise SystemExit("proof-pack ledger.algo must match the ledger entry algo")

    # 2. the recursion is real: digest == H(state_hash || prior_digest)
    algo = entry["algo"]
    if algo not in _HASH:
        raise SystemExit(f"example uses unverified algo {algo!r}; extend _HASH to check it")
    prior = entry["prior_digest"] or ""
    recomputed = _HASH[algo]((entry["state_hash"] + prior).encode()).hexdigest()
    if recomputed != entry["digest"]:
        raise SystemExit("ledger entry digest does not equal H(state_hash || prior_digest)")

    # 3. claim_mode consistency (never silently mixed)
    if pack["claim_mode"] != entry["claim_mode"]:
        raise SystemExit("proof-pack and its ledger entry must share a claim_mode")

    print("OK: canonical ProofPack + ClaimLedgerEntry examples validate (schema + head + recursion + claim_mode)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
