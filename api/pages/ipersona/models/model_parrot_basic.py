import os
from api import config
from pydantic import BaseModel, Json, field_validator
#from pydantic import BaseSettings
from typing import List, Dict, Optional, Tuple, Union, Any
from enum import Enum, IntEnum

__all__ = [
    'BaseModel',
    'Json',
    'Union',
    'List',
    'Dict',
    'Optional',
    'Tuple',
    'Any',
    'Enum',
    'IntEnum',
    'MyBaseModel',
    'RunStageEnum',
    'ObjectKindEnum',
    'ToolEnum',
    'STAFF_ROLE',
    'TRAINEE_ROLE',
    'default_run_stage',
    'default_days_since',
    'default_http_response',
]


STAFF_ROLE = 'Staff'
TRAINEE_ROLE = 'Trainee'
default_run_stage = config.strapi_stage
default_days_since = 0
default_http_response = 200

class MyBaseModel(BaseModel):
    run_stage: Optional[str] = default_run_stage
    
    class ConfigDict:
        from_attributes = True  
        
    @field_validator("run_stage", mode="before")
    @classmethod
    def transform(cls, run_stage: Optional[str]) -> str:
        # If run_stage is provided, return it. Otherwise, use default_run_stage.
        return run_stage or default_run_stage
         
          
class RunStageEnum(str, Enum):
    dev = 'dev'
    prod = 'prod'
    stage = 'stage'

class ObjectKindEnum(str, Enum):
    job_profile = 'job_profile'
    user_profile = 'user_profile'
    user_reaction = 'user_reaction'
    user_job_match = 'user_job_match'
    asset_generation = 'asset_generation'
    user_leap = 'user_leap'
    

class ToolEnum(IntEnum):
    spanner = 1
    wrench = 2