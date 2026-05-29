"""Custom exceptions for the application."""
from typing import Optional, Dict, Any
from datetime import datetime, timezone


class BackendError(Exception):
    """Base error class for backend errors."""
    
    def __init__(
        self,
        message: str,
        code: str = "backend_error",
        details: Optional[Dict[str, Any]] = None,
        http_status: int = 500
    ):
        """Initialize error.
        
        Args:
            message: Error message
            code: Error code
            details: Additional error details
            http_status: HTTP status code
        """
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}
        self.http_status = http_status
        self.timestamp = datetime.now(timezone.utc)

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary."""
        return {
            "code": self.code,
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp.isoformat()
        }


class ServiceError(BackendError):
    """Base class for service-level errors."""
    pass


class ValidationError(ServiceError):
    """Validation error."""
    
    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Optional[Any] = None,
        **kwargs: Any
    ):
        """Initialize validation error."""
        details = kwargs.pop("details", {})
        if field:
            details["field"] = field
        if value:
            details["value"] = value
            
        super().__init__(
            message=message,
            code="validation_error",
            details=details,
            http_status=400,
            **kwargs
        )


class AuthenticationError(ServiceError):
    """Authentication error."""
    
    def __init__(self, message: str, **kwargs: Any):
        """Initialize authentication error."""
        super().__init__(
            message=message,
            code="authentication_error",
            http_status=401,
            **kwargs
        )


class AuthorizationError(ServiceError):
    """Authorization error."""
    
    def __init__(self, message: str, **kwargs: Any):
        """Initialize authorization error."""
        super().__init__(
            message=message,
            code="authorization_error",
            http_status=403,
            **kwargs
        )


class NotFoundError(ServiceError):
    """Resource not found error."""
    
    def __init__(
        self,
        message: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        **kwargs: Any
    ):
        """Initialize not found error."""
        details = kwargs.pop("details", {})
        if resource_type:
            details["resource_type"] = resource_type
        if resource_id:
            details["resource_id"] = resource_id
            
        super().__init__(
            message=message,
            code="not_found",
            details=details,
            http_status=404,
            **kwargs
        )


class StateError(ServiceError):
    """State-related error."""
    
    def __init__(
        self,
        message: str,
        current_state: Optional[str] = None,
        target_state: Optional[str] = None,
        **kwargs: Any
    ):
        """Initialize state error."""
        details = kwargs.pop("details", {})
        if current_state:
            details["current_state"] = current_state
        if target_state:
            details["target_state"] = target_state
            
        super().__init__(
            message=message,
            code="state_error",
            details=details,
            http_status=409,
            **kwargs
        )


class WebSocketError(ServiceError):
    """WebSocket-related error."""
    
    def __init__(
        self,
        message: str,
        connection_id: Optional[str] = None,
        event_type: Optional[str] = None,
        **kwargs: Any
    ):
        """Initialize WebSocket error."""
        details = kwargs.pop("details", {})
        if connection_id:
            details["connection_id"] = connection_id
        if event_type:
            details["event_type"] = event_type
            
        super().__init__(
            message=message,
            code="websocket_error",
            details=details,
            http_status=500,
            **kwargs
        )


class SessionError(ServiceError):
    """Session-related error."""
    
    def __init__(
        self,
        message: str,
        session_id: Optional[str] = None,
        operation: Optional[str] = None,
        **kwargs: Any
    ):
        """Initialize session error."""
        details = kwargs.pop("details", {})
        if session_id:
            details["session_id"] = session_id
        if operation:
            details["operation"] = operation
            
        super().__init__(
            message=message,
            code="session_error",
            details=details,
            http_status=500,
            **kwargs
        )


class DatabaseError(ServiceError):
    """Database-related error."""
    
    def __init__(
        self,
        message: str,
        operation: Optional[str] = None,
        table: Optional[str] = None,
        **kwargs: Any
    ):
        """Initialize database error."""
        details = kwargs.pop("details", {})
        if operation:
            details["operation"] = operation
        if table:
            details["table"] = table
            
        super().__init__(
            message=message,
            code="database_error",
            details=details,
            http_status=500,
            **kwargs
        )


class ExternalServiceError(ServiceError):
    """External service error."""
    
    def __init__(
        self,
        message: str,
        service: Optional[str] = None,
        operation: Optional[str] = None,
        **kwargs: Any
    ):
        """Initialize external service error."""
        details = kwargs.pop("details", {})
        if service:
            details["service"] = service
        if operation:
            details["operation"] = operation
            
        super().__init__(
            message=message,
            code="external_service_error",
            details=details,
            http_status=502,
            **kwargs
        )


class RateLimitError(ServiceError):
    """Rate limit error."""
    
    def __init__(
        self,
        message: str,
        limit: Optional[int] = None,
        reset_time: Optional[datetime] = None,
        **kwargs: Any
    ):
        """Initialize rate limit error."""
        details = kwargs.pop("details", {})
        if limit:
            details["limit"] = limit
        if reset_time:
            details["reset_time"] = reset_time.isoformat()
            
        super().__init__(
            message=message,
            code="rate_limit_error",
            details=details,
            http_status=429,
            **kwargs
        )


class ConfigurationError(ServiceError):
    """Configuration error."""
    
    def __init__(
        self,
        message: str,
        component: Optional[str] = None,
        parameter: Optional[str] = None,
        **kwargs: Any
    ):
        """Initialize configuration error."""
        details = kwargs.pop("details", {})
        if component:
            details["component"] = component
        if parameter:
            details["parameter"] = parameter
            
        super().__init__(
            message=message,
            code="configuration_error",
            details=details,
            http_status=500,
            **kwargs
        )


class RepositoryError(BackendError):
    """Error raised for repository operations."""
    pass


class ConnectionError(BackendError):
    """Error raised for connection issues."""
    pass


class ResourceNotFoundError(BackendError):
    """Error raised when a resource is not found."""
    pass


class ResourceExistsError(BackendError):
    """Error raised when a resource already exists."""
    pass


class DependencyError(BackendError):
    """Error raised for dependency issues."""
    pass


class TimeoutError(BackendError):
    """Error raised for operation timeouts."""
    pass


class StorageError(BackendError):
    """Error raised for storage operations."""
    
    def __init__(
        self,
        message: str,
        storage_type: Optional[str] = None,
        operation: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialize storage error.
        
        Args:
            message: Error message
            storage_type: Type of storage (e.g. s3, gdrive)
            operation: Storage operation that failed
            details: Additional error details
        """
        details = details or {}
        if storage_type:
            details["storage_type"] = storage_type
        if operation:
            details["operation"] = operation
        super().__init__(message, details, http_status=500)


class AnalysisError(BackendError):
    """Error raised for analysis operations."""
    
    def __init__(
        self,
        message: str,
        analysis_type: Optional[str] = None,
        operation: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialize analysis error.
        
        Args:
            message: Error message
            analysis_type: Type of analysis (e.g. sentiment, topic)
            operation: Analysis operation that failed
            details: Additional error details
        """
        details = details or {}
        if analysis_type:
            details["analysis_type"] = analysis_type
        if operation:
            details["operation"] = operation
        super().__init__(message, details, http_status=500)


class TransactionError(BackendError):
    """Error raised for transaction operations."""
    
    def __init__(
        self,
        message: str,
        transaction_id: Optional[str] = None,
        operation: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialize transaction error.
        
        Args:
            message: Error message
            transaction_id: Transaction identifier
            operation: Transaction operation that failed
            details: Additional error details
        """
        details = details or {}
        if transaction_id:
            details["transaction_id"] = transaction_id
        if operation:
            details["operation"] = operation
        super().__init__(message, details, http_status=500)


class WebRTCError(BackendError):
    """Error raised for WebRTC operations."""
    
    def __init__(
        self,
        message: str,
        peer_id: Optional[str] = None,
        operation: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialize WebRTC error.
        
        Args:
            message: Error message
            peer_id: WebRTC peer identifier
            operation: WebRTC operation that failed
            details: Additional error details
        """
        details = details or {}
        if peer_id:
            details["peer_id"] = peer_id
        if operation:
            details["operation"] = operation
        super().__init__(message, details, http_status=500)


class CacheError(BackendError):
    """Error raised for cache operations."""
    
    def __init__(
        self,
        message: str,
        operation: Optional[str] = None,
        key: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialize cache error.
        
        Args:
            message: Error message
            operation: Cache operation that failed
            key: Cache key if applicable
            details: Additional error details
        """
        details = details or {}
        if operation:
            details["operation"] = operation
        if key:
            details["key"] = key
        super().__init__(message, details, http_status=500)


class SerializationError(BackendError):
    """Error raised for data serialization failures."""
    
    def __init__(
        self,
        message: str,
        data_type: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialize serialization error.
        
        Args:
            message: Error message
            data_type: Type of data being serialized
            details: Additional error details
        """
        details = details or {}
        if data_type:
            details["data_type"] = data_type
        super().__init__(message, details, http_status=500)


class DeserializationError(BackendError):
    """Error raised for data deserialization failures."""
    
    def __init__(
        self,
        message: str,
        data_type: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialize deserialization error.
        
        Args:
            message: Error message
            data_type: Type of data being deserialized
            details: Additional error details
        """
        details = details or {}
        if data_type:
            details["data_type"] = data_type
        super().__init__(message, details, http_status=500)


class NetworkError(BackendError):
    """Error raised for network operations."""
    
    def __init__(
        self,
        message: str,
        operation: Optional[str] = None,
        endpoint: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialize network error.
        
        Args:
            message: Error message
            operation: Network operation that failed
            endpoint: Network endpoint if applicable
            details: Additional error details
        """
        details = details or {}
        if operation:
            details["operation"] = operation
        if endpoint:
            details["endpoint"] = endpoint
        super().__init__(message, details, http_status=500)


class InfrastructureError(BackendError):
    """Base class for infrastructure-related errors."""
    
    def __init__(
        self,
        message: str,
        service: Optional[str] = None,
        operation: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialize infrastructure error.
        
        Args:
            message: Error message
            service: Infrastructure service name
            operation: Operation that failed
            details: Additional error details
        """
        details = details or {}
        if service:
            details["service"] = service
        if operation:
            details["operation"] = operation
        super().__init__(message, details, http_status=500)


class ServiceUnavailableError(ServiceError):
    """Service unavailable error."""
    
    def __init__(
        self,
        message: str,
        service: str,
        retry_after: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialize service unavailable error.
        
        Args:
            message: Error message
            service: Service name
            retry_after: Seconds to wait before retry
            details: Additional error details
        """
        super().__init__(
            message=message,
            code="SERVICE_UNAVAILABLE",
            http_status=503,
            details=details if details else {
                "service": service,
                "retry_after": retry_after
            }
        )



