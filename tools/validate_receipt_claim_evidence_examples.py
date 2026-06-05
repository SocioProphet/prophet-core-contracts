#!/usr/bin/env python3
"""Validate receipt, claim, and evidence-thread examples."""

import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "schemas"
EXAMPLES = ROOT / "examples" / "prophet"

PAIRS = {
    "action-receipt-completed.json": "action-receipt.schema.json",
    "claim-record-observation.json": "claim-record.schema.json",
    "evidence-thread-workspace-operation.json": "evidence-thread.schema.json",
}


def load_json(path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def validate_pair(example_name, schema_name):
    schema = load_json(SCHEMAS / schema_name)
    example = load_json(EXAMPLES / example_name)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(example)
    return example


examples = {name: validate_pair(name, schema) for name, schema in PAIRS.items()}
receipt = examples["action-receipt-completed.json"]
claim = examples["claim-record-observation.json"]
thread = examples["evidence-thread-workspace-operation.json"]

if receipt["receipt_id"] not in claim.get("receipt_ids", []):
    raise SystemExit("claim must reference action receipt")
if receipt["operation_id"] not in claim.get("operation_ids", []):
    raise SystemExit("claim must reference operation id")
if receipt["capability_id"] not in claim.get("capability_ids", []):
    raise SystemExit("claim must reference capability id")
if thread["claim_id"] != claim["claim_id"]:
    raise SystemExit("evidence thread claim_id must match claim")
thread_evidence_ids = {item["evidence_id"] for item in thread["evidence_items"]}
for evidence_id in claim["evidence_ids"]:
    if evidence_id not in thread_evidence_ids and evidence_id.startswith("receipt_"):
        raise SystemExit(f"claim receipt evidence missing from thread: {evidence_id}")

print("Receipt, claim, and evidence examples passed")
