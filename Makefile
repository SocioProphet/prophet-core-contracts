.PHONY: validate validate-workspace-operation validate-regis validate-scoped-capability validate-prophet-records

validate: validate-workspace-operation validate-regis validate-scoped-capability validate-prophet-records

validate-workspace-operation:
	python3 tools/validate_workspace_operation_examples.py

validate-regis:
	python3 tools/validate_regis_examples.py

validate-scoped-capability:
	python3 tools/validate_scoped_capability_example.py

validate-prophet-records:
	python3 tools/validate_prophet_record_examples.py
