from pydantic import BaseModel
from typing import Dict, Any, Optional
default_days_since = 1

class UserRequestRecieved(BaseModel):
    userId: str
   
class ClosedDataRequestRecieved(BaseModel):
    data: Optional[Dict[str, Any]]
        
class SessionRequestRecieved(BaseModel):
    alluser: int
    job_profile_id: int
    
class SessionJobRequestRecieved(BaseModel):
    sessionId: str
    jbId: str
    
class UserSessionRequestRecieved(BaseModel):
    job_profile_id: int
    all_user_id: int

class AllUserIdRecieved(BaseModel):
    all_user_id: int

class AllUserSessionRequestRecieved(BaseModel):
    all_user_id: int
    cursor: Optional[Dict] = {}
    filter: Optional[Dict] = {}
    limit: Optional[int] = default_days_since
    since: Optional[int] = default_days_since
    information_level: Optional[str] = "minimal"
    return_skip: Optional[bool] = False

class SessionIdRequestRecieved(BaseModel):
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
   
class AdminDataFiltering(BaseModel):
    # cursor: Optional[Dict] = {}
    # filter: Optional[Dict] = {}
    limit: Optional[int] = default_days_since
    since: Optional[int] = default_days_since
    # information_level: Optional[str] = "minimal"
    # return_skip: Optional[bool] = False

    


