.PHONY: validate validate-workspace-operation validate-regis validate-policy

validate: validate-workspace-operation validate-regis validate-policy

validate-workspace-operation:
	python3 tools/validate_workspace_operation_examples.py

validate-regis:
	python3 tools/validate_regis_examples.py

validate-policy:
	python3 tools/validate_policy_examples.py
	python3 tools/validate_policy_risk_tier_examples.py
