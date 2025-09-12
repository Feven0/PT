from celery import current_task
from api.services.celery.celery_config import celery_app
import asyncio
import json
import logging
import time
from typing import Optional
import redis

logger = logging.getLogger(__name__)

# Create a single Redis connection for all tasks
def get_redis_client():
    """Get Redis client with proper error handling using api.config"""
    try:
        from api import config
        return redis.Redis(
            host=config.cache.REDIS_HOST,
            port=config.cache.REDIS_PORT,
            password=config.cache.REDIS_PASSWORD,
            decode_responses=True,  # Enable for pub/sub
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True,
            health_check_interval=30
        )
    except Exception as e:
        logger.error(f"Failed to create Redis client: {e}")
        return None

@celery_app.task(bind=True, name='process_audio_and_save_external_celery')
def process_audio_and_save_external_celery(self, filename, content_type, contents, job_profile_id, challenge_id, all_user_id, external, run_stage):
    """
    Celery task for processing audio and saving external data
    This is a replica of the existing process_audio_and_save_external function
    """
    logger.info(f"🎵 [CELERY TASK] Starting audio processing for file: {filename}")
    logger.info(f"🎵 [CELERY TASK] Task ID: {self.request.id}")
    logger.info(f"🎵 [CELERY TASK] Job Profile ID: {job_profile_id}")
    logger.info(f"🎵 [CELERY TASK] File content size: {len(contents)} bytes")
    
    try:
        # Get Redis client
        redis_client = get_redis_client()
        if not redis_client:
            raise Exception("Failed to connect to Redis")
        
        # Update task status
        task_status = {
            "status": "processing",
            "message": "Starting audio processing...",
            "job_profile_id": job_profile_id
        }
        redis_client.setex(f"task_status_{self.request.id}", 3600, json.dumps(task_status))
        
        # Publish task started notification to Redis
        try:
            notification = {
                "type": "task_started",
                "task_id": self.request.id,
                "job_profile_id": job_profile_id,
                "filename": filename,
                "timestamp": time.time()
            }
            redis_client.publish("celery_notifications", json.dumps(notification))
            logger.info(f"🎵 [CELERY TASK] Published task started notification")
        except Exception as e:
            logger.warning(f"🎵 [CELERY TASK] Failed to publish notification: {e}")
        
        logger.info(f"🎵 [CELERY TASK] Processing file content directly")
        
        # Import here to avoid circular imports
        from api.pages.ipersona.routers.ipersona_routes import process_audio_and_save_external
        
        # Use asyncio.run() instead of creating new event loop
        # This is the recommended way for Celery tasks
        # Call the original function directly (no WebSocket handling needed)
        result = asyncio.run(
            process_audio_and_save_external(
                filename, content_type, contents, job_profile_id, 
                challenge_id, all_user_id, external, run_stage
            )
        )
        
        logger.info(f"🎵 [CELERY TASK] Audio processing completed successfully!")
        
        # Extract the actual data from JSONResponse
        if hasattr(result, 'body'):
            # If it's a JSONResponse, extract the body
            import json as json_module
            result_data = json_module.loads(result.body.decode('utf-8'))
        else:
            # If it's already a dict, use it directly
            result_data = result
        
        # Update task status to completed
        task_status = {
            "status": "completed",
            "message": "Audio processing completed successfully",
            "job_profile_id": job_profile_id,
            "result": result_data
        }
        redis_client.setex(f"task_status_{self.request.id}", 3600, json.dumps(task_status))
        
        # Publish task completed notification to Redis
        try:
            notification = {
                "type": "task_completed",
                "task_id": self.request.id,
                "job_profile_id": job_profile_id,
                "filename": filename,
                "timestamp": time.time()
            }
            redis_client.publish("celery_notifications", json.dumps(notification))
            logger.info(f"🎵 [CELERY TASK] Published task completed notification")
        except Exception as e:
            logger.warning(f"🎵 [CELERY TASK] Failed to publish completion notification: {e}")
        
        return result_data
            
    except Exception as e:
        logger.error(f"🎵 [CELERY TASK] Error: {str(e)}", exc_info=True)
        
        # Update task status to failed
        try:
            redis_client = get_redis_client()
            if redis_client:
                task_status = {
                    "status": "failed",
                    "message": str(e),
                    "job_profile_id": job_profile_id
                }
                redis_client.setex(f"task_status_{self.request.id}", 3600, json.dumps(task_status))
        except:
            pass  # Don't fail if Redis is not available
        
        raise self.retry(exc=e, countdown=60, max_retries=3)
    
    finally:
        # No cleanup needed since we're not using temporary files
        logger.info(f"🎵 [CELERY TASK] Task completed - no cleanup needed")

@celery_app.task(bind=True, name='process_upload_external_files_celery')
def process_upload_external_files_celery(self, question_filename, question_content_type, question_contents, 
                                        answer_filename, answer_content_type, answer_contents,
                                        job_profile_id, challenge_id, all_user_id, external, run_stage):
    """
    Celery task for processing dual file uploads
    This is a replica of the existing process_upload_external_files function
    """
    logger.info(f"📁 [CELERY TASK] Starting dual file processing...")
    logger.info(f"📁 [CELERY TASK] Task ID: {self.request.id}")
    logger.info(f"📁 [CELERY TASK] Question file: {question_filename}")
    logger.info(f"📁 [CELERY TASK] Answer file: {answer_filename}")
    logger.info(f"📁 [CELERY TASK] Job Profile ID: {job_profile_id}")
    
    try:
        # Get Redis client
        redis_client = get_redis_client()
        if not redis_client:
            raise Exception("Failed to connect to Redis")
        
        # Update task status
        task_status = {
            "status": "processing",
            "message": "Starting dual file processing...",
            "job_profile_id": job_profile_id
        }
        redis_client.setex(f"task_status_{self.request.id}", 3600, json.dumps(task_status))
        
        logger.info(f"📁 [CELERY TASK] Calling existing process_upload_external_files function...")
        
        # Import here to avoid circular imports
        from api.pages.ipersona.routers.ipersona_routes import process_upload_external_files
        
        # Use asyncio.run() instead of creating new event loop
        # This is the recommended way for Celery tasks
        result = asyncio.run(
            process_upload_external_files(
                question_filename, question_content_type, question_contents,
                answer_filename, answer_content_type, answer_contents,
                job_profile_id, challenge_id, all_user_id, external, run_stage
            )
        )
        
        logger.info(f"📁 [CELERY TASK] Dual file processing completed successfully!")
        
        # Update task status to completed
        task_status = {
            "status": "completed",
            "message": "Dual file processing completed successfully",
            "job_profile_id": job_profile_id,
            "result": result
        }
        redis_client.setex(f"task_status_{self.request.id}", 3600, json.dumps(task_status))
        
        return result
            
    except Exception as e:
        logger.error(f"📁 [CELERY TASK] Error: {str(e)}", exc_info=True)
        
        # Update task status to failed
        try:
            redis_client = get_redis_client()
            if redis_client:
                task_status = {
                    "status": "failed",
                    "message": str(e),
                    "job_profile_id": job_profile_id
                }
                redis_client.setex(f"task_status_{self.request.id}", 3600, json.dumps(task_status))
        except:
            pass  # Don't fail if Redis is not available
        
        raise self.retry(exc=e, countdown=60, max_retries=3)

def get_task_status(task_id: str) -> Optional[dict]:
    """Get the status of a Celery task from Redis"""
    try:
        redis_client = get_redis_client()
        if not redis_client:
            return None
        
        data = redis_client.get(f"task_status_{task_id}")
        return json.loads(data) if data else None
    except:
        return None
