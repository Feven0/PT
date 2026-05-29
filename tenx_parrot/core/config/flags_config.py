from typing import Dict, Optional
from pydantic import Field

from core.types.model import CoreBaseModel

class FeatureFlags(CoreBaseModel):
    """Feature flags configuration."""
    enabled_features: Dict[str, bool] = Field(
        default_factory=dict,
        description="Enabled features"
    )