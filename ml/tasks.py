import os
import sys
import logging
from celery import current_task
from shared.celery_app import celery_app
from run_pipeline import run_pipeline
from shared.minio_client import get_minio_client
import tempfile
import re
from shared.redis_client import redis_client

# Add the parent directory to the path so we can import from shared
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@celery_app.task(bind=True, name='ml.tasks.run_pipeline_task')
def run_pipeline_task(self, video_path="input.mp4"):
    """
    Celery task to run the video enhancement pipeline
    
    Args:
        video_path (str): MinIO object path (bucket/key)
        
    Returns:
        dict: Results of the pipeline execution
    """
    try:
        # Always treat video_path as MinIO object path (bucket/key)
        minio_client = get_minio_client()
        bucket, key = video_path.split('/', 1)
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(key)[-1])
        minio_client.download_fileobj(bucket, key, temp_file)
        temp_file.close()
        local_video_path = temp_file.name
        
        # Update task state to STARTED
        self.update_state(
            state='STARTED',
            meta={'status': 'Pipeline started', 'video_path': video_path}
        )

        # Define a callback to publish progress to Redis
        def publish_progress_to_redis(progress_data):
            redis_client.publish(f"task_updates:{self.request.id}", progress_data)

        # Run the pipeline with task instance for progress updates and Redis callback
        results = run_pipeline(local_video_path, task=self, progress_callback=publish_progress_to_redis)

        # Upload the enhanced video to MinIO under 'enhanced/reconstructed.mp4' in the same bucket
        enhanced_local_path = os.path.join('ml_output', 'reconstructed.mp4')
        enhanced_key = 'enhanced/reconstructed.mp4'
        with open(enhanced_local_path, 'rb') as enhanced_file:
            minio_client.upload_fileobj(enhanced_file, bucket, enhanced_key)
        enhanced_minio_path = f"{bucket}/{enhanced_key}"

        # Update task state to SUCCESS
        self.update_state(
            state='SUCCESS',
            meta={
                'status': 'Pipeline completed successfully',
                'video_path': video_path,
                'total_frames': len(results),
                'enhanced_frames': sum(1 for r in results if r.get('blurry') or r.get('dark')),
                'output_path': enhanced_minio_path
            }
        )
        # Publish final success to Redis
        publish_progress_to_redis({
            'state': 'SUCCESS',
            'status': 'Pipeline completed successfully',
            'output_path': enhanced_minio_path
        })
        
        # Clean up temp file
        os.unlink(temp_file.name)
        
        return {
            'status': 'success',
            'video_path': video_path,
            'total_frames': len(results),
            'enhanced_frames': sum(1 for r in results if r.get('blurry') or r.get('dark')),
            'output_path': enhanced_minio_path,
            'results': results
        }
        
    except Exception as e:
        # Update task state to FAILURE
        self.update_state(
            state='FAILURE',
            meta={
                'status': 'Pipeline failed',
                'error': str(e),
                'video_path': video_path
            }
        )
        # Publish failure to Redis
        redis_client.publish(f"task_updates:{self.request.id}", {
            'state': 'FAILURE',
            'status': 'Pipeline failed',
            'error': str(e)
        })
        
        logging.error(f"Pipeline task failed: {str(e)}")
        raise

@celery_app.task(bind=True, name='ml.tasks.get_task_status')
def get_task_status(self, task_id):
    """
    Get the status of a running task
    
    Args:
        task_id (str): The task ID to check
        
    Returns:
        dict: Task status information
    """
    task = celery_app.AsyncResult(task_id)
    
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'status': 'Task is pending...'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'status': task.info.get('status', ''),
            'meta': task.info
        }
    else:
        response = {
            'state': task.state,
            'status': str(task.info),
        }
    
    return response 