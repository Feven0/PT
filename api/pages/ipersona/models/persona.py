from pydantic import BaseModel
from typing import Dict, Any, Optional
class UserRequestRecieved(BaseModel):
    userId: str
    
class UserSessionRequestRecieved(BaseModel):
    userId: str
    sessionId: str
    jbId: str
    
class SessionRequestRecieved(BaseModel):
    userId: str
    
class SessionJobRequestRecieved(BaseModel):
    sessionId: str
    jbId: str
    
class userSessionRequestRecieved(BaseModel):
    jobId: int
    userId: int
    name: str
    cvJson: Optional[Dict[str, Any]]
    jbJson: Optional[Dict[str, Any]]
    
class ChatHistoryRequestRecieved(BaseModel):
    sessionId: int
          
class MetricsRequestRecieved(BaseModel):
    userId: str
    sessionId: str
    jbId: str    
    
class SaveMetricsRequestRecieved(BaseModel):
    response: Optional[Dict[str, Any]]
    data: Optional[Dict[str, Any]]    
    
class ClarificationRequestRecieved(BaseModel):
    question: str


