.ONESHELL:
SHELL:=/bin/bash

.PHONY: test-clean
test-clean:
	@rm -rf ./temp_venv
	@rm -f ./.coverage

.PHONY: model-creation-tests
model-creation-tests: test-clean
	@uv run coverage run
	@uv run coverage report

.PHONY: model-function-tests
model-function-tests:
	source ./temp_venv/venv/bin/activate
	pytest ./model_function_tests
	deactivate

.PHONY: run-all-tests
run-all-tests: model-creation-tests model-function-tests


.PHONY: lint
lint:
	@echo "ISort:"
	@uv run isort pymusas_models model_function_tests model_creation_tests model_release.py
	@echo "Flake 8:"
	@uv run flake8 --config .flake8 pymusas_models model_function_tests model_creation_tests model_release.py
	@echo "MyPy:"
	@uv run mypy
	@echo "Linting finished"