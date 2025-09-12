# Celery Setup for Tenx iPersona

This project now includes Celery integration for background task processing, providing better scalability and reliability compared to FastAPI's built-in background tasks.

## Quick Start

### 1. Install Dependencies
```bash
make install-celery
```

### 2. Start Celery Worker
```bash
make celery-start
```

### 3. Start FastAPI Server (in another terminal)
```bash
uvicorn app:app --host 0.0.0.0 --port 9990 --reload
```

## Available Make Commands

| Command | Description |
|---------|-------------|
| `make celery-start` | Start Celery worker in foreground |
| `make celery-start-bg` | Start Celery worker in background |
| `make celery-stop` | Stop Celery worker |
| `make celery-restart` | Restart Celery worker |
| `make celery-status` | Check worker status |
| `make celery-monitor` | Monitor tasks and workers |
| `make celery-flower` | Start Flower web UI (http://localhost:5555) |
| `make celery-purge` | Purge all pending tasks |
| `make celery-logs` | Show worker logs |
| `make celery-test` | Test Celery connection |
| `make dev-start` | Start Celery in background for development |

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

## Benefits

✅ **No interference** - Celery tasks run independently  
✅ **Scalable** - Can run multiple workers  
✅ **Persistent** - Tasks survive server restarts  
✅ **Monitorable** - Track progress via API and Flower  
✅ **Same logic** - Uses existing processing functions  

## Troubleshooting

### Check if Celery is running
```bash
make celery-status
```

### Test connection
```bash
make celery-test
```

### View logs
```bash
make celery-logs
```

### Purge stuck tasks
```bash
make celery-purge
```
