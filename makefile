.ONESHELL:
SHELL:=/bin/bash

model-creation-tests:
	pytest --virtual-env-directory=./temp_venv --overwrite ./model_creation_tests

model-function-tests:
	source ./temp_venv/venv/bin/activate
	pytest ./model_function_tests
	deactivate

run-all-tests: model-creation-tests model-function-tests