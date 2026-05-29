"""Prompt configuration management."""
from typing import Dict, List, Optional
from pydantic import Field

from core.types.model import CoreBaseModel

class PromptConfig(CoreBaseModel):
    """Configuration for prompt management."""
    enabled: bool = Field(default=True, description="Enable prompt management")
    template_paths: List[str] = Field(default_factory=list, description="Paths to template files")
    cache_templates: bool = Field(default=True, description="Enable template caching")
    cache_ttl: int = Field(default=3600, description="Cache TTL in seconds")
    max_retries: int = Field(default=3, description="Max retries for template loading")
    timeout: int = Field(default=30, description="Timeout for template loading")
    default_variables: Dict[str, str] = Field(
        default_factory=dict,
        description="Default variables available to all templates"
    ) 