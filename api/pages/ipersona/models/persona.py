from pydantic import BaseModel
from typing import Dict, Any, Optional
from api.pages.ipersona.models.model_parrot_basic import MyBaseModel

default_days_since = 1

class UserRequestRecieved(MyBaseModel):
    userId: str
   
class ClosedDataRequestRecieved(MyBaseModel):
    data: Optional[Dict[str, Any]]
        
class SessionRequestRecieved(MyBaseModel):
    alluser: int
    job_profile_id: int
    
class SessionJobRequestRecieved(MyBaseModel):
    sessionId: str
    jbId: str
    
class UserSessionRequestRecieved(MyBaseModel):
    job_profile_id: int
    all_user_id: int

class AllUserIdRecieved(MyBaseModel):
    all_user_id: int

class AllUserSessionRequestRecieved(MyBaseModel):
    all_user_id: int
    cursor: Optional[Dict] = {}
    filter: Optional[Dict] = {}
    limit: Optional[int] = default_days_since
    since: Optional[int] = default_days_since
    information_level: Optional[str] = "minimal"
    return_skip: Optional[bool] = False

class SessionIdRequestRecieved(MyBaseModel):
    sessionId: int
               
class MetricsRequestRecieved(MyBaseModel):
    userId: str
    sessionId: str
    jbId: str    
    
class SaveMetricsRequestRecieved(MyBaseModel):
    response: Optional[Dict[str, Any]]
    data: Optional[Dict[str, Any]]    
    
class ClarificationRequestRecieved(MyBaseModel):
    question: str
    
class audioRequestRecieved(MyBaseModel):
    text: str
   
class AdminDataFiltering(MyBaseModel):
    # cursor: Optional[Dict] = {}
    # filter: Optional[Dict] = {}
    limit: Optional[int] = default_days_since
    since: Optional[int] = default_days_since
    # information_level: Optional[str] = "minimal"
    # return_skip: Optional[bool] = False

    


