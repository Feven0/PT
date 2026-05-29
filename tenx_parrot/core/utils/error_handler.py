"""Error handling and recovery for the tool system."""
from typing import Dict, Any, Optional, List, Callable, Awaitable
import logging
import traceback
from datetime import datetime
from dataclasses import dataclass, field
from core.base.manager import BaseManager
from core.errors.exceptions import BaseError

logger = logging.getLogger(__name__)

# Type alias for error handlers
ErrorHandlerFunc = Callable[[BaseError, Dict[str, Any]], Awaitable[None]]

@dataclass
class ErrorRecord:
    """Record of an error occurrence."""
    error_id: str
    error_type: str
    message: str
    timestamp: datetime
    traceback: str
    context: Dict[str, Any] = field(default_factory=dict)
    handled: bool = False
    resolution: Optional[str] = None

class ErrorHandler(BaseManager):
    """Manages error handling and recovery."""
    
    def __init__(self, max_errors: int = 1000):
        """Initialize error handler."""
        super().__init__()
        self.max_errors = max_errors
        self.errors: Dict[str, ErrorRecord] = {}
        self.error_handlers: Dict[str, List[ErrorHandlerFunc]] = {}
        
    async def initialize(self) -> None:
        """Initialize the error handler."""
        self.initialized = True
        logger.info("Error handler initialized")
        
    async def cleanup(self) -> None:
        """Clean up error handler."""
        self.errors.clear()
        self.error_handlers.clear()
        self.initialized = False
        logger.info("Error handler cleaned up")
        
    def register_handler(
        self,
        error_type: str,
        handler: ErrorHandlerFunc
    ) -> None:
        """Register an error handler."""
        if error_type not in self.error_handlers:
            self.error_handlers[error_type] = []
        self.error_handlers[error_type].append(handler)
        logger.info(f"Registered handler for {error_type}")
        
    async def handle_error(
        self,
        error: BaseError,
        context: Optional[Dict[str, Any]] = None
    ) -> ErrorRecord:
        """Handle an error."""
        error_id = f"err_{len(self.errors)}"
        record = ErrorRecord(
            error_id=error_id,
            error_type=error.__class__.__name__,
            message=str(error),
            timestamp=datetime.now(),
            traceback=traceback.format_exc(),
            context=context or {}
        )
        
        self.errors[error_id] = record
        
        # Enforce max errors limit
        if len(self.errors) > self.max_errors:
            oldest = sorted(
                self.errors.items(),
                key=lambda x: x[1].timestamp
            )[0][0]
            del self.errors[oldest]
            
        # Call error handlers
        handlers = self.error_handlers.get(record.error_type, [])
        handlers.extend(self.error_handlers.get("*", []))
        
        for handler in handlers:
            try:
                await handler(error, context or {})
                record.handled = True
            except Exception as e:
                logger.error(f"Error in error handler: {e}")
                
        if not record.handled:
            logger.error(
                f"Unhandled {record.error_type}: {record.message}\n"
                f"{record.traceback}"
            )
            
        return record
        
    def get_error(self, error_id: str) -> Optional[ErrorRecord]:
        """Get error record by ID."""
        return self.errors.get(error_id)
        
    def list_errors(
        self,
        error_type: Optional[str] = None,
        handled_only: bool = False,
        unhandled_only: bool = False
    ) -> List[ErrorRecord]:
        """List error records."""
        errors = list(self.errors.values())
        
        if error_type:
            errors = [e for e in errors if e.error_type == error_type]
            
        if handled_only:
            errors = [e for e in errors if e.handled]
        elif unhandled_only:
            errors = [e for e in errors if not e.handled]
            
        return sorted(errors, key=lambda e: e.timestamp, reverse=True)
        
    def clear_errors(
        self,
        error_type: Optional[str] = None,
        handled_only: bool = False
    ) -> None:
        """Clear error records."""
        if error_type:
            self.errors = {
                id: record
                for id, record in self.errors.items()
                if record.error_type != error_type
            }
        elif handled_only:
            self.errors = {
                id: record
                for id, record in self.errors.items()
                if not record.handled
            }
        else:
            self.errors.clear()
            
    def set_resolution(
        self,
        error_id: str,
        resolution: str
    ) -> None:
        """Set resolution for an error."""
        if error_id in self.errors:
            self.errors[error_id].resolution = resolution
            self.errors[error_id].handled = True 