from pydantic import BaseModel
class UserRequestRecieved(BaseModel):
    userId: str
    
class UserSessionRequestRecieved(BaseModel):
    userId: str
    sessionId: str
    jbId: str
    
class AnalyseRequestRecieved(BaseModel):
    id: str
    jbId: str
    cvPath: str
    jbPath: str
    persona: str
    
    

class SessionRequestRecieved(BaseModel):
    userId: str
    
class SessionJobRequestRecieved(BaseModel):
    sessionId: str
    jbId: str
    
class AnalyseJobRequestRecieved(BaseModel):
    sessionId: str
    jbId: str
    cvPath: str
    jbPath: str
    
class MetricsRequestRecieved(BaseModel):
    userId: str
    sessionId: str
    jbId: str
