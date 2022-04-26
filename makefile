.ONESHELL:
SHELL:=/bin/bash

model-creation-tests:
	pytest --virtual-env-directory=./temp_venv --overwrite ./model_creation_tests

model-function-tests:
	pwd
	echo "break"
	ls -al
	echo "break"
	ls -al ./temp_venv
	echo "break"
	ls -al ./temp_venv/venv
	echo "break"
	ls -al ./temp_venv/venv/bin
	echo "break"
	source ./temp_venv/venv/bin/activate
	pytest ./model_function_tests
	deactivate

run-all-tests: model-creation-tests model-function-tests