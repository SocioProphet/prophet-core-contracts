.PHONY: validate validate-workspace-operation validate-decision-world-signals

validate: validate-workspace-operation validate-decision-world-signals

validate-workspace-operation:
	python3 tools/validate_workspace_operation_examples.py

validate-decision-world-signals:
	python3 tools/validate_decision_world_signal_examples.py
