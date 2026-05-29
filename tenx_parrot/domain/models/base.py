"""Base domain models and utilities."""
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID
from pydantic import Field

from core.types.model import CoreBaseModel

class BaseDomainModel(CoreBaseModel):
    """Base model for all domain models."""
    
    id: Optional[UUID] = Field(None, description="Unique identifier")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Update timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata") 