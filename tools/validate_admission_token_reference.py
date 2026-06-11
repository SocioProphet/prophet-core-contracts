#!/usr/bin/env python3
"""Validate the AdmissionToken reference Python type."""

from __future__ import annotations

import copy
import pickle
import sys
import os
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from reference.admission_token import AdmissionToken


def main() -> int:
    try:
        AdmissionToken()  # type: ignore[call-arg]
    except TypeError:
        pass
    else:
        raise AssertionError("AdmissionToken direct construction unexpectedly succeeded")

    token = AdmissionToken.from_admission(
        token_id="adm_reference_001",
        issuer_id="operation_plane_local_001",
        issued_at="2026-05-12T04:00:00Z",
        expires_at="2026-05-12T04:15:00Z",
        proposed_action_ref={
            "action_id": "act_regis_ingest_tpf_001",
            "action_type": "regis.graph_delta.ingest",
            "target_ref": "regis:graph:semantic-feature-plane",
            "operation_ref": "op_holographme_regis_export_001",
        },
        policy_decision_ref={
            "decision_id": "pd_regis_ingest_tpf_001",
            "decision_result": "allow_with_constraints",
            "policy_bundle_hash": "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            "reason_codes": ["purpose_bound_release", "do_not_learn_required", "do_not_link_required"],
        },
        authority_decision_ref={
            "decision_id": "ad_auth_holographme_regis_001",
            "decision_result": "allow",
            "effective_authority_band": "recommend",
            "actor_id": "agent_exporter_001",
            "subject_id": "sub_example_001",
        },
        sink_restrictions={
            "do_not_learn": True,
            "do_not_link": True,
            "no_raw_twin_export": True,
            "allowed_sinks": ["regis.graph_materialization"],
            "forbidden_sinks": ["model_training", "embedding_generation", "durable_memory", "analytics_warehouse", "cross_domain_identity_linking"],
        },
        allowed_operation={
            "operation_type": "regis.graph_delta.ingest",
            "resource_ref": "regis:graph:semantic-feature-plane",
            "max_authority_band": "recommend",
            "single_use": True,
        },
        evidence_refs=("tpf_proj_mission_fit_001_capability_claims_capability", "tr_projection_001", "pdl_projection_001"),
        nonce="adm_nonce_reference_001",
    )

    for bypass_name, bypass in [("pickle", lambda: pickle.dumps(token)), ("deepcopy", lambda: copy.deepcopy(token))]:
        try:
            bypass()
        except TypeError:
            pass
        else:
            raise AssertionError(f"AdmissionToken {bypass_name} bypass unexpectedly succeeded")

    allowed_request = {
        "action_type": "regis.graph_delta.ingest",
        "resource_ref": "regis:graph:semantic-feature-plane",
        "authority_band": "recommend",
        "sink": "regis.graph_materialization",
    }
    now = datetime(2026, 5, 12, 4, 5, tzinfo=timezone.utc)
    if not token.verify(allowed_request, now=now):
        raise AssertionError("AdmissionToken reference verify failed for allowed request")

    forbidden_sink = dict(allowed_request)
    forbidden_sink["sink"] = "embedding_generation"
    if token.verify(forbidden_sink, now=now):
        raise AssertionError("AdmissionToken reference verify allowed forbidden sink")

    excessive_authority = dict(allowed_request)
    excessive_authority["authority_band"] = "commit"
    if token.verify(excessive_authority, now=now):
        raise AssertionError("AdmissionToken reference verify allowed excessive authority")

    within_skew = datetime(2026, 5, 12, 4, 15, 30, tzinfo=timezone.utc)
    if not token.verify(allowed_request, now=within_skew):
        raise AssertionError("AdmissionToken reference verify rejected token inside clock-skew allowance")

    expired_time = datetime(2026, 5, 12, 4, 16, 1, tzinfo=timezone.utc)
    if token.verify(allowed_request, now=expired_time):
        raise AssertionError("AdmissionToken reference verify allowed expired token beyond clock-skew allowance")

    print("AdmissionToken reference validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
