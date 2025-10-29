from pydantic import BaseModel
from typing import Dict, Any, Optional, Union
from api.pages.ipersona.models.model_parrot_basic import MyBaseModel

default_days_since = 7
default_limit = 10
default_status = "all"

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


class ChallengeRequestFiltering(MyBaseModel):
    challenge_id: int

class SessionRequestFiltering(MyBaseModel):
    sessionId: str
    
class OverallRequestRecieved(MyBaseModel):
    all_user_id: int
    job_profile_id: int
    challenge_id: int
    template_id: Optional[int] = None

class UpdateSessionModeRequestReceieved(MyBaseModel):
    sessionId: int
    mode: str
    
class UserSessionRequestRecieved(MyBaseModel):
    mode: str 
    job_profile_id: int
    all_user_id: int
    template: bool = False
    generate: bool 
    external: bool = False
    challenge: bool = False
    template_id: int
    challenge_id: int

# class UserSessionRequestRecieved(MyBaseModel):
#     job_profile_id: int
#     all_user_id: int
#     template: bool = False
#     generate: bool 
#     external: bool = False
#     challenge: bool = False
#     template_id: int
#     challenge_id: int

class AlUserSessionRequestRecieved(MyBaseModel):
    all_user_id: int
    job_profile_id: int
    template_id: int
    challenge_id: int
    # limit: Optional[int] = default_days_since
    since: Optional[int] = default_days_since

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
   
class AdminJobDataTempFiltering(MyBaseModel):
    cursor: Optional[Dict] = {}
    filter: Optional[Dict] = {}
    limit: Optional[int] = default_limit
    since: Optional[int] = default_days_since
    information_level: Optional[str] = "minimal"
    return_skip: Optional[bool] = False
    job_profile_id: int

class AdminChallengeDataTempFiltering(MyBaseModel):
    cursor: Optional[Dict] = {}
    filter: Optional[Dict] = {}
    limit: Optional[int] = default_limit
    since: Optional[int] = default_days_since
    information_level: Optional[str] = "minimal"
    return_skip: Optional[bool] = False
    challenge_id: int

class AdminDataFiltering(MyBaseModel):
    cursor: Optional[Dict] = {}
    filter: Optional[Dict] = {}
    limit: Optional[int] = default_limit
    since: Optional[int] = default_days_since
    information_level: Optional[str] = "minimal"
    return_skip: Optional[bool] = False
    
class AdminDataTempFiltering(MyBaseModel):
    cursor: Optional[Dict] = {}
    filter: Optional[Dict] = {}
    limit: Optional[int] = default_limit
    since: Optional[int] = default_days_since
    job_profile_id: int
    # information_level: Optional[str] = "minimal"
    # return_skip: Optional[bool] = False
class AdminInterviewByTemplateIdFiltering(MyBaseModel):
    cursor: Optional[Dict] = {}
    filter: Optional[Dict] = {}
    limit: Optional[int] = default_limit
    since: Optional[int] = default_days_since
    information_level: Optional[str] = "minimal"
    return_skip: Optional[bool] = False
    template_id: int
    status: str = default_status

class AdminJobByTemplateIdFiltering(MyBaseModel):
    cursor: Optional[Dict] = {}
    filter: Optional[Dict] = {}
    limit: Optional[int] = default_limit
    since: Optional[int] = default_days_since
    information_level: Optional[str] = "minimal"
    return_skip: Optional[bool] = False
    template_id: int

class AdminDataEachJobFiltering(MyBaseModel):
    limit: Optional[int] = default_limit
    since: Optional[int] = default_days_since
    filter: Optional[Dict] = {}
    job_profile_id: int
      
class TinderTemplateRequestRecieved(MyBaseModel):
    name: str
    type: str
    tag: str
    description: str
    template_questions: Optional[list] = []
    job_profile_ids: Optional[list] = []
    prompt_ids: Optional[list] = []
    challenge_ids: Optional[list] = []

class UpdateTinderTemplateRequestRecieved(MyBaseModel):
    template_id: int
    name: str
    type: str
    tag: str
    description: str
    template_questions: Optional[Union[list, str]] = {}
    job_profile_ids: Optional[Union[list, str]] = []
    prompt_ids: Optional[Union[list, str]] = []
    challenge_ids: Optional[Union[list, str]] = []

class GetFilteredTinderTemplateRequestRecieved(MyBaseModel):
    job_profile_id: Optional[int] = None  
    challenge_id: Optional[int] = None
    prompt_id: Optional[int] = None
    type: Optional[str] = None  # Optional type field
    cursor: Optional[Dict] = {}
    filter: Optional[Dict] = {}
    limit: Optional[int] = default_limit
    since: Optional[int] = default_days_since
    information_level: Optional[str] = "minimal"    
    return_skip: Optional[bool] = False

class GetTemplateRequestRecieved(MyBaseModel):
    template_id: int

class TinderTemplateJobIdRequestRecieved(MyBaseModel):
    job_profile_id: int
    
class TemplateLLMContextRequestRecieved(MyBaseModel):
    context: str
    all_user_id: int
    job_profile_ids: Optional[list] = []
    challenge_ids: Optional[list] = []

class TinderTemplateAttachJobIdRequestRecieved(MyBaseModel):
    template_id: int
    job_profile_ids: Optional[list] = []
    prompt_ids: Optional[list] = []
    challenge_ids: Optional[list] = []

class RunStageSetupRequestRecieved(MyBaseModel):
    pass
    
class ExternalRequestRecieved(MyBaseModel):
    transcribe_chat: Optional[list] = []
    job_profile_id: int
    all_user_id: int
    template: bool = False
    generate: bool = False
    external: bool 
    challenge: bool = False

class UpdateSessionModeRequestReceieved(MyBaseModel):
    sessionId: int
    mode: str

class GetAllTinderTemplateRequestRecieved(MyBaseModel):
    cursor: Optional[Dict] = {}
    since: Optional[int] = default_days_since
    limit: Optional[int] = default_limit
    run_stage: Optional[str] = "dev"
    filter: Optional[Dict] = {}
