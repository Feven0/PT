 .SILENT:  # Silences all commands
#    # Set V=1 for verbose output
#   ifeq ($(V),1)
#       QUIET :=
#   else
#       QUIET := @
#   endif

#   test:
#       $(QUIET) pytest

# Environment variables
SHELL := /bin/bash
PYTHON := python3
PYTHON_VERSION := 3.12
VENV := .venv
VENV_BIN := $(VENV)/bin

# Environment stages
ENV_STAGE ?= dev

# Set colors for output
BLUE=\033[0;34m
PINK=\033[0;35m
GREEN=\033[0;32m
YELLOW=\033[1;33m'
RED=\033[0;31m
NC=\033[0m

# Directories - Fix absolute paths
BACKEND_DIR = $(shell pwd)
SCRIPTS_DIR := $(BACKEND_DIR)/scripts
TEST_DIR = $(BACKEND_DIR)/tests
DOCS_DIR = $(BACKEND_DIR)/docs

# Test directory specification
PYTEST_ARGS ?=
#PYTEST_BASE_CMD := cd $(BACKEND_DIR) && PYTHONPATH=$(BACKEND_DIR) pytest
PYTEST_BASE_CMD := PYTHONPATH=$(BACKEND_DIR) pytest --import-mode=importlib

# Process management
SUPERVISOR_CONF := $(BACKEND_DIR)/supervisor.conf
PM2_CONFIG := $(BACKEND_DIR)/ecosystem.config.js

# Virtual environment activation
define activate_venv
	@if [ ! -d "$(VENV)" ]; then \
		echo -e "${YELLOW}Virtual environment not found. Creating one...${NC}"; \
		uv venv $(VENV) --python $(PYTHON_VERSION); \
	fi
	@echo -e "${GREEN}Activating virtual environment...${NC}"
	@source $(VENV_BIN)/activate || exit 1
endef

# Execute command in virtual environment
define run_in_venv	
	source $(VENV_BIN)/activate && \
	$1
endef
# echo -e ${GREEN}$(which python)${NC} && \
# echo -e ${GREEN}$(which pytest)${NC} && \

.PHONY: help
help: ## Show this help message
	@echo -e 'Usage: make [target]'
	@echo -e ''
	@echo -e 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.PHONY: check-env
check-env: ## Check if environment variables are set
	@if [ -z "$$AWS_ACCESS_KEY_ID" ] || [ -z "$$AWS_SECRET_ACCESS_KEY" ]; then \
		echo -e "AWS credentials not set. Please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY"; \
		exit 1; \
	fi

.PHONY: check-node
check-node: ## Check if Node.js and npm are installed
	@if ! command -v node > /dev/null; then \
		echo -e "Node.js is not installed. Please install Node.js first."; \
		exit 1; \
	fi
	@if ! command -v npm > /dev/null; then \
		echo -e "npm is not installed. Please install npm first."; \
		exit 1; \
	fi

.PHONY: install-pm2
install-pm2: check-node ## Install PM2 globally
	@if ! command -v pm2 > /dev/null; then \
		echo -e "Installing PM2 globally..."; \
		npm install -g pm2; \
	else \
		echo -e "PM2 is already installed"; \
	fi

.PHONY: setup-env
setup-env: check-env ## Set up environment (dev/test/prod)
	@echo -e "${BLUE}Setting up $(ENV_STAGE) environment...${NC}"	
	@chmod +x $(SCRIPTS_DIR)/setup_env.sh	
	$(call activate_venv)
	$(call run_in_venv,$(SCRIPTS_DIR)/setup_env.sh $(ENV_STAGE))

.PHONY: setup-dev
setup-dev: ## Set up development environment
	@echo -e "${PINK}Setting up dev environment...${NC}"
	$(call activate_venv)
	$(call run_in_venv,$(SCRIPTS_DIR)/setup_env.sh dev)

.PHONY: setup-test
setup-test: ## Set up test environment
	@echo -e "${PINK}Setting up test environment...${NC}"
	$(call activate_venv)
	$(call run_in_venv,$(SCRIPTS_DIR)/setup_env.sh test)
	@if [ ! -f "$(TEST_DIR)/.env.test" ]; then \
		echo -e "${YELLOW}Creating test environment file...${NC}"; \
		cp $(TEST_DIR)/.env.test.example $(TEST_DIR)/.env.test; \
	fi

.PHONY: setup-prod
setup-prod: install-pm2 ## Set up production environment
	@make setup-env ENV_STAGE=prod

.PHONY: generate-env
generate-env: ## Generate environment configuration
	@echo -e "${BLUE}Generating environment configuration for $(ENV_STAGE)...${NC}"
	$(call activate_venv)
	$(call run_in_venv,$(PYTHON) $(SCRIPTS_DIR)/generate_env.py --stage $(ENV_STAGE))

.PHONY: install-deps
install-deps: ## Install dependencies
	@echo -e "${BLUE}Installing dependencies...${NC}"
	$(call activate_venv)
	@if [ "$(ENV_STAGE)" = "dev" ]; then \
		$(call run_in_venv,uv pip install -r requirements.txt); \
	else \
		$(call run_in_venv,uv pip install -r requirements.txt); \
	fi

.PHONY: test
test: ## Run all tests with coverage
	@echo -e "${BLUE}Running all tests with coverage...${NC}"
	$(call activate_venv)
	$(call run_in_venv,$(PYTEST_BASE_CMD) \
		--cov=backend \
		--cov-report=term-missing \
		--cov-report=html:coverage \
		-v $(TEST_DIR))

.PHONY: test-unit
test-unit: ## Run unit tests
	@echo -e "${BLUE}Running unit tests...${NC}"
	$(call activate_venv)
	$(call run_in_venv,$(PYTEST_BASE_CMD) -v -m "unit" $(TEST_DIR))

.PHONY: test-integration
test-integration: ## Run integration tests
	@echo -e "${BLUE}Running integration tests...${NC}"
	$(call activate_venv)
	$(call run_in_venv,$(PYTEST_BASE_CMD) -v -m "integration" $(TEST_DIR))

.PHONY: test-api
test-api: ## Run API tests
	@echo -e "${BLUE}Running API tests...${NC}"
	$(call activate_venv)
	$(call run_in_venv,$(PYTEST_BASE_CMD) -v -m "api" $(TEST_DIR))

.PHONY: test-repository
test-repository: ## Run repository tests
	@echo -e "${BLUE}Running repository tests...${NC}"
	$(call activate_venv)
	$(call run_in_venv,$(PYTEST_BASE_CMD) -v -m "repository" $(TEST_DIR))

.PHONY: test-service
test-service: ## Run service tests
	@echo -e "${BLUE}Running service tests...${NC}"
	$(call activate_venv)
	$(call run_in_venv,$(PYTEST_BASE_CMD) -v -m "service" $(TEST_DIR))

.PHONY: test-infrastructure
test-infrastructure: ## Run infrastructure tests
	@echo -e "${BLUE}Running infrastructure tests...${NC}"
	$(call activate_venv)
	$(call run_in_venv,$(PYTEST_BASE_CMD) -v -m "infrastructure" $(TEST_DIR))

.PHONY: test-core
test-core: ## Run core tests
	@echo -e "${BLUE}Running core tests...${NC}"
	$(call activate_venv)
	$(call run_in_venv,$(PYTEST_BASE_CMD) -v -m "core" $(TEST_DIR))

.PHONY: test-coverage
test-coverage: ## Generate test coverage report
	@echo -e "${BLUE}Generating test coverage report...${NC}"
	$(call activate_venv)
	$(call run_in_venv, $(PYTEST_BASE_CMD) \
		--cov=backend \
		--cov-report=term-missing \
		--cov-report=html:coverage \
		--cov-report=xml:coverage/coverage.xml \
		-v $(TEST_DIR))

.PHONY: test-watch
test-watch: ## Run tests in watch mode
	@echo -e "${BLUE}Running tests in watch mode...${NC}"
	$(call activate_venv)
	$(call run_in_venv,ptw $(TEST_DIR) -- -v)

.PHONY: format
format: ## Format code
	@echo -e "${BLUE}Formatting code...${NC}"
	$(call activate_venv)
	$(call run_in_venv,black .)
	$(call run_in_venv,isort .)

.PHONY: lint
lint: ## Run linters
	@echo -e "${BLUE}Running linters...${NC}"
	$(call activate_venv)
	$(call run_in_venv,ruff check .)
	$(call run_in_venv,mypy .)
	$(call run_in_venv,pylint api core)

.PHONY: security
security: ## Run security checks
	@echo -e "${BLUE}Running security checks...${NC}"
	$(call activate_venv)
	$(call run_in_venv,bandit -r api core)
	$(call run_in_venv,safety check)

.PHONY: clean
clean: ## Clean up build artifacts
	@echo -e "${BLUE}Cleaning up...${NC}"
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name "*.pyo" -delete
	@find . -type f -name "*.pyd" -delete
	@find . -type f -name ".coverage" -delete
	@find . -type d -name "*.egg-info" -exec rm -rf {} +
	@find . -type d -name "*.egg" -exec rm -rf {} +
	@find . -type d -name ".pytest_cache" -exec rm -rf {} +
	@find . -type d -name ".mypy_cache" -exec rm -rf {} +
	@find . -type d -name ".ruff_cache" -exec rm -rf {} +
	@find . -type d -name "coverage" -exec rm -rf {} +
	@find . -type d -name "dist" -exec rm -rf {} +
	@find . -type d -name "build" -exec rm -rf {} +
	@find . -type d -name "htmlcov" -exec rm -rf {} +

.PHONY: docs
docs: ## Build documentation
	@echo -e "${BLUE}Building documentation...${NC}"
	$(call activate_venv)
	$(call run_in_venv,mkdocs build)

.PHONY: docs-serve
docs-serve: ## Serve documentation
	@echo -e "${BLUE}Serving documentation...${NC}"
	$(call activate_venv)
	$(call run_in_venv,mkdocs serve)

.PHONY: run
run: ## Run the application
	@echo -e "${BLUE}Running application in $(ENV_STAGE) mode...${NC}"
	$(call activate_venv)
	@if [ "$(ENV_STAGE)" = "prod" ]; then \
		source $(VENV_BIN)/activate && gunicorn app:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:9900 --lifespan on; \
	else \
		source $(VENV_BIN)/activate && uvicorn app:app --reload --host 0.0.0.0 --port 9900 --lifespan on; \
	fi

.PHONY: run-supervisor
run-supervisor: ## Run the application with supervisor
	@echo -e "${BLUE}Running application with supervisor...${NC}"
	$(call activate_venv)
	$(call run_in_venv,supervisord -c $(SUPERVISOR_CONF))

.PHONY: supervisor-status
supervisor-status: ## Check supervisor status
	$(call activate_venv)
	$(call run_in_venv,supervisorctl status)

.PHONY: supervisor-reload
supervisor-reload: ## Reload supervisor
	$(call activate_venv)
	$(call run_in_venv,supervisorctl reload)

.PHONY: run-pm2
run-pm2: install-pm2 ## Run the application with PM2
	@echo -e "${BLUE}Running application with PM2...${NC}"
	$(call activate_venv)
	$(call run_in_venv,pm2 start $(PM2_CONFIG))

.PHONY: pm2-status
pm2-status: ## Check PM2 status
	@pm2 status

.PHONY: pm2-logs
pm2-logs: ## View PM2 logs
	@pm2 logs

.PHONY: pm2-reload
pm2-reload: ## Reload PM2 processes
	@pm2 reload all

.PHONY: pm2-stop
pm2-stop: ## Stop PM2 processes
	@pm2 stop all

.PHONY: pm2-delete
pm2-delete: ## Delete PM2 processes
	@pm2 delete all

.PHONY: docker-build
docker-build: ## Build Docker image
	@echo -e "${BLUE}Building Docker image...${NC}"
	@docker build -t ipersona-backend:$(ENV_STAGE) .

.PHONY: docker-run
docker-run: ## Run Docker container
	@echo -e "${BLUE}Running Docker container...${NC}"
	@docker run -p 9900:9900 ipersona-backend:$(ENV_STAGE)

.PHONY: docker-compose
docker-compose: ## Run with Docker Compose
	@echo -e "${BLUE}Running with Docker Compose...${NC}"
	@docker-compose up -d

.PHONY: prisma-generate
prisma-generate: ## Generate Prisma client
	@echo -e "${BLUE}Generating Prisma client...${NC}"
	$(call activate_venv)
	$(call run_in_venv,prisma generate)

.PHONY: prisma-migrate
prisma-migrate: ## Run Prisma migrations
	@echo -e "${BLUE}Running Prisma migrations...${NC}"
	$(call activate_venv)
	$(call run_in_venv,prisma migrate dev)

.PHONY: prisma-reset
prisma-reset: ## Reset Prisma database
	@echo -e "${BLUE}Resetting Prisma database...${NC}"
	$(call activate_venv)
	$(call run_in_venv,prisma migrate reset)

.PHONY: all
all: setup-env install-deps prisma-generate test lint ## Set up everything and run tests 


.PHONY: test-clean
test-clean: ## Clean test artifacts
	@echo -e "${BLUE}Cleaning test artifacts...${NC}"
	@rm -rf .coverage
	@rm -rf coverage/
	@rm -rf .pytest_cache/
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete 

.PHONY: test-path
test-path: ## Test Python path resolution
	@echo -e "${BLUE}Testing Python path resolution...${NC}"
	@echo -e "${PINK}Backend directory: $(BACKEND_DIR)${NC}"
	$(call activate_venv)
	$(call run_in_venv,PYTHONPATH=$(BACKEND_DIR) $(PYTEST_BASE_CMD) $(TEST_DIR)/test_path_resolution.py -v -s)

.PHONY: test-app-health
test-app-health: ## Run app health tests (use PYTEST_ARGS="test_name" to run specific test)
	@echo -e "${BLUE}Running app health tests...${NC}"
	@echo -e "${PINK}Backend directory: $(BACKEND_DIR)${NC}"
	$(call activate_venv)
	$(call run_in_venv,PYTHONPATH=$(BACKEND_DIR) $(PYTEST_BASE_CMD) $(TEST_DIR)/test_app_health.py $(PYTEST_ARGS))

.PHONY: test-app-components
test-app-components: ## Run app component tests (use PYTEST_ARGS="test_name" to run specific test)
	@echo -e "${BLUE}Running app component tests...${NC}"
	@echo -e "${PINK}Backend directory: $(BACKEND_DIR)${NC}"
	$(call activate_venv)
	$(call run_in_venv,PYTHONPATH=$(BACKEND_DIR) $(PYTEST_BASE_CMD) $(TEST_DIR)/test_app_components.py $(PYTEST_ARGS)) 