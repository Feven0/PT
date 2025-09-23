# Makefile for Tenx iPersona Docker-based Celery Management
# Usage: make <command>

.PHONY: help celery-start celery-stop celery-restart celery-status celery-monitor celery-flower celery-purge celery-logs build-celery run-worker run-flower dev-start prod-start stop-all logs-all restart-all

# Default target
help:
	@echo "Tenx iPersona Docker-based Celery Management"
	@echo "==========================================="
	@echo ""
	@echo "Available commands:"
	@echo "  make build-celery     - Build Celery Docker images"
	@echo "  make celery-start     - Start Celery worker (Docker)"
	@echo "  make celery-stop      - Stop Celery worker (Docker)"
	@echo "  make celery-restart   - Restart Celery worker (Docker)"
	@echo "  make celery-status    - Check Celery worker status"
	@echo "  make celery-monitor   - Monitor Celery tasks and workers"
	@echo "  make celery-flower    - Start Flower (Celery monitoring web UI)"
	@echo "  make run-worker       - Run worker with stdout logs (Docker)"
	@echo "  make run-flower       - Run Flower on 0.0.0.0:5555 (Docker)"
	@echo "  make celery-purge     - Purge all pending tasks"
	@echo "  make celery-logs      - Show Celery worker logs"
	@echo "  make dev-start        - Start all services for development"
	@echo "  make prod-start       - Start all services for production"
	@echo "  make stop-all         - Stop all services"
	@echo "  make logs-all         - Show logs for all services"
	@echo "  make restart-all      - Restart all services"
	@echo "  make help            - Show this help message"
	@echo ""

# Build Celery Docker images
build-celery:
	@echo "Building all Docker images (including Celery)..."
	@./build.sh
	@echo "All Docker images built successfully!"

# Start Celery worker
celery-start:
	@echo "Starting Celery worker (Docker)..."
	docker-compose up -d celery_worker
	@echo "Celery worker started successfully!"

# Start Celery worker in background (same as celery-start for Docker)
celery-start-bg:
	@echo "Starting Celery worker in background (Docker)..."
	docker-compose up -d celery_worker
	@echo "Celery worker started in background!"

# Stop Celery worker
celery-stop:
	@echo "Stopping Celery worker (Docker)..."
	docker-compose stop celery_worker
	@echo "Celery worker stopped!"

# Restart Celery worker
celery-restart:
	@echo "Restarting Celery worker (Docker)..."
	docker-compose restart celery_worker
	@echo "Celery worker restarted!"

# Check Celery worker status
celery-status:
	@echo "Checking Celery worker status (Docker)..."
	@if docker-compose ps celery_worker | grep -q "Up"; then \
		echo "✅ Celery worker is running"; \
		docker-compose exec celery_worker celery -A api.services.celery.celery_worker_config inspect active; \
		docker-compose exec celery_worker celery -A api.services.celery.celery_worker_config inspect stats; \
	else \
		echo "❌ Celery worker is not running"; \
	fi

# Monitor Celery tasks and workers
celery-monitor:
	@echo "Monitoring Celery tasks and workers (Docker)..."
	@echo "============================================="
	@echo ""
	@echo "📝 NOTE: Task processing logs appear in Docker container logs"
	@echo "📝 This terminal shows worker status and task management"
	@echo ""
	@echo "Active Tasks:"
	@docker-compose exec celery_worker celery -A api.services.celery.celery_worker_config inspect active
	@echo ""
	@echo "Scheduled Tasks:"
	@docker-compose exec celery_worker celery -A api.services.celery.celery_worker_config inspect scheduled
	@echo ""
	@echo "Reserved Tasks:"
	@docker-compose exec celery_worker celery -A api.services.celery.celery_worker_config inspect reserved
	@echo ""
	@echo "Worker Stats:"
	@docker-compose exec celery_worker celery -A api.services.celery.celery_worker_config inspect stats
	@echo ""
	@echo "Registered Tasks:"
	@docker-compose exec celery_worker celery -A api.services.celery.celery_worker_config inspect registered

# Start Flower (Celery monitoring web UI)
celery-flower:
	@echo "Starting Flower monitoring web UI (Docker)..."
	@echo "Flower will be available at: http://localhost:5555"
	docker-compose up -d flower

# Exact run: Celery worker with stdout logs (Docker)
worker:
	@echo "Starting Celery worker (stdout logs; Docker)..."
	docker-compose up celery_worker

# Exact run: Flower on 0.0.0.0:5555 (Docker)
flower:
	@echo "Starting Flower on 0.0.0.0:5555 (Docker)..."
	docker-compose up flower

# Purge all pending tasks
celery-purge:
	@echo "Purging all pending tasks (Docker)..."
	@docker-compose exec celery_worker celery -A api.services.celery.celery_worker_config purge -f
	@echo "All pending tasks purged!"

# Show Celery worker logs
celery-logs:
	@echo "Showing Celery worker logs (Docker)..."
	@docker-compose logs -f celery_worker

# Test Celery connection
celery:
	@echo "Testing Celery connection (Docker)..."
	@docker-compose exec celery_worker python -c "from api.services.celery.celery_worker_config import celery_app; print('✅ Celery app loaded successfully'); print('Broker:', celery_app.conf.broker_url)"

# Clean up Celery files
celery-clean:
	@echo "Cleaning up Celery containers and images..."
	@docker-compose down celery_worker flower
	@docker rmi celery_worker:latest 2>/dev/null || true
	@echo "Celery Docker resources cleaned up!"

# Development mode - start both FastAPI and Celery
dev-start:
	@echo "Starting development environment (Docker)..."
	@echo "Building and starting all services..."
	@./build.sh
	@echo "All services started. FastAPI available at http://localhost:4500"
	@echo "Flower available at http://localhost:5555"

# Production mode - start all services
prod-start:
	@echo "Starting production environment (Docker)..."
	@echo "Building and starting all services..."
	@./build.sh
	@echo "Production environment started!"
	@echo "FastAPI: http://localhost:4500"
	@echo "Flower: http://localhost:5555"

# Stop all services
stop-all:
	@echo "Stopping all services..."
	@docker-compose down
	@echo "All services stopped!"

# View all logs
logs-all:
	@echo "Showing logs for all services..."
	@docker-compose logs -f

# Restart all services
restart-all:
	@echo "Restarting all services..."
	@docker-compose restart
	@echo "All services restarted!"



# # Start Flower (Celery monitoring web UI)
# celery-flower:
# 	@echo "Starting Flower monitoring web UI..."
# 	@echo "Flower will be available at: http://localhost:5555"
# 	celery -A api.services.celery.celery_config flower --port=5555

# Exact run: Celery worker with stdout logs
workers:
	@echo "Starting Celery worker (stdout logs; parrot env)..."
	@PYTHONPATH=/home/rehmet/tenx_ipersona /opt/miniconda/envs/parrot/bin/celery -A api.services.celery.celery_worker:celery_app worker -l info

# Minimal worker that only imports the socket test task.
# Usage: make socket_worker PORT=9990
socket_worker:
	@echo "Starting Socket-Only Celery worker (parrot env)..."
	@SOCKETIO_SERVER_URL=http://localhost:9990 PYTHONPATH=/home/rehmet/tenx_ipersona \
	/opt/miniconda/envs/parrot/bin/celery -A api.services.celery.celery_socket_only worker -l info
