.PHONY: validate validate-workspace-operation validate-regis validate-scoped-capability validate-prophet-records validate-value-claims validate-health-ai-contracts validate-decision-world-signals validate-admission-token validate-policy validate-integration validate-audit-record validate-release-manifest

validate: validate-workspace-operation validate-regis validate-scoped-capability validate-prophet-records validate-value-claims validate-health-ai-contracts validate-decision-world-signals validate-admission-token validate-policy validate-integration validate-audit-record validate-release-manifest

validate-workspace-operation:
	python3 tools/validate_workspace_operation_examples.py

validate-regis:
	python3 tools/validate_regis_examples.py

validate-scoped-capability:
	python3 tools/validate_scoped_capability_example.py

validate-prophet-records:
	python3 tools/validate_prophet_record_examples.py

validate-value-claims:
	python3 tools/validate_value_claim_examples.py

validate-health-ai-contracts:
	python3 tools/validate_health_ai_contracts.py

validate-decision-world-signals:
	python3 tools/validate_decision_world_signal_examples.py

validate-admission-token:
	python3 tools/validate_admission_token_examples.py
	python3 tools/validate_admission_token_reference.py

validate-policy:
	python3 tools/validate_policy_examples.py
	python3 tools/validate_policy_risk_tier_examples.py

validate-integration:
	python3 tools/validate_admission_chain_examples.py

validate-audit-record:
	python3 tools/validate_audit_record_examples.py

validate-release-manifest:
	python3 tools/validate_release_manifest_examples.py

