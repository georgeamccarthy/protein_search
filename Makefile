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
	black backend frontend tests

lint:  ## Lint
	flake8 backend frontend tests

test:  ## Run tests
	pytest -ra

build:
	make format
	make coverage

# For building the docker compose
docker:

	@ # Creating directory to store the models into
	@ mkdir -p backend/models

	@ # Creating directory to store the tokenizers into
	@ mkdir -p backend/tokenizers

	@ # Creating directory to store the data into
	@ mkdir -p backend/data

	@ # Creating directory to store the embeddings into
	@ mkdir -p backend/embeddings

	@ # Allow both the Docker container and local directory
	@ # to access contents
	@ # By default, only root on both container and host
	@ # machine can access the folders
	@ sudo chmod -R 777 backend/models
	@ sudo chmod -R 777 backend/tokenizers
	@ sudo chmod -R 777 backend/data
	@ sudo chmod -R 777 backend/embeddings

	docker-compose -f docker-compose.yml up --build

# For starting the docker compose,
up:
	docker-compose -f docker-compose.yml up

## For removing containers
remove:
	docker-compose down --remove-orphans

# List all containers
ps:
	docker-compose ps -a
