"""Task context for agent operations."""
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid

from pydantic import Field, ConfigDict
from ..config.models import BaseConfigModel

class TaskContext(BaseConfigModel):
    """Context for a task execution."""
    description: str = Field(description="Description of the task to execute")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional task metadata")
    state: str = Field(default="idle", description="Current state of the task")
    state_metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional state metadata")
    tool_calls: List[Dict[str, Any]] = Field(default_factory=list, description="History of tool calls made")
    files_seen: List[str] = Field(default_factory=list, description="Files accessed during task execution")
    search_results: List[Dict[str, Any]] = Field(default_factory=list, description="Search results from task execution")
    edits_made: List[Dict[str, Any]] = Field(default_factory=list, description="Code edits made during task execution")
    commands_run: List[Dict[str, Any]] = Field(default_factory=list, description="Commands executed during task")
    errors: List[Dict[str, Any]] = Field(default_factory=list, description="Errors encountered during execution")
    conversation_history: List[Dict[str, Any]] = Field(default_factory=list, description="History of conversation messages")
    start_time: datetime = Field(default_factory=datetime.now, description="When the task started")
    last_update: datetime = Field(default_factory=datetime.now, description="When the task was last updated")
    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier for the task")
    created_at: datetime = Field(default_factory=datetime.now, description="When the task was created")
    completed_at: Optional[datetime] = Field(default=None, description="When the task was completed")
    messages: List[Dict[str, Any]] = Field(default_factory=list, description="Messages exchanged during task execution")
    actions: List[Dict[str, Any]] = Field(default_factory=list, description="Actions taken during task execution")
    workspace_path: Optional[str] = Field(default=None, description="Path to the workspace")

    model_config = ConfigDict(
        extra='allow'  # Allow extra fields
    )

    def update_state(self, new_state: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Update task state with metadata."""
        self.state = new_state
        if metadata:
            self.state_metadata.update(metadata)
        self.last_update = datetime.now()

    def add_tool_call(self, tool_call: Dict[str, Any]) -> None:
        """Add a tool call to history."""
        self.tool_calls.append({
            **tool_call,
            "timestamp": datetime.now().isoformat()
        })
        self.last_update = datetime.now()

    def add_error(self, error: Dict[str, Any]) -> None:
        """Add an error to history."""
        self.errors.append({
            **error,
            "timestamp": datetime.now().isoformat(),
            "state": self.state
        })
        self.last_update = datetime.now()

    def add_message(self, message: Dict[str, Any]) -> None:
        """Add a message to history."""
        self.messages.append({
            **message,
            "timestamp": datetime.now().isoformat()
        })
        self.last_update = datetime.now()

    def complete(self) -> None:
        """Mark task as completed."""
        self.completed_at = datetime.now()
        self.last_update = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary for backward compatibility."""
        return {
            "task_id": self.task_id,
            "description": self.description,
            "metadata": self.metadata,
            "state": self.state,
            "state_metadata": self.state_metadata,
            "tool_calls": self.tool_calls,
            "files_seen": self.files_seen,
            "search_results": self.search_results,
            "edits_made": self.edits_made,
            "commands_run": self.commands_run,
            "errors": self.errors,
            "conversation_history": self.conversation_history,
            "messages": self.messages,
            "workspace_path": self.workspace_path,
            "start_time": self.start_time.isoformat(),
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "last_update": self.last_update.isoformat()
        } 