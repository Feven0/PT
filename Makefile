# Makefile for Tenx iPersona Celery Management
# Usage: make <command>

.PHONY: help celery-start celery-stop celery-restart celery-status celery-monitor celery-flower celery-purge celery-logs install-celery

# Default target
help:
	@echo "Tenx iPersona Celery Management"
	@echo "=============================="
	@echo ""
	@echo "Available commands:"
	@echo "  make celery-start     - Start Celery worker"
	@echo "  make celery-stop      - Stop Celery worker"
	@echo "  make celery-restart   - Restart Celery worker"
	@echo "  make celery-status    - Check Celery worker status"
	@echo "  make celery-monitor   - Monitor Celery tasks and workers"
	@echo "  make celery-flower    - Start Flower (Celery monitoring web UI)"
	@echo "  make celery-purge     - Purge all pending tasks"
	@echo "  make celery-logs      - Show Celery worker logs"
	@echo "  make install-celery   - Install Celery dependencies"
	@echo "  make help            - Show this help message"
	@echo ""

# Install Celery dependencies
install-celery:
	@echo "Installing Celery dependencies..."
	pip install celery==5.3.4 flower
	@echo "Celery dependencies installed successfully!"

# Start Celery worker
celery-start:
	@echo "Starting Celery worker..."
	celery -A api.services.celery.celery_config worker \
		--loglevel=info \
		--queues=audio_processing,file_processing,default \
		--concurrency=2 \
		--hostname=worker@$$(hostname)-$$(date +%s) \
		--time-limit=1800 \
		--soft-time-limit=1500 \
		--max-tasks-per-child=10 \
		--prefetch-multiplier=1

# Start Celery worker in background
celery-start-bg:
	@echo "Starting Celery worker in background..."
	celery -A api.services.celery.celery_config worker \
		--loglevel=info \
		--queues=audio_processing,file_processing,default \
		--concurrency=2 \
		--hostname=worker@$$(hostname)-$$(date +%s) \
		--time-limit=1800 \
		--soft-time-limit=1500 \
		--max-tasks-per-child=10 \
		--prefetch-multiplier=1 \
		--detach \
		--pidfile=celery.pid \
		--logfile=celery.log

# Stop Celery worker
celery-stop:
	@echo "Stopping Celery worker..."
	@if [ -f celery.pid ]; then \
		kill -TERM $$(cat celery.pid) && \
		rm -f celery.pid && \
		echo "Celery worker stopped successfully!"; \
	else \
		echo "No Celery worker PID file found. Trying to stop by process name..."; \
		pkill -f "celery.*worker" && echo "Celery worker stopped!" || echo "No Celery worker found running."; \
	fi

# Restart Celery worker
celery-restart: celery-stop
	@sleep 2
	@$(MAKE) celery-start-bg

# Check Celery worker status
celery-status:
	@echo "Checking Celery worker status..."
	@celery -A api.services.celery.celery_config inspect active
	@echo ""
	@celery -A api.services.celery.celery_config inspect stats

# Monitor Celery tasks and workers
celery-monitor:
	@echo "Monitoring Celery tasks and workers..."
	@echo "====================================="
	@echo ""
	@echo "📝 NOTE: Task processing logs appear in your uvicorn terminal"
	@echo "📝 This terminal shows worker status and task management"
	@echo ""
	@echo "Active Tasks:"
	@celery -A api.services.celery.celery_config inspect active
	@echo ""
	@echo "Scheduled Tasks:"
	@celery -A api.services.celery.celery_config inspect scheduled
	@echo ""
	@echo "Reserved Tasks:"
	@celery -A api.services.celery.celery_config inspect reserved
	@echo ""
	@echo "Worker Stats:"
	@celery -A api.services.celery.celery_config inspect stats
	@echo ""
	@echo "Registered Tasks:"
	@celery -A api.services.celery.celery_config inspect registered

# Start Flower (Celery monitoring web UI)
celery-flower:
	@echo "Starting Flower monitoring web UI..."
	@echo "Flower will be available at: http://localhost:5555"
	celery -A api.services.celery.celery_config flower --port=5555

# Purge all pending tasks
celery-purge:
	@echo "Purging all pending tasks..."
	@celery -A api.services.celery.celery_config purge -f
	@echo "All pending tasks purged!"

# Show Celery worker logs
celery-logs:
	@echo "Showing Celery worker logs..."
	@if [ -f celery.log ]; then \
		tail -f celery.log; \
	else \
		echo "No log file found. Start Celery with 'make celery-start-bg' to create logs."; \
	fi

# Test Celery connection
celery:
	@echo "Testing Celery connection..."
	@python -c "from api.services.celery.celery_config import celery_app; print('✅ Celery app loaded successfully'); print('Broker:', celery_app.conf.broker_url)"

# Clean up Celery files
celery-clean:
	@echo "Cleaning up Celery files..."
	@rm -f celery.pid celery.log
	@echo "Celery files cleaned up!"

# Development mode - start both FastAPI and Celery
dev-start:
	@echo "Starting development environment..."
	@echo "Starting Celery worker in background..."
	@$(MAKE) celery-start-bg
	@echo "Celery worker started. Now start FastAPI with:"
	@echo "uvicorn app:app --host 0.0.0.0 --port 9990 --reload"

# Production mode - start Celery with more workers
prod-start:
	@echo "Starting production Celery worker..."
	celery -A api.services.celery.celery_config worker \
		--loglevel=info \
		--queues=audio_processing,file_processing,default \
		--concurrency=4 \
		--hostname=worker@%h \
		--time-limit=1800 \
		--soft-time-limit=1500 \
		--max-tasks-per-child=50 \
		--prefetch-multiplier=1 \
		--detach \
		--pidfile=celery.pid \
		--logfile=celery.log
