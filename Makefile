###############################################################################
# Tenx iPersona - Makefile (modeled after tenx_parrot)                        #
###############################################################################

.SILENT:

# Environment
SHELL := /bin/bash
PYTHON := python3
PYTHON_VERSION := 3.12
VENV := .venv
VENV_BIN := $(VENV)/bin

# uv (Python package/dependency manager)
UV_BIN := $(shell command -v uv 2>/dev/null || echo "")

# Stage
ENV_STAGE ?= dev

# Colors
BLUE=\033[0;34m
PINK=\033[0;35m
GREEN=\033[0;32m
YELLOW=\033[1;33m
RED=\033[0;31m
NC=\033[0m

# Directories
BACKEND_DIR = $(shell pwd)
SCRIPTS_DIR := $(BACKEND_DIR)/scripts
FRONTEND_DIR := $(BACKEND_DIR)/frontend
TEST_DIR = $(BACKEND_DIR)/tests

# Pytest
CMD ?=
PYTEST_ARGS ?=
PYTEST_BASE_CMD := PYTHONPATH=$(BACKEND_DIR) pytest --import-mode=importlib

# Venv helpers (use uv as per project convention)
define activate_venv
	@if [ ! -d "$(VENV)" ]; then \
		echo -e "${YELLOW}Virtual environment not found. Creating one...${NC}"; \
		if ! command -v uv >/dev/null 2>&1; then \
			echo -e "${BLUE}uv not found. Installing uv system-wide (user space)...${NC}"; \
			curl -LsSf https://astral.sh/uv/install.sh | sh; \
			export PATH="$$HOME/.local/bin:$$PATH"; \
		fi; \
		uv venv $(VENV) --python $(PYTHON_VERSION); \
	fi
	@echo -e "${GREEN}Activating virtual environment...${NC}"
	@source $(VENV_BIN)/activate || exit 1
endef

define run_in_venv
	source $(VENV_BIN)/activate && \
	$1
endef

.PHONY: help uv-install uv-version install-deps test test-unit test-integration test-watch test-coverage \
        format lint security clean run \
        workers work start-backend start-frontend generate-env setup-env setup-backend setup-frontend setup runpy

help: ## Show this help message
	@echo -e 'Usage: make [target]'
	@echo -e ''
	@echo -e 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

uv-install: ## Install uv (Python package manager) system-wide for current user
	@if command -v uv >/dev/null 2>&1; then \
		echo -e "${GREEN}uv is already installed at: $(UV_BIN)${NC}"; \
	else \
		echo -e "${BLUE}Installing uv...${NC}"; \
		curl -LsSf https://astral.sh/uv/install.sh | sh; \
		echo -e "${YELLOW}If uv is not found, add $$HOME/.local/bin to your PATH:${NC}"; \
		echo '  export PATH="$$HOME/.local/bin:$$PATH"'; \
	fi

uv-version: ## Print uv version (if installed)
	@command -v uv >/dev/null 2>&1 && uv --version || echo -e "${RED}uv is not installed${NC}"

install-deps: ## Install dependencies (uv)
	@echo -e "${BLUE}Installing dependencies...${NC}"
	$(call activate_venv)
	$(call run_in_venv,uv pip install -r requirements.txt)

test: ## Run tests (if any)
	@echo -e "${BLUE}Running tests...${NC}"
	$(call activate_venv)
	$(call run_in_venv,$(PYTEST_BASE_CMD) -v $(TEST_DIR) $(PYTEST_ARGS))

test-unit: ## Run unit tests
	@echo -e "${BLUE}Running unit tests...${NC}"
	$(call activate_venv)
	$(call run_in_venv,$(PYTEST_BASE_CMD) -v -m "unit" $(TEST_DIR))

test-integration: ## Run integration tests
	@echo -e "${BLUE}Running integration tests...${NC}"
	$(call activate_venv)
	$(call run_in_venv,$(PYTEST_BASE_CMD) -v -m "integration" $(TEST_DIR))

test-watch: ## Run tests in watch mode
	@echo -e "${BLUE}Running tests in watch mode...${NC}"
	$(call activate_venv)
	$(call run_in_venv,ptw $(TEST_DIR) -- -v)

test-coverage: ## Generate coverage report
	@echo -e "${BLUE}Generating coverage report...${NC}"
	$(call activate_venv)
	$(call run_in_venv,$(PYTEST_BASE_CMD) \
		--cov=api \
		--cov-report=term-missing \
		--cov-report=html:coverage \
		--cov-report=xml:coverage/coverage.xml \
		-v $(TEST_DIR))

format: ## Format code
	@echo -e "${BLUE}Formatting code...${NC}"
	$(call activate_venv)
	$(call run_in_venv,black .)
	$(call run_in_venv,isort .)

lint: ## Run linters
	@echo -e "${BLUE}Running linters...${NC}"
	$(call activate_venv)
	$(call run_in_venv,ruff check .)
	$(call run_in_venv,mypy .)

security: ## Run security checks
	@echo -e "${BLUE}Running security checks...${NC}"
	$(call activate_venv)
	$(call run_in_venv,bandit -r api)
	$(call run_in_venv,safety check)

clean: ## Clean build/test artifacts
	@echo -e "${BLUE}Cleaning up...${NC}"
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name "*.pyo" -delete
	@find . -type f -name ".coverage" -delete
	@find . -type d -name ".pytest_cache" -exec rm -rf {} +
	@find . -type d -name ".mypy_cache" -exec rm -rf {} +
	@find . -type d -name ".ruff_cache" -exec rm -rf {} +
	@find . -type d -name "coverage" -exec rm -rf {} +

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

# ---------------------- Environment ----------------------

.PHONY: generate-env
generate-env: ## Generate environment configuration
	@echo -e "${BLUE}Generating environment configuration for $(ENV_STAGE)...${NC}"
	$(call activate_venv)
	$(call run_in_venv,$(PYTHON) $(SCRIPTS_DIR)/generate_env.py --stage $(ENV_STAGE))

# ---------------------- Setup ----------------------

.PHONY: setup-env
setup-env: ## Set up environment (dev/test/prod)
	@echo -e "${BLUE}Setting up $(ENV_STAGE) environment...${NC}"
	$(call activate_venv)
	@echo -e "${GREEN}Python venv ready for $(ENV_STAGE).${NC}"

.PHONY: setup-backend
setup-backend: ## Setup backend Python deps
	@echo -e "${BLUE}Setting up backend...${NC}"
	$(call activate_venv)
	$(call run_in_venv,uv pip install -r api/requirements.txt)

.PHONY: setup-frontend
setup-frontend: check-node ## Setup frontend Node deps
	@echo -e "${BLUE}Setting up frontend...${NC}"
	@cd $(FRONTEND_DIR) && \
	if command -v pnpm > /dev/null && [ -f "pnpm-lock.yaml" ]; then \
		echo "Using pnpm with frozen lockfile"; \
		pnpm install --frozen-lockfile; \
	elif [ -f "package-lock.json" ]; then \
		echo "Using npm ci (lockfile detected)"; \
		npm ci --no-audit --no-fund; \
	else \
		echo "Using npm install (no lockfile)"; \
		npm install --no-audit --no-fund; \
	fi

.PHONY: setup
setup: setup-backend setup-frontend ## Setup both backend and frontend

# ---------------------- Start ----------------------
.PHONY: runpy
runpy: ## Run FastAPI app (ENV_STAGE=prod for gunicorn)
	@echo -e "${BLUE}Run a command in backend...${NC}"
	$(call activate_venv)
	source $(VENV_BIN)/activate && python ${CMD}; 

start-backend: ## Run FastAPI app (ENV_STAGE=prod for gunicorn)
	@echo -e "${BLUE}Running application in $(ENV_STAGE) mode...${NC}"
	$(call activate_venv)
	source $(VENV_BIN)/activate && uvicorn app:app --reload --host 0.0.0.0 --port 9990 --lifespan on; 
	
start-frontend: ## Run frontend app
	@echo -e "${BLUE}Running frontend application...${NC}"
	@cd $(FRONTEND_DIR) && npm run dev


# ---------------------- Celery (local legacy) ----------------------

workers: ## Start Celery worker via explicit path (legacy)
	@echo "Starting Celery worker (stdout logs; parrot env)..."
	@PYTHONPATH=/home/rehmet/tenx_ipersona /opt/miniconda/envs/parrot/bin/celery -A api.services.celery.celery_worker:celery_app worker -l info

work: ## Kill Celery processes locally and start worker (legacy)
	@echo "🔥 Killing all running Celery processes..."
	@echo "==========================================="
	@echo ""
	@echo "3️⃣ Killing local Celery processes..."
	@ps aux | grep -E 'celery.*worker' | grep -v grep | grep -v "make work" | awk '{print $$2}' | xargs -r kill -TERM 2>/dev/null || echo "   ℹ️ No local Celery worker processes found"
	@ps aux | grep -E 'celery.*beat' | grep -v grep | grep -v "make work" | awk '{print $$2}' | xargs -r kill -TERM 2>/dev/null || echo "   ℹ️ No local Celery beat processes found"
	@ps aux | grep -E 'celery.*flower' | grep -v grep | grep -v "make work" | awk '{print $$2}' | xargs -r kill -TERM 2>/dev/null || echo "   ℹ️ No local Celery flower processes found"
	@echo ""
	@echo "4️⃣ Force killing any remaining stubborn processes..."
	@ps aux | grep -E 'python.*celery' | grep -v grep | grep -v "make work" | awk '{print $$2}' | xargs -r kill -9 2>/dev/null || echo "   ℹ️ No remaining Python Celery processes found"
	@echo ""
	@echo "⏳ Waiting 2 seconds for processes to fully terminate..."
	@sleep 2
	@echo ""
	@echo "✅ All Celery processes terminated!"
	@echo ""
	@echo "🚀 Starting Celery worker with logs..."
	@echo "======================================"
	@PYTHONPATH=/home/rehmet/tenx_ipersona /opt/miniconda/envs/parrot/bin/celery -A api.services.celery.celery_worker:celery_app worker -l info

