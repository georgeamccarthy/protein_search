# .DEFAULT_GOAL := help
.PHONY: coverage deps testdeps lint test

coverage:  ## Run tests with coverage
	coverage erase
	coverage run -m pytest -ra
	coverage report -m

deps:  ## Install dependencies
	pip install --upgrade pip
	pip install -r requirements.txt

testdeps:
	pip install black coverage flake8 pytest

format:
	black backend tests

lint:  ## Lint
	flake8 backend teasts

test:  ## Run tests
	pytest -ra

build:
	make format
	make coverage