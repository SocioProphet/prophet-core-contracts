.PHONY: validate validate-workspace-operation validate-regis validate-admission-token

validate: validate-workspace-operation validate-regis validate-admission-token

validate-workspace-operation:
	python3 tools/validate_workspace_operation_examples.py

validate-regis:
	python3 tools/validate_regis_examples.py

validate-admission-token:
	python3 tools/validate_admission_token_examples.py
	python3 tools/validate_admission_token_reference.py
