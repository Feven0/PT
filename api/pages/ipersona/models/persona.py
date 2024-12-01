from pydantic import BaseModel
from typing import Dict, Any, Optional
class UserRequestRecieved(BaseModel):
    userId: str
    
class SessionRequestRecieved(BaseModel):
    alluser: int
    jobId: int
    
class SessionJobRequestRecieved(BaseModel):
    sessionId: str
    jbId: str
    
class UserSessionRequestRecieved(BaseModel):
    jobId: int
    alluserId: int
       
class AllUserSessionRequestRecieved(BaseModel):
    alluserId: int

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
    
class audioRequestRecieved(BaseModel):
    text: str
   
    


