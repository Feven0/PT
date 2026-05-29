"""TenX domain models."""
from typing import Dict, Any, Optional, List
from datetime import datetime,timezone
from pydantic import Field

from core.types.model import CoreBaseModel


class Theme(CoreBaseModel):
    """Theme model."""
    
    id: str
    name: str
    description: Optional[str] = None
    variables: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime


class Component(CoreBaseModel):
    """Component model."""
    
    id: str
    name: str
    description: Optional[str] = None
    type: str
    theme_id: Optional[str] = None
    template: str
    props: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime


class Layout(CoreBaseModel):
    """Layout model."""
    
    id: str
    name: str
    description: Optional[str] = None
    type: str
    theme_id: Optional[str] = None
    template: str
    sections: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime


class RenderRequest(CoreBaseModel):
    """Render request model."""
    
    data: Dict[str, Any] = Field(default_factory=dict)
    variables: Optional[Dict[str, Any]] = None


class RenderResponse(CoreBaseModel):
    """Render response model."""
    
    html: str
    css: Optional[str] = None
    js: Optional[str] = None 