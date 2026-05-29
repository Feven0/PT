"""Error handling for the backend system."""
from typing import Dict, Any, Optional
from datetime import datetime, timezone

class BackendError(Exception):
    """Base error class for backend errors."""
    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.code = code
        self.details = details or {}
        self.timestamp = datetime.now(timezone.utc)
        
        # Create a more complete error message
        error_msg = f"[{code}] {message}"
        if details:
            error_msg += f"\nDetails: {details}"
        error_msg += f"\nTimestamp: {self.timestamp.isoformat()}"
        
        self.message = error_msg
        super().__init__(error_msg)
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary."""
        return {
            "code": self.code,
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp.isoformat()
        }

BaseError = BackendError

class AgentError(BackendError):
    """Agent-related errors."""
    def __init__(
        self,
        message: str,
        code: str = "AGENT_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, code=code, details=details)

class ChainError(BackendError):
    """Chain-related errors."""
    def __init__(
        self,
        message: str,
        code: str = "CHAIN_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, code=code, details=details)

class ToolError(BackendError):
    """Tool execution errors."""
    def __init__(
        self,
        message: str,
        code: str = "TOOL_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, code=code, details=details)

class ValidationError(BackendError):
    """Validation errors."""
    def __init__(
        self,
        message: str,
        code: str = "VALIDATION_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, code=code, details=details)

class ChatError(BackendError):
    """Chat-related errors."""
    def __init__(
        self,
        message: str,
        code: str = "CHAT_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, code=code, details=details)

class ResourceError(BackendError):
    """Resource-related errors."""
    def __init__(
        self,
        message: str,
        code: str = "RESOURCE_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, code=code, details=details)

# Error handlers
def handle_agent_error(error: Exception, context: Dict[str, Any]) -> AgentError:
    """Handle agent errors."""
    if isinstance(error, AgentError):
        return error
        
    return AgentError(
        message=str(error),
        details={
            "context": context,
            "error_type": type(error).__name__
        }
    )

def handle_chain_error(error: Exception, context: Dict[str, Any]) -> ChainError:
    """Handle chain errors."""
    if isinstance(error, ChainError):
        return error
        
    return ChainError(
        message=str(error),
        details={
            "context": context,
            "error_type": type(error).__name__
        }
    )

def handle_tool_error(error: Exception, context: Dict[str, Any]) -> ToolError:
    """Handle tool execution errors."""
    if isinstance(error, ToolError):
        return error
        
    return ToolError(
        message=str(error),
        details={
            "context": context,
            "error_type": type(error).__name__
        }
    )

def handle_chat_error(error: Exception, context: Dict[str, Any]) -> ChatError:
    """Handle chat errors."""
    if isinstance(error, ChatError):
        return error
        
    return ChatError(
        message=str(error),
        details={
            "context": context,
            "error_type": type(error).__name__
        }
    ) 