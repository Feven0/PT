"""Middleware configuration."""
from typing import Optional, List, Dict, Any
from pydantic import Field

from core.types.model import CoreBaseModel

class ErrorHandlerConfig(CoreBaseModel):
    """Error handler middleware configuration."""
    enabled: bool = Field(default=True, description="Enable error handler")
    log_errors: bool = Field(default=True, description="Log errors")
    include_traceback: bool = Field(default=False, description="Include traceback in error response")
    error_handlers: Dict[str, str] = Field(default_factory=dict, description="Custom error handlers")
    sanitize_errors: bool = Field(default=True, description="Sanitize error messages")
    default_error_message: str = Field(default="An error occurred", description="Default error message")

class RequestProcessorConfig(CoreBaseModel):
    """Request processor middleware configuration."""
    enabled: bool = Field(default=True, description="Enable request processor")
    log_requests: bool = Field(default=True, description="Log requests")
    log_responses: bool = Field(default=True, description="Log responses")
    compress_response: bool = Field(default=True, description="Compress response")
    max_content_length: int = Field(default=10485760, description="Maximum content length")
    allowed_content_types: List[str] = Field(
        default=["application/json", "multipart/form-data"],
        description="Allowed content types"
    )
    request_timeout: float = Field(default=30.0, description="Request timeout in seconds")

class HealthCheckConfig(CoreBaseModel):
    """Health check middleware configuration."""
    enabled: bool = Field(default=True, description="Enable health check")
    endpoint: str = Field(default="/health", description="Health check endpoint")
    include_details: bool = Field(default=False, description="Include health check details")
    timeout: float = Field(default=5.0, description="Health check timeout in seconds")
    required_services: List[str] = Field(default_factory=list, description="Required services")
    check_interval: int = Field(default=60, description="Check interval in seconds") 