from celery import Celery
import os

# Redis configuration
REDIS_URL = os.getenv('REDIS_URL', 'redis://redis:6379/0')

# Create Celery app instance
celery_app = Celery(
    'video_enhancer',
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=['ml.tasks']  # Include the tasks module
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Optional: Configure task routes
celery_app.conf.task_routes = {
    'ml.tasks.run_pipeline_task': {'queue': 'ml_queue'},
}

if __name__ == '__main__':
    celery_app.start()
