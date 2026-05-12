.PHONY: validate validate-workspace-operation validate-regis validate-release-manifest

validate: validate-workspace-operation validate-regis validate-release-manifest

validate-workspace-operation:
	python3 tools/validate_workspace_operation_examples.py

validate-regis:
	python3 tools/validate_regis_examples.py

validate-release-manifest:
	python3 tools/validate_release_manifest_examples.py
