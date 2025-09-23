"""
Task Management API Endpoints

This module provides API endpoints for managing and monitoring Celery tasks
using the flexible task tracking system.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query, Body
from api.services.celery.socket_test_tasks import socket_test_task
from celery import Celery as _Celery
from api import config as _cfg
from api.socket.core import emit_with_log
from fastapi import Path

from api.services.celery.task_tracker import task_tracker, TaskStatus, TaskType
from api.pages.ipersona.models.task import (
    TaskResponse, 
    TaskStatisticsResponse, 
    TaskStatusOptionsResponse, 
    TaskStatusEnum,
    TargetType,
    MultiTargetRequest,
    TASK_STATUS_DESCRIPTIONS
)

router = APIRouter(prefix="/tasks", tags=["Task Management"])


@router.get("/target-types")
async def get_target_types():
    """
    Get available target types for task management.
    
    Returns a list of all supported target types that can be used
    with the /target endpoints.
    """
    target_types = [
        {
            "value": target_type.value,
            "name": target_type.name,
            "description": f"Tasks associated with {target_type.name.lower().replace('_', ' ')}"
        }
        for target_type in TargetType
    ]
    
    return {
        "target_types": target_types,
        "count": len(target_types)
    }


@router.get("/", response_model=List[TaskResponse])
async def list_tasks(
    status: Optional[TaskStatusEnum] = Query(None, description="Filter by task status"),
    target_type: Optional[str] = Query(None, description="Filter by target type"),
    limit: int = Query(50, description="Maximum number of tasks to return")
):
    """
    List all tasks with optional filtering
    
    Use the status parameter to filter tasks by status. The available options
    can be retrieved from the /tasks/status-options endpoint.
    """
    try:
        # Get all tasks
        tasks = task_tracker.get_all_tasks(limit=limit)
        
        # Apply filters
        if status:
            tasks = [task for task in tasks if task.get("status") == status.value]
        
        if target_type:
            tasks = [task for task in tasks if task.get("target_type") == target_type]
        
        return tasks
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving tasks: {str(e)}")


@router.get("/target", response_model=List[TaskResponse])
async def get_tasks_by_target(
    target_type: TargetType = Query(..., description="Target type (job_profile, challenge, session, all_user)"),
    target_id: int = Query(..., description="Target ID")
):
    """
    Get tasks for a specific target using generic target_type and target_id.
    
    This endpoint is more scalable than the previous approach and supports
    all target types defined in the TargetType enum.
    
    Examples:
    - GET /tasks/target?target_type=job_profile&target_id=123
    - GET /tasks/target?target_type=session&target_id=456
    """
    try:
        # Create target dictionary with only the specified target active
        target = {
            "job_profile_id": 0,
            "challenge_id": 0,
            "session_id": 0,
            "all_user_id": 0
        }
        target[target_type.value] = target_id
        
        # Get tasks for this target
        tasks = task_tracker.get_tasks_by_target_type(target_type.value, str(target_id))
        
        return tasks
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving tasks: {str(e)}")


@router.post("/target/multi", response_model=List[TaskResponse])
async def get_tasks_by_multiple_targets(
    request: MultiTargetRequest = Body(..., description="Multiple target criteria")
):
    """
    Get tasks that match multiple target criteria simultaneously.
    
    This endpoint allows you to filter tasks by multiple target values at once.
    For example, you can find tasks that belong to both a specific job_profile_id
    and a specific all_user_id.
    
    Target types can be:
    - Enum values: "job_profile", "challenge", "session", "all_user"
    - Arbitrary strings: "custom_target", "external_id", etc.
    
    Examples:
    - POST /tasks/target/multi
      {
        "targets": {
          "job_profile": 123,
          "all_user": 456
        }
      }
    - POST /tasks/target/multi
      {
        "targets": {
          "session": 789,
          "all_user": 101,
          "custom_target": 999
        }
      }
    """
    try:
        # Convert targets to string format
        targets_dict = {}
        for target_type, target_id in request.targets.items():
            # Convert string to enum if it matches a TargetType enum value
            if isinstance(target_type, str):
                # Try to find matching enum by value
                enum_value = None
                for enum_member in TargetType:
                    if enum_member.value == target_type:
                        enum_value = enum_member.value
                        break
                
                if enum_value:
                    # It's a valid enum value
                    targets_dict[enum_value] = target_id
                else:
                    # It's an arbitrary string
                    targets_dict[str(target_type)] = target_id
            elif isinstance(target_type, TargetType):
                # Handle actual enum instances
                targets_dict[target_type.value] = target_id
            else:
                # Handle other types
                targets_dict[str(target_type)] = target_id
        
        # Get tasks that match all specified targets
        tasks = task_tracker.get_tasks_by_multiple_targets(targets_dict)
        
        return tasks
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving tasks: {str(e)}")
        
@router.get("/statistics", response_model=TaskStatisticsResponse)
async def get_task_statistics():
    """
    Get overall task statistics
    """
    try:
        stats = task_tracker.get_task_statistics()
        return stats
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving statistics: {str(e)}")


@router.post("/socket-test")
async def enqueue_socket_test(
    job_id: str = Query("123", description="Job id used to build room name: processing_<job_id>"),
    message: str = Query("hello from api", description="Message to send in the socket_test event")
):
    """Enqueue a Celery task that emits a Socket.IO test event to the client's room.

    The room name is built as processing_<job_id>. Ensure your frontend joins that room.
    """
    try:
        room = f"processing_{job_id}"
        # Use a lightweight client to avoid app-binding issues
        _client = _Celery(broker=_cfg.cache.REDIS_URL, backend=_cfg.cache.REDIS_URL)
        task_id = _client.send_task('socket_test_task', kwargs={"room": room, "message": message}, queue='celery')
        print(f"[API] queued socket_test_task id={task_id} room={room}")
        return {"status": "queued", "task_id": str(task_id), "room": room, "event": "socket_test"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to enqueue socket test task: {str(e)}")


@router.post("/socket-direct")
async def emit_socket_direct(
    job_id: str = Query("123", description="Job id used to build room name: processing_<job_id>"),
    message: str = Query("hello-from-direct", description="Message to send in the socket_test event")
):
    """Emit socket_test directly from FastAPI to verify client join/listener."""
    try:
        room = f"processing_{job_id}"
        await emit_with_log("socket_test", {"message": "no matter what you print these", "via": "direct"}, room=room)
        return {"status": "emitted", "room": room, "event": "socket_test"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to emit directly: {str(e)}")


@router.post("/socket-test-fixed")
async def enqueue_socket_test_fixed(
    job_id: str = Query("123", description="Job id used to build room name: processing_<job_id>")
):
    """Enqueue Celery with a backend-defined message (ignores client input)."""
    try:
        room = f"processing_{job_id}"
        fixed_message = "hello-from-backend-celery"
        _client = _Celery(broker=_cfg.cache.REDIS_URL, backend=_cfg.cache.REDIS_URL)
        task_id = _client.send_task('socket_test_task', kwargs={"room": room, "message": fixed_message}, queue='celery')
        print(f"[API] queued FIXED socket_test_task id={task_id} room={room}")
        return {"status": "queued", "task_id": str(task_id), "room": room, "event": "socket_test", "message": fixed_message}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to enqueue fixed socket test task: {str(e)}")


@router.post("/socket-test-by-sid")
async def enqueue_socket_test_by_sid(
    sid: str | None = Query(None, description="Socket SID (preferred). If provided, used directly."),
    client_id: str | None = Query(None, description="Optional client id previously registered via 'register'"),
    message: str = Query("hello-from-celery-by-sid", description="Message to send in the socket_test event")
):
    """Enqueue Celery to emit to a specific client SID (no room/join needed)."""
    try:
        target = sid or client_id
        if not target:
            raise HTTPException(status_code=400, detail="Provide sid or client_id")
        _client = _Celery(broker=_cfg.cache.REDIS_URL, backend=_cfg.cache.REDIS_URL)
        task_id = _client.send_task('socket_test_task', kwargs={"room": None, "message": message, "sid": target}, queue='celery')
        print(f"[API] queued BY_SID socket_test_task id={task_id} target={target}")
        return {"status": "queued", "task_id": str(task_id), "target": target, "event": "socket_test"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to enqueue socket test by sid: {str(e)}")

@router.delete("/target")
async def delete_tasks_by_target(
    target_type: TargetType = Query(..., description="Target type (job_profile, challenge, session, all_user)"),
    target_id: int = Query(..., description="Target ID"),
    task_type: Optional[str] = Query(None, description="Specific task type to delete")
):
    """
    Delete tasks for a specific target using generic target_type and target_id.
    If task_type is provided, only delete that specific task.
    
    This endpoint is more scalable than the previous approach and supports
    all target types defined in the TargetType enum.
    
    Examples:
    - DELETE /tasks/target?target_type=job_profile&target_id=123
    - DELETE /tasks/target?target_type=session&target_id=456&task_type=audio_processing
    """
    try:
        # Create target dictionary with only the specified target active
        target = {
            "job_profile_id": 0,
            "challenge_id": 0,
            "session_id": 0,
            "all_user_id": 0
        }
        target[target_type.value] = target_id
        
        if task_type:
            # Delete specific task
            success = task_tracker.delete_task(target, task_type)
            if not success:
                raise HTTPException(status_code=404, detail="Task not found")
            return {"message": f"Task {task_type} deleted successfully"}
        else:
            # Delete all tasks for this target
            tasks = task_tracker.get_tasks_by_target_type(target_type.value, str(target_id))
            
            deleted_count = 0
            for task in tasks:
                task_type = task.get("task_type")
                if task_tracker.delete_task(target, task_type):
                    deleted_count += 1
            
            return {"message": f"Deleted {deleted_count} tasks for target {target_type.value}:{target_id}"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting tasks: {str(e)}")








 