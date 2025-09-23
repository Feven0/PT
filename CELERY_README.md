# Docker-based Celery Setup for Tenx iPersona

This project now includes Docker-based Celery integration for background task processing, providing better scalability, reliability, and isolation compared to FastAPI's built-in background tasks.

## Quick Start

### 1. Build Celery Docker Images
```bash
make build-celery
```

### 2. Start All Services (FastAPI + Celery + Flower)
```bash
make dev-start
```

### 3. Access Services
- **FastAPI**: http://localhost:4900
- **Flower (Celery Monitoring)**: http://localhost:5555

## Available Make Commands

| Command | Description |
|---------|-------------|
| `make build-celery` | Build Celery Docker images |
| `make celery-start` | Start Celery worker (Docker) |
| `make celery-start-bg` | Start Celery worker in background (Docker) |
| `make celery-stop` | Stop Celery worker (Docker) |
| `make celery-restart` | Restart Celery worker (Docker) |
| `make celery-status` | Check worker status (Docker) |
| `make celery-monitor` | Monitor tasks and workers (Docker) |
| `make celery-flower` | Start Flower web UI (Docker) |
| `make celery-purge` | Purge all pending tasks (Docker) |
| `make celery-logs` | Show worker logs (Docker) |
| `make celery` | Test Celery connection (Docker) |
| `make dev-start` | Start all services for development |
| `make prod-start` | Start all services for production |

## New Endpoints

### Audio Processing with Celery
- **POST** `/audio_upload_external_celery` - Process audio files using Celery
- **GET** `/audio_upload_external_celery_status/{task_id}` - Check task status

### Files Processing with Celery
- **POST** `/files_upload_external_celery` - Process dual audio files using Celery
- **GET** `/files_upload_external_celery_status/{task_id}` - Check task status

### Example Usage

```bash
# Upload audio file
curl -X POST "http://localhost:9990/audio_upload_external_celery" \
  -F "file=@audio.mp3" \
  -F "target={\"job_profile_id\":\"123\"}"

# Check audio task status
curl "http://localhost:9990/audio_upload_external_celery_status/{task_id}"

# Upload dual files (question + answer)
curl -X POST "http://localhost:9990/files_upload_external_celery" \
  -F "Question_file=@question.mp3" \
  -F "Answer_file=@answer.mp3" \
  -F "target={\"job_profile_id\":\"123\"}"

# Check files task status
curl "http://localhost:9990/files_upload_external_celery_status/{task_id}"
```

## Monitoring

### Flower Web UI
Start Flower for a beautiful web interface to monitor Celery:
```bash
make celery-flower
```
Then visit: http://localhost:5555

### Command Line Monitoring
```bash
make celery-monitor
```

## Configuration

Celery is configured to use Redis as both broker and result backend:
- **Broker**: `redis://redis.10academy.org:6379/0`
- **Queues**: `audio_processing`, `file_processing`, `default`
- **Concurrency**: 2 workers (configurable)
- **Container**: Docker-based with automatic restart

## Benefits

✅ **Containerized** - Isolated environment with consistent dependencies  
✅ **No interference** - Celery tasks run independently  
✅ **Scalable** - Can run multiple workers  
✅ **Persistent** - Tasks survive server restarts  
✅ **Monitorable** - Track progress via API and Flower  
✅ **Same logic** - Uses existing processing functions  
✅ **Easy deployment** - Single docker-compose command  

## Troubleshooting

### Check if Celery is running
```bash
make celery-status
```

### Test connection
```bash
make celery
```

### View logs
```bash
make celery-logs
```

### Purge stuck tasks
```bash
make celery-purge
```

### Rebuild containers
```bash
make build-celery
make dev-start
```

### Clean up Docker resources
```bash
make celery-clean
```

## Docker Commands

### Direct Docker Compose Commands
```bash
# Start all services
docker-compose up -d

# Start only Celery worker
docker-compose up -d celery_worker

# Start only Flower
docker-compose up -d flower

# View logs
docker-compose logs -f celery_worker
docker-compose logs -f flower

# Stop services
docker-compose stop celery_worker
docker-compose stop flower

# Rebuild and restart
docker-compose build celery_worker flower
docker-compose up -d
```
