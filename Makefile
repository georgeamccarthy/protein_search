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

# For building the docker compose
docker:
	docker-compose -f docker-compose.yml up --build

# For starting the docker comppose,
up:
	docker-compose -f docker-compose.yml up

## For removing containers
remove:
	docker-compose down --remove-orphans

# List all containers
ps:
	docker-compose ps -a
