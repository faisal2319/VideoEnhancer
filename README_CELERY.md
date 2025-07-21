# Video Quality Enhancer with Celery

This project now uses Celery with Redis for distributed task processing of video enhancement pipelines.

## Architecture

- **API Service**: FastAPI application that handles HTTP requests and triggers Celery tasks
- **Celery Worker**: Processes video enhancement tasks in the background
- **Redis**: Message broker and result backend for Celery
- **Shared Volume**: Cross-service communication through shared files

## Services

### 1. Redis Service

- Message broker for Celery
- Stores task results and state
- Runs on port 6379

### 2. API Service

- FastAPI application
- Handles HTTP requests
- Triggers Celery tasks
- Runs on port 8000

### 3. Celery Worker

- Processes video enhancement tasks
- Runs the ML pipeline in the background
- Monitored by health checks

## Setup and Running

### 1. Build and Start Services

```bash
docker-compose up --build
```

This will start:

- Redis service
- API service (port 8000)
- Celery worker

### 2. Check Service Health

```bash
# Check API health
curl http://localhost:8000/health

# Check Redis
docker-compose exec redis redis-cli ping

# Check Celery worker
docker-compose exec celery-worker celery -A shared.celery_app inspect ping
```

## API Endpoints

### Trigger Video Enhancement

```bash
curl -X POST "http://localhost:8000/api/v1/enhance-video" \
  -H "Content-Type: application/json" \
  -d '{"video_path": "input.mp4"}'
```

Response:

```json
{
  "status": "success",
  "message": "Video enhancement task submitted",
  "task_id": "abc123-def456-ghi789",
  "video_path": "input.mp4",
  "task_status_url": "/api/v1/task-status/abc123-def456-ghi789"
}
```

### Check Task Status

```bash
curl "http://localhost:8000/api/v1/task-status/{task_id}"
```

Response:

```json
{
  "task_id": "abc123-def456-ghi789",
  "status": {
    "state": "SUCCESS",
    "status": "Pipeline completed successfully",
    "meta": {
      "video_path": "input.mp4",
      "total_frames": 100,
      "enhanced_frames": 25,
      "output_path": "ml_output/reconstructed.mp4"
    }
  }
}
```

## Task States

- **PENDING**: Task is waiting to be processed
- **STARTED**: Task has started processing
- **SUCCESS**: Task completed successfully
- **FAILURE**: Task failed with an error

## Monitoring

### View Celery Worker Status

```bash
docker-compose exec celery-worker celery -A shared.celery_app inspect active
```

### View Task Results

```bash
docker-compose exec celery-worker celery -A shared.celery_app inspect reserved
```

### View Failed Tasks

```bash
docker-compose exec celery-worker celery -A shared.celery_app inspect failed
```

## Development

### Running Locally (without Docker)

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Start Redis:

   ```bash
   redis-server
   ```

3. Start Celery worker:

   ```bash
   cd ml
   celery -A ../shared.celery_app worker --loglevel=info
   ```

4. Start API:
   ```bash
   python api/main.py
   ```

### Testing

```bash
# Test Celery connection
python test_celery.py
```

## File Structure

```
video-quality-enhancer/
├── shared/
│   └── celery_app.py          # Shared Celery app instance
├── ml/
│   ├── tasks.py               # Celery tasks
│   ├── run_pipeline.py        # Original pipeline
│   └── celery_worker.py       # Worker configuration
├── api/
│   ├── main.py                # FastAPI app
│   └── routes.py              # API routes with Celery integration
├── docker-compose.yml         # Multi-service setup
├── Dockerfile                 # Container configuration
└── requirements.txt           # Python dependencies
```

## Troubleshooting

### Common Issues

1. **Celery worker not starting**

   - Check Redis connection
   - Verify shared volume mounts
   - Check logs: `docker-compose logs celery-worker`

2. **Tasks not being processed**

   - Verify worker is running: `docker-compose exec celery-worker celery -A shared.celery_app inspect active`
   - Check Redis connection
   - Verify task queue configuration

3. **Import errors**
   - Ensure PYTHONPATH is set correctly
   - Check shared volume mounts
   - Verify file permissions

### Logs

```bash
# View all logs
docker-compose logs

# View specific service logs
docker-compose logs api
docker-compose logs celery-worker
docker-compose logs redis
```

## Configuration

### Environment Variables

- `REDIS_URL`: Redis connection string (default: `redis://redis:6379/0`)
- `PYTHONPATH`: Python path for imports (default: `/app`)

### Celery Configuration

- Task timeout: 30 minutes
- Soft timeout: 25 minutes
- Queue: `ml_queue`
- Result backend: Redis
- Serializer: JSON
