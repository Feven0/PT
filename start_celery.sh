#!/bin/bash
echo "Starting Celery worker..."
celery -A api.services.celery.celery_config worker \
    --loglevel=info \
    --queues=audio_processing,file_processing,default \
    --concurrency=2 \
    --hostname=worker@%h \
    --time-limit=1800 \
    --soft-time-limit=1500 \
    --max-tasks-per-child=10 \
    --prefetch-multiplier=1



