.PHONY: validate validate-workspace-operation validate-regis validate-integration

validate: validate-workspace-operation validate-regis validate-integration

validate-workspace-operation:
	python3 tools/validate_workspace_operation_examples.py

validate-regis:
	python3 tools/validate_regis_examples.py

validate-integration:
	python3 tools/validate_admission_chain_examples.py
