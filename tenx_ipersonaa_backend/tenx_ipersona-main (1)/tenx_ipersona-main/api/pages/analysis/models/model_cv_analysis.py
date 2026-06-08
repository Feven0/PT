from pydantic import BaseModel
from typing import List, Dict, Optional, Tuple, Union, Any

class FileReceivedPayload(BaseModel): 
    filename: str
    content_type: str
    userId: str
    email: str
    
class FileSchemaModel(BaseModel):
    files: str
    content_type: str
    userId: str
    
class AnalysisResponse(BaseModel):
    userId: str
    email: Optional[str] = ""
    data: Optional[Dict] = {}
    status: Optional[int] = 200
    message: Optional[str] = ""
    time_to_wait: Optional[int] = -1
