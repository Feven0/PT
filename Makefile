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
PYTEST_ARGS ?=
PYTEST_BASE_CMD := PYTHONPATH=$(BACKEND_DIR) pytest --import-mode=importlib

# Venv helpers (use uv as per project convention)
define activate_venv
	@if [ ! -d "$(VENV)" ]; then \
		echo -e "${YELLOW}Virtual environment not found. Creating one...${NC}"; \
		uv venv $(VENV) --python $(PYTHON_VERSION); \
	fi
	@echo -e "${GREEN}Activating virtual environment...${NC}"
	@source $(VENV_BIN)/activate || exit 1
endef

define run_in_venv
	source $(VENV_BIN)/activate && \
	$1
endef

.PHONY: help install-deps test test-unit test-integration test-watch test-coverage \
        format lint security clean run docker-compose docker-build docker-run \
        celery-start celery-stop celery-restart celery-status celery-monitor \
        celery-flower worker flower celery-purge celery-logs celery celery-clean \
        dev-start prod-start stop-all logs-all restart-all workers flower-build \
        flower-run flower-logs flower-stop work

help: ## Show this help message
	@echo -e 'Usage: make [target]'
	@echo -e ''
	@echo -e 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

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

start-backend: ## Run FastAPI app (ENV_STAGE=prod for gunicorn)
	@echo -e "${BLUE}Running application in $(ENV_STAGE) mode...${NC}"
	$(call activate_venv)
	source $(VENV_BIN)/activate && uvicorn app:app --reload --host 0.0.0.0 --port 9990 --lifespan on; 
	
start-frontend: ## Run frontend app
	@echo -e "${BLUE}Running frontend application...${NC}"
	@cd $(FRONTEND_DIR) && npm run dev


# ---------------------- Docker ----------------------

docker-build: ## Build project docker images
	@echo -e "${BLUE}Building Docker images...${NC}"
	@./build.sh


# ---------------------- Celery (Component) ----------------------

build-celery: ## Build Celery-related images/scripts
	@echo "Building all Docker images (including Celery)..."
	@./build.sh
	@echo "All Docker images built successfully!"

celery-start: ## Start Celery worker (docker-compose)
	@echo "Starting Celery worker (Docker)..."
	docker-compose up -d celery_worker
	@echo "Celery worker started successfully!"

celery-start-bg: ## Start Celery worker in background
	@echo "Starting Celery worker in background (Docker)..."
	docker-compose up -d celery_worker
	@echo "Celery worker started in background!"

celery-stop: ## Stop Celery worker
	@echo "Stopping Celery worker (Docker)..."
	docker-compose stop celery_worker
	@echo "Celery worker stopped!"

celery-restart: ## Restart Celery worker
	@echo "Restarting Celery worker (Docker)..."
	docker-compose restart celery_worker
	@echo "Celery worker restarted!"

celery-status: ## Celery worker status and stats
	@echo "Checking Celery worker status (Docker)..."
	@if docker-compose ps celery_worker | grep -q "Up"; then \
		echo "✅ Celery worker is running"; \
			docker-compose exec celery_worker celery -A api.services.celery.celery_config inspect active; \
			docker-compose exec celery_worker celery -A api.services.celery.celery_config inspect stats; \
	else \
		echo "❌ Celery worker is not running"; \
	fi

celery-monitor: ## Show Celery active/scheduled/reserved/stats/registered
	@echo "Monitoring Celery tasks and workers (Docker)..."
	@echo "============================================="
	@echo ""
	@echo "Active Tasks:"
	@docker-compose exec celery_worker celery -A api.services.celery.celery_config inspect active
	@echo ""
	@echo "Scheduled Tasks:"
	@docker-compose exec celery_worker celery -A api.services.celery.celery_config inspect scheduled
	@echo ""
	@echo "Reserved Tasks:"
	@docker-compose exec celery_worker celery -A api.services.celery.celery_config inspect reserved
	@echo ""
	@echo "Worker Stats:"
	@docker-compose exec celery_worker celery -A api.services.celery.celery_config inspect stats
	@echo ""
	@echo "Registered Tasks:"
	@docker-compose exec celery_worker celery -A api.services.celery.celery_config inspect registered

celery-flower: ## Start Flower (docker-compose)
	@echo "Starting Flower monitoring web UI (Docker)..."
	@echo "Flower will be available at: http://localhost:5555"
	docker-compose up -d flower

worker: ## Run Celery worker (foreground)
	@echo "Starting Celery worker (stdout logs; Docker)..."
	docker-compose up celery_worker

flower: ## Run Flower (foreground)
	@echo "Starting Flower on 0.0.0.0:5555 (Docker)..."
	docker-compose up flower

celery-purge: ## Purge all pending Celery tasks
	@echo "Purging all pending tasks (Docker)..."
	@docker-compose exec celery_worker celery -A api.services.celery.celery_config purge -f
	@echo "All pending tasks purged!"

celery-logs: ## Tail Celery worker logs
	@echo "Showing Celery worker logs (Docker)..."
	@docker-compose logs -f celery_worker

celery: ## Test Celery app load
	@echo "Testing Celery connection (Docker)..."
	@docker-compose exec celery_worker python -c "from api.services.celery.celery_config import celery_app; print('✅ Celery app loaded successfully'); print('Broker:', celery_app.conf.broker_url)"

celery-clean: ## Clean Celery containers/images
	@echo "Cleaning up Celery containers and images..."
	@docker-compose down celery_worker flower
	@docker rmi celery_worker:latest 2>/dev/null || true
	@echo "Celery Docker resources cleaned up!"

dev-start: ## Build and start all services (dev)
	@echo "Starting development environment (Docker)..."
	@./build.sh
	@echo "All services started. FastAPI available at http://localhost:4500"
	@echo "Flower available at http://localhost:5555"

prod-start: ## Build and start all services (prod)
	@echo "Starting production environment (Docker)..."
	@./build.sh
	@echo "Production environment started!"
	@echo "FastAPI: http://localhost:4500"
	@echo "Flower: http://localhost:5555"

stop-all: ## Stop all services (docker-compose down)
	@echo "Stopping all services..."
	@docker-compose down
	@echo "All services stopped!"

logs-all: ## Tail all service logs
	@echo "Showing logs for all services..."
	@docker-compose logs -f

restart-all: ## Restart all services
	@echo "Restarting all services..."
	@docker-compose restart
	@echo "All services restarted!"

# Legacy direct-exec/diagnostic targets retained as requested
workers: ## Start Celery worker via explicit path (legacy)
	@echo "Starting Celery worker (stdout logs; parrot env)..."
	@PYTHONPATH=/home/rehmet/tenx_ipersona /opt/miniconda/envs/parrot/bin/celery -A api.services.celery.celery_worker:celery_app worker -l info

flower-build: ## Build Flower docker image (docker.flower)
	@echo "Building Flower image..."
	@docker build -f docker.flower -t tenx/flower:latest .

flower-run: ## Run Flower container directly
	@echo "Running Flower..."
	@docker rm -f flower || true
	@docker run -d --name flower \
		-p 5555:5555 \
		-e CELERY_BROKER_URL=${CELERY_BROKER_URL} \
		-e CELERY_RESULT_BACKEND=${CELERY_RESULT_BACKEND} \
		tenx/flower:latest

flower-logs: ## Tail Flower logs
	@docker logs -f flower | cat

flower-stop: ## Stop Flower container
	@docker rm -f flower || true

work: ## Kill Celery processes locally and start worker (legacy)
	@echo "🔥 Killing all running Celery processes..."
	@echo "==========================================="
	@echo ""
	@echo "1️⃣ Stopping Docker Celery worker..."
	@docker-compose stop celery_worker 2>/dev/null || echo "   ℹ️ No Docker Celery worker running"
	@echo ""
	@echo "2️⃣ Removing Docker Celery container..."
	@docker-compose rm -f celery_worker 2>/dev/null || echo "   ℹ️ No Docker Celery container to remove"
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

