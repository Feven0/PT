#!/bin/bash

# Celery Worker Startup Script for Tenx iPersona
# This script starts Celery workers for processing audio and file uploads

echo "Starting Celery workers for Tenx iPersona..."

# Set environment variables
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Start Celery worker with specific queues
celery -A api.services.celery.celery_config worker \
    --loglevel=info \
    --queues=audio_processing,file_processing,default \
    --concurrency=2 \
    --hostname=worker@%h \
    --time-limit=1800 \
    --soft-time-limit=1500 \
    --max-tasks-per-child=10 \
    --prefetch-multiplier=1

echo "Celery worker started successfully!"
