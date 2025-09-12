"""
Task Tracking System for Celery Tasks

This module provides a flexible task tracking system that can handle
different target types (job_profile_id, challenge_id, session_id, etc.)
where only one target is active (non-zero) at a time.
"""

import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum

from api.services.redis.redis_config import RedisBase


class TaskStatus(Enum):
    """Enum for task statuses"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskType(Enum):
    """Enum for task types"""
    AUDIO_PROCESSING = "audio_processing"
    TRANSCRIPTION = "transcription"
    EVALUATION = "evaluation"
    OVERALL_EVALUATION = "overall_evaluation"


class TaskTracker:
    """
    Flexible task tracking system for Celery tasks
    """
    
    def __init__(self):
        self.redis = RedisBase()
        self.task_prefix = "task_tracker"
    
    def detect_active_target(self, target: Dict[str, Any]) -> Tuple[str, str]:
        """
        Detect which target type is active (non-zero) and return (target_type, target_id)
        Priority order: job_profile_id > challenge_id > template_id > session_id > user_id > all_user_id
        
        Args:
            target: Dict containing various ID fields
            
        Returns:
            Tuple of (target_type, target_id) for the active target
            
        Raises:
            ValueError: If no target is active
        """
        # Priority order for target selection
        priority_targets = ['job_profile_id', 'challenge_id', 'template_id', 'session_id', 'user_id', 'all_user_id']
        
        for target_type in priority_targets:
            if target_type in target and target[target_type] and target[target_type] != 0:
                return (target_type, str(target[target_type]))
        
        # If no priority target found, check all targets ending with '_id'
        active_targets = []
        for key, value in target.items():
            if key.endswith('_id') and value and value != 0:
                active_targets.append((key, str(value)))
        
        if len(active_targets) == 0:
            raise ValueError("No active target found - all IDs are zero or None")
        
        # Return the first active target if no priority target found
        return active_targets[0]
    
    def register_task(self, task_type: str, target: Dict[str, Any], 
                     metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Register a new task with automatic target detection
        
        Args:
            task_type: Type of task (e.g., 'audio_processing', 'transcription')
            target: Dict containing various ID fields (only one should be non-zero)
            metadata: Additional task metadata
            
        Returns:
            Task data dictionary
        """
        try:
            target_type, target_id = self.detect_active_target(target)
            
            # Check if task already exists to prevent duplicates
            redis_key = f"{self.task_prefix}:{target_type}:{target_id}:{task_type}"
            existing_task = self.redis.get(redis_key)
            
            if existing_task:
                # Check if existing task is in a final state (completed or failed)
                # If so, allow creating a new task
                existing_status = existing_task.get('status')
                if existing_status in ['completed', 'failed', 'cancelled']:
                    # Delete the old task to make room for the new one
                    self.redis.delete(redis_key)
                else:
                    # Task already exists and is not in final state, return existing data
                    return existing_task
            
            task_data = {
                "task_type": task_type,
                "target_type": target_type,
                "target_id": target_id,
                "status": TaskStatus.PENDING.value,
                "created_at": datetime.utcnow().isoformat(),
                "started_at": None,
                "completed_at": None,
                "error_message": None,
                "progress": 0,
                "metadata": metadata or {},
                "all_targets": target  # Store all targets for reference
            }
            
            # Store in Redis
            self.redis.set(redis_key, task_data)
            
            # Also store in a general task list (only if not already there)
            task_list_key = f"{self.task_prefix}:all_tasks"
            existing_tasks = self.redis.get(task_list_key) or []
            if redis_key not in existing_tasks:
                existing_tasks.append(redis_key)
                self.redis.set(task_list_key, existing_tasks)
            
            return task_data
            
        except ValueError as e:
            raise ValueError(f"Invalid target configuration: {e}")
    
    def update_task_status(self, target: Dict[str, Any], task_type: str, 
                          status: TaskStatus, progress: Optional[int] = None, 
                          error_message: Optional[str] = None) -> bool:
        """
        Update task status and progress
        
        Args:
            target: Dict containing target information
            task_type: Type of task
            status: New status
            progress: Progress percentage (0-100)
            error_message: Error message if status is failed
            
        Returns:
            True if update was successful, False otherwise
        """
        try:
            target_type, target_id = self.detect_active_target(target)
            redis_key = f"{self.task_prefix}:{target_type}:{target_id}:{task_type}"
            
            task_data = self.redis.get(redis_key)
            if not task_data:
                return False
            
            # Update status and timestamps
            task_data["status"] = status.value
            task_data["progress"] = progress or task_data.get("progress", 0)
            
            if status == TaskStatus.PROCESSING and not task_data.get("started_at"):
                task_data["started_at"] = datetime.utcnow().isoformat()
            elif status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
                task_data["completed_at"] = datetime.utcnow().isoformat()
            
            if error_message:
                task_data["error_message"] = error_message
            
            # Save updated task data
            self.redis.set(redis_key, task_data)
            return True
            
        except ValueError as e:
            print(f"Error updating task status: {e}")
            return False
    
    def get_task_by_target(self, target: Dict[str, Any], task_type: str) -> Optional[Dict[str, Any]]:
        """
        Get task data for a specific target and task type
        
        Args:
            target: Dict containing target information
            task_type: Type of task
            
        Returns:
            Task data dictionary or None if not found
        """
        try:
            target_type, target_id = self.detect_active_target(target)
            redis_key = f"{self.task_prefix}:{target_type}:{target_id}:{task_type}"
            return self.redis.get(redis_key)
        except ValueError:
            return None
    
    def get_tasks_by_target_type(self, target_type: str, target_id: str) -> List[Dict[str, Any]]:
        """
        Get all tasks for a specific target type and ID
        
        Args:
            target_type: Type of target (e.g., 'job_profile_id')
            target_id: Target ID
            
        Returns:
            List of task data dictionaries sorted by created_at (newest first)
        """
        tasks = []
        task_list_key = f"{self.task_prefix}:all_tasks"
        task_keys = self.redis.get(task_list_key) or []
        
        # Filter keys that match the target pattern
        pattern = f"{self.task_prefix}:{target_type}:{target_id}:"
        matching_keys = [key for key in task_keys if key.startswith(pattern)]
        
        # Get task data for matching keys
        for key in matching_keys:
            task_data = self.redis.get(key)
            if task_data:
                tasks.append(task_data)
        
        # Sort by created_at timestamp (newest first)
        tasks.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        return tasks
    
    def get_tasks_by_multiple_targets(self, targets: Dict[str, int]) -> List[Dict[str, Any]]:
        """
        Get all tasks that match multiple target criteria
        
        Args:
            targets: Dict containing target type and ID pairs (e.g., {'job_profile_id': 123, 'all_user_id': 456})
            
        Returns:
            List of task data dictionaries sorted by created_at (newest first)
        """
        tasks = []
        task_list_key = f"{self.task_prefix}:all_tasks"
        task_keys = self.redis.get(task_list_key) or []
        
        # Get all tasks first
        all_tasks = []
        for key in task_keys:
            task_data = self.redis.get(key)
            if task_data:
                all_tasks.append(task_data)
        
        # Filter tasks that match ALL specified targets
        for task in all_tasks:
            task_targets = task.get("all_targets", {})
            matches_all = True
            
            for target_type, target_id in targets.items():
                # Check if the task has this target and it matches
                if (target_type not in task_targets or 
                    task_targets[target_type] != target_id):
                    matches_all = False
                    break
            
            if matches_all:
                tasks.append(task)
        
        # Sort by created_at timestamp (newest first)
        tasks.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        return tasks
    
    def get_tasks_by_status(self, status: TaskStatus) -> List[Dict[str, Any]]:
        """
        Get all tasks with a specific status
        
        Args:
            status: Task status to filter by
            
        Returns:
            List of task data dictionaries sorted by created_at (newest first)
        """
        tasks = []
        task_list_key = f"{self.task_prefix}:all_tasks"
        task_keys = self.redis.get(task_list_key) or []
        
        for key in task_keys:
            task_data = self.redis.get(key)
            if task_data and task_data.get("status") == status.value:
                tasks.append(task_data)
        
        # Sort by created_at timestamp (newest first)
        tasks.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        return tasks
    
    def get_all_tasks(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get all tasks (limited by count)
        
        Args:
            limit: Maximum number of tasks to return
            
        Returns:
            List of task data dictionaries sorted by created_at (newest first)
        """
        tasks = []
        task_list_key = f"{self.task_prefix}:all_tasks"
        task_keys = self.redis.get(task_list_key) or []
        
        for key in task_keys:
            task_data = self.redis.get(key)
            if task_data:
                tasks.append(task_data)
        
        # Sort by created_at timestamp (newest first) and apply limit
        tasks.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return tasks[:limit]
    
    def delete_task(self, target: Dict[str, Any], task_type: str) -> bool:
        """
        Delete a task
        
        Args:
            target: Dict containing target information
            task_type: Type of task
            
        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            target_type, target_id = self.detect_active_target(target)
            redis_key = f"{self.task_prefix}:{target_type}:{target_id}:{task_type}"
            
            # Remove from Redis
            self.redis.delete(redis_key)
            
            # Remove from task list
            task_list_key = f"{self.task_prefix}:all_tasks"
            task_keys = self.redis.get(task_list_key) or []
            if redis_key in task_keys:
                task_keys.remove(redis_key)
                self.redis.set(task_list_key, task_keys)
            
            return True
            
        except ValueError:
            return False
    
    def cleanup_duplicate_tasks(self) -> int:
        """
        Clean up duplicate tasks that might exist due to previous bugs
        
        Returns:
            Number of duplicates removed
        """
        removed_count = 0
        task_list_key = f"{self.task_prefix}:all_tasks"
        task_keys = self.redis.get(task_list_key) or []
        
        # Track unique tasks by their key
        unique_tasks = []
        seen_keys = set()
        
        for key in task_keys:
            if key not in seen_keys:
                unique_tasks.append(key)
                seen_keys.add(key)
            else:
                # This is a duplicate, remove it
                self.redis.delete(key)
                removed_count += 1
        
        # Update the task list with only unique tasks
        if removed_count > 0:
            self.redis.set(task_list_key, unique_tasks)
        
        return removed_count
    
    def create_target_dict(self, job_profile_id: Optional[int] = None, 
                          challenge_id: Optional[int] = None, 
                          session_id: Optional[int] = None,
                          user_id: Optional[int] = None,
                          all_user_id: Optional[int] = None,
                          template_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Create a target dictionary for task tracking
        
        Args:
            job_profile_id: Job profile ID
            challenge_id: Challenge ID
            session_id: Session ID
            user_id: User ID
            all_user_id: All user ID
            template_id: Template ID
            
        Returns:
            Target dictionary with all fields (only one should be non-zero)
        """
        return {
            "job_profile_id": job_profile_id or 0,
            "challenge_id": challenge_id or 0,
            "session_id": session_id or 0,
            "user_id": user_id or 0,
            "all_user_id": all_user_id or 0,
            "template_id": template_id or 0
        }
    
    def create_target_dict_from_data(self, target_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a target dictionary from arbitrary target data
        
        Args:
            target_data: Dictionary containing target information
            
        Returns:
            Target dictionary with all known targets and any additional targets
        """
        # Start with default values for known targets
        target_dict = {
            "job_profile_id": 0,
            "challenge_id": 0,
            "session_id": 0,
            "user_id": 0,
            "all_user_id": 0,
            "template_id": 0
        }
        
        # Update with provided values
        for key, value in target_data.items():
            if value is not None and value != 0:
                target_dict[key] = value
        
        return target_dict
    
    def update_task_progress(self, target: Dict[str, Any], task_type: str, 
                           progress: int, status: Optional[TaskStatus] = None, 
                           error_message: Optional[str] = None) -> bool:
        """
        Update task progress with optional status change
        
        Args:
            target: Dict containing target information
            task_type: Type of task
            progress: Progress percentage (0-100)
            status: Optional status to set (if None, keeps current status)
            error_message: Error message if status is failed
            
        Returns:
            True if update was successful, False otherwise
        """
        try:
            target_type, target_id = self.detect_active_target(target)
            redis_key = f"{self.task_prefix}:{target_type}:{target_id}:{task_type}"
            
            task_data = self.redis.get(redis_key)
            if not task_data:
                return False
            
            # Update progress
            task_data["progress"] = progress
            
            # Update status if provided
            if status:
                task_data["status"] = status.value
                
                # Update timestamps based on status
                if status == TaskStatus.PROCESSING and not task_data.get("started_at"):
                    task_data["started_at"] = datetime.utcnow().isoformat()
                elif status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
                    task_data["completed_at"] = datetime.utcnow().isoformat()
            
            # Update error message if provided
            if error_message:
                task_data["error_message"] = error_message
            
            # Save updated task data
            self.redis.set(redis_key, task_data)
            return True
            
        except ValueError as e:
            print(f"Error updating task progress: {e}")
            return False
    
    def get_task_statistics(self) -> Dict[str, Any]:
        """
        Get overall task statistics
        
        Returns:
            Dictionary with task statistics
        """
        all_tasks = self.get_all_tasks(limit=1000)  # Get more tasks for stats
        
        stats = {
            "total_tasks": len(all_tasks),
            "by_status": {},
            "by_type": {},
            "by_target_type": {}
        }
        
        for task in all_tasks:
            # Count by status
            status = task.get("status", "unknown")
            stats["by_status"][status] = stats["by_status"].get(status, 0) + 1
            
            # Count by task type
            task_type = task.get("task_type", "unknown")
            stats["by_type"][task_type] = stats["by_type"].get(task_type, 0) + 1
            
            # Count by target type
            target_type = task.get("target_type", "unknown")
            stats["by_target_type"][target_type] = stats["by_target_type"].get(target_type, 0) + 1
        
        return stats


# Global task tracker instance
task_tracker = TaskTracker() 