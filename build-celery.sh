#!/bin/bash

# Celery and Flower Build Script
# Usage: ./build-celery.sh [branch] [action]
# Actions: build, up, down, restart, logs
# Examples:
#   ./build-celery.sh              # Build and start with current branch
#   ./build-celery.sh dev build    # Just build images
#   ./build-celery.sh dev-prod up  # Start services without rebuilding
#   ./build-celery.sh dev logs     # Show logs

set -e

# Create alias if docker-compose command doesn't exist
if ! command -v docker-compose &> /dev/null; then
    if ! command -v docker-compose &> /dev/null; then
        if command -v docker &> /dev/null && docker compose version &> /dev/null; then
            docker-compose() { docker compose "$@"; }
        else
            echo "Error: Neither docker-compose nor docker compose command found"
            exit 1
        fi
    fi
fi
#-----------------------------------------------
#---- Setup necessary ENV variables ------------
#-----------------------------------------------
branch_name=${1:-$(git symbolic-ref -q HEAD)}
branch_name=${branch_name##refs/heads/}
export branch_name=${branch_name:-HEAD}

action=${2:-"restart"}  # Default action: restart (build + up)

if [ "$branch_name" == "prod" ]; then
    echo "******Running Production Celery Environment******"
    export STRAPI_STAGE="prod"  
elif [ "$branch_name" == "dev-prod" ]; then
    echo "******Running dev-prod Celery Environment******"
    export STRAPI_STAGE="dev-prod"   
else
    echo "******Running Development Celery Environment******"
    export STRAPI_STAGE="dev"  
fi

# Set default environment file based on stage
if [[ $STRAPI_STAGE == "prod" ]]; then
    envfile=".env/.envprod"
elif [[ $STRAPI_STAGE == "dev-prod" ]]; then
    envfile=".env/.envdev"
else
    envfile=".env/.envdev"
fi

# Try to source environment file if it exists, otherwise use defaults
if [ -f "$envfile" ]; then
    echo "build-celery.sh: using envfile=$envfile"
    # Don't source it as it might cause issues, just note it exists
else
    echo "build-celery.sh: envfile=$envfile not found, using environment defaults"
fi

# Extract Redis URL from api/config.py
echo "Extracting Redis configuration from api/config.py..."
REDIS_URL_FROM_CONFIG=$(python3 -c "
import sys, os
sys.path.append('.')
os.environ['STRAPI_STAGE'] = '$STRAPI_STAGE'
# Disable all logging to prevent interference
import logging
logging.disable(logging.CRITICAL)
try:
    from api.config import cache
    print(cache.REDIS_URL)
except Exception as e:
    print('redis://redis.10academy.org:6379/0')
" 2>/dev/null | tail -1)

# Use the extracted Redis URL, adding /0 database if not present
if [[ "$REDIS_URL_FROM_CONFIG" != *"/0" ]] && [[ "$REDIS_URL_FROM_CONFIG" != *"/1" ]] && [[ "$REDIS_URL_FROM_CONFIG" != *"/2" ]]; then
    REDIS_URL_FROM_CONFIG="${REDIS_URL_FROM_CONFIG}/0"
fi

export REDIS_URL="${REDIS_URL_FROM_CONFIG}"
echo "Using Redis URL from config: ${REDIS_URL}"

# Set project name based on branch
if [[ $branch_name == "prod" ]]; then
    project_name="prod_celery"
elif [[ $branch_name == "dev-prod" ]]; then
    project_name="ipersona_celery"
else
    project_name="dev_celery"
fi

echo "Project: $project_name"
echo "Branch: $branch_name" 
echo "Stage: $STRAPI_STAGE"
echo "Action: $action"

#=========================================
#       write docker-compose-celery.yml
#=========================================

cat <<EOF > docker-compose-celery.yml
version: "3"
services:
  celery_worker:
    container_name: ${project_name}_worker
    build:
      context: .
      dockerfile: Dockerfile.celery
    image: celery_worker:latest
    restart: unless-stopped
    environment:
      - STRAPI_STAGE=$STRAPI_STAGE
      - PYTHONPATH=/app
      - REDIS_URL=\${REDIS_URL:-redis://redis.10academy.org:6379/0}
      - CELERY_BROKER_URL=\${REDIS_URL:-redis://redis.10academy.org:6379/0}
      - CELERY_RESULT_BACKEND=\${REDIS_URL:-redis://redis.10academy.org:6379/0}
      - SOCKETIO_REDIS_URL=\${REDIS_URL:-redis://redis.10academy.org:6379/0}
      - AWS_ACCESS_KEY_ID=\${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=\${AWS_SECRET_ACCESS_KEY}
      - AWS_DEFAULT_REGION=\${AWS_DEFAULT_REGION:-us-east-1}
    networks:
      - celery_network
    command: ["/bin/bash", "-c", "echo 'Starting Celery worker...' && celery -A api.services.celery.celery_worker:celery_app worker --loglevel=info --queues=celery,audio_processing,file_processing,default --concurrency=2 --hostname=worker@%h --time-limit=1800 --soft-time-limit=1500 --max-tasks-per-child=10 --prefetch-multiplier=1"]

  flower:
    container_name: ${project_name}_flower
    build:
      context: .
      dockerfile: docker.flower
    image: tenx_flower:latest
    restart: unless-stopped
    environment:
      - CELERY_BROKER_URL=\${REDIS_URL:-redis://redis.10academy.org:6379/0}
      - CELERY_RESULT_BACKEND=\${REDIS_URL:-redis://redis.10academy.org:6379/0}
    networks:
      - celery_network
    ports:
      - "5555:5555"
    depends_on:
      - celery_worker

networks:
    celery_network:
        name: ${project_name}_network
        driver: bridge      

EOF

#-----------------------------------------------
#---- Handle different actions ----------------
#-----------------------------------------------

case $action in
    "build")
        echo "🔨 Building Celery and Flower images..."
        docker-compose -f docker-compose-celery.yml -p "$project_name" build --no-cache
        echo "✅ Build completed!"
        ;;
        
    "up")
        echo "🚀 Starting Celery and Flower services..."
        docker-compose -f docker-compose-celery.yml -p "$project_name" up -d
        echo "✅ Services started!"
        docker ps | grep -E "(celery|flower)"
        ;;
        
    "down")
        echo "🛑 Stopping Celery and Flower services..."
        docker-compose -f docker-compose-celery.yml -p "$project_name" down --remove-orphans
        echo "✅ Services stopped!"
        ;;
        
    "restart"|"")
        echo "🔄 Restarting Celery and Flower services..."
        
        # Clean up any existing containers
        echo "Cleaning up existing containers..."
        docker stop "${project_name}_worker" "${project_name}_flower" 2>/dev/null || true
        docker rm -f "${project_name}_worker" "${project_name}_flower" 2>/dev/null || true
        
        # Stop existing compose project
        docker-compose -f docker-compose-celery.yml -p "$project_name" down --remove-orphans 2>/dev/null || true
        
        # Build and start
        echo "Building images..."
        docker-compose -f docker-compose-celery.yml -p "$project_name" build --no-cache celery_worker flower
        
        echo "Starting services..."
        docker-compose -f docker-compose-celery.yml -p "$project_name" up -d --force-recreate
        
        echo "✅ Services restarted!"
        docker ps | grep -E "(celery|flower)"
        ;;
        
    "logs")
        echo "📋 Showing Celery worker logs..."
        docker logs -f "${project_name}_worker"
        ;;
        
    "flower-logs")
        echo "📋 Showing Flower logs..."
        docker logs -f "${project_name}_flower"
        ;;
        
    "status")
        echo "📊 Celery and Flower status:"
        docker ps | grep -E "(celery|flower)" || echo "No Celery/Flower containers running"
        
        if docker ps | grep -q "${project_name}_worker"; then
            echo ""
            echo "Celery worker tasks:"
            docker exec "${project_name}_worker" celery -A api.services.celery.celery_worker:celery_app inspect registered 2>/dev/null || echo "Worker not ready"
        fi
        ;;
        
    "test")
        echo "🧪 Testing Celery worker..."
        if [ -f "test_celery_docker.py" ]; then
            export REDIS_URL='\${REDIS_URL:-redis://redis.10academy.org:6379/0}'
            python test_celery_docker.py
        else
            echo "test_celery_docker.py not found"
        fi
        ;;
        
    *)
        echo "❌ Unknown action: $action"
        echo ""
        echo "Available actions:"
        echo "  build      - Build Celery and Flower images only"
        echo "  up         - Start services without rebuilding"
        echo "  down       - Stop all services"
        echo "  restart    - Stop, rebuild, and start services (default)"
        echo "  logs       - Show Celery worker logs"
        echo "  flower-logs - Show Flower logs"
        echo "  status     - Show running status and registered tasks"
        echo "  test       - Test Celery worker with test script"
        echo ""
        echo "Examples:"
        echo "  ./build-celery.sh                    # Restart with current branch"
        echo "  ./build-celery.sh dev-prod build     # Build images for dev-prod"
        echo "  ./build-celery.sh dev logs           # Show logs"
        echo "  ./build-celery.sh dev-prod status    # Check status"
        exit 1
        ;;
esac

echo ""
echo "🎯 Celery build script completed!"
echo "   Project: $project_name"
echo "   Branch: $branch_name"
echo "   Stage: $STRAPI_STAGE"
echo ""
echo "💡 Useful commands:"
echo "   ./build-celery.sh $branch_name logs       # View worker logs"
echo "   ./build-celery.sh $branch_name status     # Check status"
echo "   ./build-celery.sh $branch_name down       # Stop services"
echo "   docker exec ${project_name}_worker celery -A api.services.celery.celery_worker:celery_app inspect active"
echo ""
