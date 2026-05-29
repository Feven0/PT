"""Request context type definitions."""
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class RequestContext(BaseModel):
    """Request context information."""
    
    request_id: str
    start_time: datetime
    path: str
    method: str
    client: Optional[Tuple[str, int]] = None  # (host, port)
    headers: Dict[str, Any] = {}
    
    model_config = ConfigDict(
        arbitrary_types_allowed=True
    )
    
    @property
    def duration(self) -> float:
        """Get request duration in seconds."""
        if not self.start_time:
            return 0.0
        return (datetime.now() - self.start_time).total_seconds()
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary.
        
        Returns:
            Dictionary representation of context
        """
        return {
            "request_id": self.request_id,
            "start_time": self.start_time.isoformat(),
            "path": self.path,
            "method": self.method,
            "client": self.client,
            "headers": self.headers,
            "duration": self.duration
        }
        
    def get_header(self, name: str, default: Any = None) -> Any:
        """Get header value.
        
        Args:
            name: Header name
            default: Default value if header not found
            
        Returns:
            Header value
        """
        return self.headers.get(name, default)
        
    def get_client_ip(self) -> Optional[str]:
        """Get client IP address.
        
        Returns:
            Client IP address or None
        """
        if not self.client:
            return None
        return self.client[0]
        
    def get_client_port(self) -> Optional[int]:
        """Get client port.
        
        Returns:
            Client port or None
        """
        if not self.client:
            return None
        return self.client[1] 