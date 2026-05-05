.PHONY: validate validate-workspace-operation

validate: validate-workspace-operation

validate-workspace-operation:
	python3 tools/validate_workspace_operation_examples.py
