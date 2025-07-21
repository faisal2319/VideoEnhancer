from fastapi import APIRouter, Query, HTTPException, UploadFile, File, WebSocket, WebSocketDisconnect
from typing import Optional
import logging
import os
import sys
import shutil
from datetime import datetime
import asyncio

# Add the parent directory to the path so we can import from shared
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.celery_app import celery_app
from shared.minio_client import get_minio_client
import uuid
from shared.redis_client import redis_client

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/test")
async def test_route():
    """Basic test endpoint"""
    logger.info("Test route accessed")
    return {"message": "Test route working!", "status": "success"}

@router.get("/echo")
async def echo_route(message: Optional[str] = Query(None, description="Message to echo back")):
    """Echo endpoint that returns the provided message"""
    logger.info(f"Echo route accessed with message: {message}")
    return {
        "message": message or "No message provided",
        "echo": True,
        "status": "success"
    }

@router.get("/status")
async def status_route():
    """Status endpoint with some system info"""
    logger.info("Status route accessed")
    return {
        "service": "Video Quality Enhancer API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": ["/test", "/echo", "/status", "/enhance-video", "/task-status"]
    }

@router.post("/enhance-video")
async def enhance_video(file: UploadFile = File(...)):
    """
    Upload and trigger video enhancement pipeline as a Celery task
    
    Args:
        file (UploadFile): The video file to enhance
        
    Returns:
        dict: Task information including task ID
    """
    try:
        logger.info(f"Received video upload: {file.filename}")
        
        # Validate file type
        if not file.content_type.startswith("video/"):
            raise HTTPException(status_code=400, detail="File must be a video")
        
        # Generate a unique filename for MinIO
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        minio_filename = f"{timestamp}_{unique_id}_{file.filename}"
        minio_bucket = "videos"
        
        # Upload the file to MinIO
        minio_client = get_minio_client()
        minio_client.upload_fileobj(
            file.file,
            minio_bucket,
            minio_filename,
            ExtraArgs={"ContentType": file.content_type}
        )
        logger.info(f"Video uploaded to MinIO: {minio_bucket}/{minio_filename}")
        
        # The path to send to the ML task is the MinIO object path
        minio_object_path = f"{minio_bucket}/{minio_filename}"
        
        # Submit the task to Celery using celery_app
        task = celery_app.send_task('ml.tasks.run_pipeline_task', args=[minio_object_path])
        
        logger.info(f"Task submitted with ID: {task.id}")
        
        return {
            "status": "success",
            "message": "Video enhancement task submitted",
            "task_id": task.id,
            "minio_object_path": minio_object_path,
            "original_filename": file.filename,
            "task_status_url": f"/api/v1/task-status/{task.id}"
        }
        
    except Exception as e:
        logger.error(f"Failed to submit enhancement task: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to submit task: {str(e)}")

@router.get("/task-status/{task_id}")
async def get_task_status_endpoint(task_id: str):
    """
    Get the status of a running task
    
    Args:
        task_id (str): The task ID to check
        
    Returns:
        dict: Task status information
    """
    try:
        logger.info(f"Checking status for task: {task_id}")
        
        # Get task status using celery_app
        status_result = celery_app.send_task('ml.tasks.get_task_status', args=[task_id])
        status = status_result.get()
        
        # If task is completed successfully, include the output video path
        response = {
            "task_id": task_id,
            "status": status,
            "progress": status.get('meta', {}).get('progress_percent', 0) if status.get('meta') else 0,
            "step": status.get('meta', {}).get('step', 'UNKNOWN') if status.get('meta') else 'UNKNOWN'
        }
        
        # If task is completed successfully, include the enhanced video path
        if status.get('state') == 'SUCCESS':
            output_path = status.get('meta', {}).get('output_path', 'ml_output/reconstructed.mp4')
            if os.path.exists(output_path):
                response["enhanced_video_path"] = output_path
                response["enhanced_video_url"] = f"/api/v1/video/{task_id}"
        
        return response
        
    except Exception as e:
        logger.error(f"Failed to get task status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get task status: {str(e)}")

@router.get("/video/{task_id}")
async def get_enhanced_video(task_id: str):
    """
    Get the enhanced video file for a completed task
    
    Args:
        task_id (str): The task ID
        
    Returns:
        FileResponse: The enhanced video file
    """
    try:
        # Get task status to find the output path
        status_result = celery_app.send_task('ml.tasks.get_task_status', args=[task_id])
        status = status_result.get()
        
        if status.get('state') != 'SUCCESS':
            raise HTTPException(status_code=404, detail="Task not completed or failed")
        
        output_path = status.get('meta', {}).get('output_path', 'ml_output/reconstructed.mp4')
        
        if not os.path.exists(output_path):
            raise HTTPException(status_code=404, detail="Enhanced video not found")
        
        # Return the video file
        from fastapi.responses import FileResponse
        return FileResponse(
            path=output_path,
            media_type="video/mp4",
            filename=f"enhanced_video_{task_id}.mp4"
        )
        
    except Exception as e:
        logger.error(f"Failed to get enhanced video: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get enhanced video: {str(e)}") 

@router.websocket("/ws/video/{task_id}")
async def websocket_video_updates(websocket: WebSocket, task_id: str):
    """
    WebSocket endpoint for real-time video enhancement task updates
    """
    await websocket.accept()
    pubsub = redis_client.client.pubsub()
    channel = f"task_updates:{task_id}"
    pubsub.subscribe(channel)
    try:
        while True:
            message = pubsub.get_message(timeout=1.0)
            if message and message['type'] == 'message':
                try:
                    await websocket.send_text(message['data'])
                except Exception as e:
                    # If sending fails, break and cleanup
                    break
            await asyncio.sleep(0.1)
    except WebSocketDisconnect:
        pass
    finally:
        pubsub.unsubscribe(channel)
        pubsub.close()
        await websocket.close() 