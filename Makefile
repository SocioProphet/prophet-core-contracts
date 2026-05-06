.PHONY: validate validate-workspace-operation validate-regis

validate: validate-workspace-operation validate-regis

validate-workspace-operation:
	python3 tools/validate_workspace_operation_examples.py

validate-regis:
	python3 tools/validate_regis_examples.py
