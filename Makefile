#################################################################################
# GLOBALS                                                                       #
#################################################################################

PROJECT_DIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
VIRTUALENV_DIR := "env"
PYTHON_INTERPRETER = python3

#################################################################################
# SETUP                                                                         #
#################################################################################

## Set up python interpreter environment 
create_environment:
	$(PYTHON_INTERPRETER) -m venv $(VIRTUALENV_DIR)
	@echo ">>> New virtualenv created. Activate with:\nsource $(VIRTUALENV_DIR)/bin/activate"

## Install Python Dependencies for application
install:
	$(PYTHON_INTERPRETER) -m pip install -U pip setuptools wheel
	$(PYTHON_INTERPRETER) -m pip install -r requirements.txt

.PHONY: create_environment requirements

#################################################################################
# DEVELOPMENT COMMANDS                                                          #
#################################################################################

## Delete all compiled Python files

clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete

## Format using Black
format: 
	isort src tests --profile black
	black src tests

## Lint using flake8
lint:
	flake8 src

## Run tests using pytest
test:
	pytest tests/

.PHONY: clean format lint test