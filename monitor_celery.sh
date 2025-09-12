#!/bin/bash

# Celery Monitoring Script for Tenx iPersona
# This script provides monitoring capabilities for Celery tasks

echo "Celery Monitoring for Tenx iPersona"
echo "=================================="

# Set environment variables
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Show active tasks
echo "Active Tasks:"
celery -A api.services.celery.celery_config inspect active

echo ""
echo "Scheduled Tasks:"
celery -A api.services.celery.celery_config inspect scheduled

echo ""
echo "Reserved Tasks:"
celery -A api.services.celery.celery_config inspect reserved

echo ""
echo "Worker Stats:"
celery -A api.services.celery.celery_config inspect stats

echo ""
echo "Registered Tasks:"
celery -A api.services.celery.celery_config inspect registered
