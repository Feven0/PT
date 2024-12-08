import os, sys
import re
import copy
import json
from datetime import datetime, timedelta


#from .pathfig import *


from api import config
from api.modules.leap_base import LeapBaseClass
#from api.modules.leap_trainee import TraineeSchema
#
from api.utils.logger import LLPackerLogger
logger = LLPackerLogger(__file__)
from collections import defaultdict

capitalize = lambda x: x[0].upper() + x[1:]


class IpersonaSessionSchema(LeapBaseClass):
    '''
    Schema Name:
        IPersonaSession
    Attributes:
        i_persona_observer: Relation with IPersonaObserver
        tinder_user_profile: Relation with TinderUserProfile
        tinder_job_profile: Relation with TInderJobProfile
        slug: Text	
        attributes: Json	
        status: Text
    '''
    def __init__(self, **kwargs) -> None:
        self.kwargs = copy.deepcopy(kwargs)
        super().__init__(**kwargs)
        
        self.table_single = kwargs.get('table_single', "")
        self.table = kwargs.get('table', "")
        self.data = kwargs.get('data', "")
        
        if not self.table_single:
            self.table_single = "iPersonaSession"
            
        if not self.table:
            self.table = "iPersonaSessions"
            
        if not self.data:
            logger.info(f"Using default data schema for {self.table_single} ...")
            self.data = '''
                data {
                    id
                    attributes {
                        slug
                        status
                        attributes
                        createdAt  
                        i_persona_observer {
                            data {
                                id
                                attributes {
                                    attributes
                                    metadata
                                }
                            }        	
                        }
                        tinder_job_profile {
                            data {
                                id
                            }
                        } 
                        tinder_user_profile {
                            data {
                                id
                            }
                        } 
                        %s
                    }
                }
            '''
        else:
            logger.info(f"Using passed data schema for {self.table_single} ...")
     
            
        self.type_map = {   
            "slug": "String",
            "status": "String",
            "attributes": "JSON",
            "i_persona_observer": "ID",
            "tinder_job_profile": "ID",
            "tinder_user_profile": "ID"

        }

        self.id_names_map = {  }
         
        self.data_template = copy.deepcopy(self.data)
        self.data = self.data%""
        _ = self.process_extra_data(kwargs.get('extra_data', []), inplace=True)
    
    def get_session_by_id(self, sessionId, **kwargs):
        data_json = self.exists(scol='id', sval=sessionId, op='eq', stype="ID", **kwargs)  
        data = self.get_session_data(data_json)   
        return data
    
    def filter_by_observer_id(self, vid, **kwargs):
        session_filter = f"""
            filters: {{
                i_persona_observer : {{ id: {{ eq: {vid} }} }}
            }}
        """
        return self.get_all_objects(filter=session_filter , **kwargs)
    
    def filter_by_tinder_user_profile_id(self, user_profile_id, **kwargs):
        session_filter = f"""
            filters: {{
                tinder_user_profile : {{ id: {{ eq: {user_profile_id} }} }}
            }}
        """
        data_json = self.get_all_objects(filter=session_filter , **kwargs)
        data = self.get_session_data(data_json)
        return data
    
    def filter_by_with_user_job_id(self, user_profile_id, job_profile_id, **kwargs):
        session_filter = f"""
            filters: {{
                tinder_user_profile : {{ id: {{ eq: {user_profile_id} }} }}
                tinder_job_profile : {{ id: {{ eq: {job_profile_id} }} }}

            }}
        """
        data_json = self.get_all_objects(filter=session_filter , **kwargs)
        data = self.get_sessions_data(data_json)
        return data

    def get_all_sessions(self, **kwargs):
        session_json = self.get_all_objects(**kwargs)  
        session = self.get_sessions_data(session_json)
        return session       
        
    def save_session(self, params, **kwargs):
        session_json = self.save_or_update_object(params, **kwargs)
        session = self.get_extracted_data(session_json)
        return session
    
    def save_if_new_user(self, scol, params, **kwargs):
        return self.save_if_new(scol, params, **kwargs)
    
    def update_session(self, params, **kwargs):
        if self.id_name() not in params:
            logger.error("Id is missing for update!")
            return []
        return self.save_or_update_object(params, **kwargs)

    def delete_session(self, ids, **kwargs):
        return self.delete_objects_by_id(ids, **kwargs)
    
    def get_extracted_data(self, session_json):
        if isinstance(session_json, list) and len(session_json) > 0:  
            first_item = session_json[0]  
            if 'data' in first_item and 'createIPersonaSession' in first_item['data']:
                session = first_item['data']['createIPersonaSession']['data']
                return session
        return None    
    
    def get_sessions_data(self, session_json):
        all_sessions = []
        if isinstance(session_json, list) and len(session_json) > 0:  
            first_item = session_json[0]  
            if 'data' in first_item and 'iPersonaSessions' in first_item['data']:
                session = first_item['data']['iPersonaSessions']['data']
                all_sessions=session
                return all_sessions
        return None 
    
    def get_session_data(self, session_json):
        all_sessions = []
        if isinstance(session_json, dict) and len(session_json) > 0:  
            first_item = session_json  
            if 'data' in first_item and 'iPersonaSession' in first_item['data']:
                session = first_item['data']['iPersonaSession']['data']
                all_sessions=session
                return all_sessions
        return None 
    
class IpersonaTraineeSchema(LeapBaseClass):
    '''
    Schema Name:
        TinderUserProfiles
    Attributes:
        all_users: Relation with AllUsers
        attributes: Json	
    '''
    def __init__(self, **kwargs) -> None:
        self.kwargs = copy.deepcopy(kwargs)
        super().__init__(**kwargs)
        
        self.table_single = kwargs.get('table_single', "")
        self.table = kwargs.get('table', "")
        self.data = kwargs.get('data', "")
        
        if not self.table_single:
            self.table_single = "tinderUserProfile"
            
        if not self.table:
            self.table = "tinderUserProfiles"
            
        if not self.data:
            logger.info(f"Using default data schema for {self.table_single} ...")
            self.data = '''
                data {
                    id
                    attributes {
                        attributes
                        all_users {
                            data {
                                id
                            }        	
                        }    
                      %s                                                   
                    }
                }
            '''
        else:
            logger.info(f"Using passed data schema for {self.table_single} ...")
     
            
        self.type_map = {    
            "attributes": "JSON",
            "all_users": "ID"
        }

        self.id_names_map = {  }
         
        self.data_template = copy.deepcopy(self.data)
        self.data = self.data%""
        _ = self.process_extra_data(kwargs.get('extra_data', []), inplace=True)
    
    def get_trainee_by_id(self, user_profile_id, **kwargs):
        data_json = self.exists(scol='id', sval= user_profile_id, op='eq', stype="ID", **kwargs)       
        data = self.get_extracted_trainee_data(data_json)   
        return data     
    
    def filter_by_alluser_id(self, all_user_id, **kwargs):
        session_filter = f"""
            filters: {{
                all_users : {{ id: {{ eq: {all_user_id} }} }}
            }}
        """
        data_json = self.get_all_objects(filter=session_filter , **kwargs)
        data = self.get_extracted_data(data_json)
        return data

    def get_all_trainees_info(self, **kwargs):
        session_json = self.get_all_objects(**kwargs)  
        session = self.get_extracted_data(session_json)
        return session
    
    def get_extracted_data(self, session_json):
        if isinstance(session_json, list) and len(session_json) > 0:  
            first_item = session_json[0]  
            if 'data' in first_item and 'tinderUserProfiles' in first_item['data']:
                session = first_item['data']['tinderUserProfiles']['data']
                return session
        return None   
    
    def get_extracted_trainee_data(self, data_json):
        data = []
        if isinstance(data_json, dict) and len(data_json) > 0:  
            first_item = data_json  
            if 'data' in first_item and 'tinderUserProfile' in first_item['data']:
                data_json = first_item['data']['tinderUserProfile']['data']
                data = data_json
                return data
        return None     

class IpersonaJobSchema(LeapBaseClass):
    '''
    Schema Name:
        TinderJobProfiles
    Attributes:
        id: ID,
        attributes: Json	
    '''
    def __init__(self, **kwargs) -> None:
        self.kwargs = copy.deepcopy(kwargs)
        super().__init__(**kwargs)
        
        self.table_single = kwargs.get('table_single', "")
        self.table = kwargs.get('table', "")
        self.data = kwargs.get('data', "")
        
        if not self.table_single:
            self.table_single = "tinderJobProfile"
            
        if not self.table:
            self.table = "tinderJobProfiles"
            
        if not self.data:
            logger.info(f"Using default data schema for {self.table_single} ...")
            self.data = '''
                data {
                    id
                    attributes {
                        attributes  
                      %s                                                   
                    }
                }
            '''
        else:
            logger.info(f"Using passed data schema for {self.table_single} ...")
     
            
        self.type_map = {    
            "id": "ID",
            "attributes": "JSON"
        }

        self.id_names_map = {  }
         
        self.data_template = copy.deepcopy(self.data)
        self.data = self.data%""
        _ = self.process_extra_data(kwargs.get('extra_data', []), inplace=True)
    
    def get_job_by_id(self, idval, **kwargs):
        return self.exists(scol='id', sval=idval, op='eq', stype="ID", **kwargs)        
    
    def filter_by_job_id(self, job_profile_id, **kwargs):
        session_filter = f"""
            filters: {{
                id : {{ eq: {job_profile_id} }} 
            }}
        """
        data_json = self.get_all_objects(filter=session_filter , **kwargs)
        data = self.get_extracted_data(data_json)
        return data

    def get_all_jobs_info(self, **kwargs):
        session_json = self.get_all_objects(**kwargs)  
        session = self.get_extracted_data(session_json)
        return session
    
    def get_extracted_data(self, session_json):
        if isinstance(session_json, list) and len(session_json) > 0:  
            first_item = session_json[0]  
            if 'data' in first_item and 'tinderJobProfiles' in first_item['data']:
                session = first_item['data']['tinderJobProfiles']['data']
                return session
        return None        

class IpersonaSessionOverallObserverSchema(LeapBaseClass):
    '''
    Schema Name:
        IPersonaSessionOverallObservers
    Attributes:
        tinder_user_profile: Relation with TinderUserProfile
        tinder_job_profile: Relation with TInderJobProfile
        attributes: Json	
    '''
    def __init__(self, **kwargs) -> None:
        self.kwargs = copy.deepcopy(kwargs)
        super().__init__(**kwargs)
        
        self.table_single = kwargs.get('table_single', "")
        self.table = kwargs.get('table', "")
        self.data = kwargs.get('data', "")
        
        if not self.table_single:
            self.table_single = "iPersonaSessionOverallObserver"
            
        if not self.table:
            self.table = "iPersonaSessionOverallObservers"
            
        if not self.data:
            logger.info(f"Using default data schema for {self.table_single} ...")
            self.data = '''
                data {
                    id
                    attributes {
                        attributes
                        tinder_user_profile {
                            data {
                                id
                            }
                        } 
                        tinder_job_profile {
                            data {
                                id
                            }
                        } 
                        %s
                    }
                }
            '''
        else:
            logger.info(f"Using passed data schema for {self.table_single} ...")
     
            
        self.type_map = { 
            "id": "ID",
            "attributes": "JSON",            
            "tinder_user_profile": "ID",
            "tinder_job_profile": "ID"        }

        self.id_names_map = {  }
         
        self.data_template = copy.deepcopy(self.data)
        self.data = self.data%""
        _ = self.process_extra_data(kwargs.get('extra_data', []), inplace=True)
    
    def filter_by_tinder_user_profile_id(self, user_profile_id, **kwargs):
        session_filter = f"""
            filters: {{
                tinder_user_profile : {{ id: {{ eq: {user_profile_id} }} }}
            }}
        """
        data_json = self.get_all_objects(filter=session_filter , **kwargs)
        data = self.get_extracted_from_user_data(data_json)
        return data
    
    def filter_by_with_user_and_job_id(self, user_profile_id, job_profile_id, **kwargs):
        session_filter = f"""
            filters: {{
                tinder_user_profile : {{ id: {{ eq: {user_profile_id} }} }},
                tinder_job_profile : {{ id: {{ eq: {job_profile_id} }} }}
            }}
        """
        data_json = self.get_all_objects(filter=session_filter , **kwargs)
        data = self.get_extracted_from_user_job_data(data_json)
        return data
    
    def save_Session_Overall_Observer(self, params, **kwargs):
        session_json = self.save_or_update_object(params, **kwargs)
        session = self.get_extracted_data(session_json)
        return session
    
    def update_session(self, params, **kwargs):
        if self.id_name() not in params:
            logger.error("Id is missing for update!")
            return []
        return self.save_or_update_object(params, **kwargs)
   
    def get_extracted_data(self, session_json):
        if isinstance(session_json, list) and len(session_json) > 0:  
            first_item = session_json[0]  
            if 'data' in first_item and 'createIPersonaSessionOverallObserver' in first_item['data']:
                session = first_item['data']['createIPersonaSessionOverallObserver']['data']
                return session
        return None  
    
    def get_extracted_from_user_job_data(self, session_json):
        all_sessions = []
        if isinstance(session_json, list) and len(session_json) > 0:  
            first_item = session_json[0]  
            if 'data' in first_item and 'iPersonaSessionOverallObservers' in first_item['data']:
                session = first_item['data']['iPersonaSessionOverallObservers']['data']
                for session in session:
                    attributes = session.get('attributes', {}).get('attributes', {})
                    id = session.get('id', '')
                    all_sessions.append(attributes)   
                
                result = {
                    "id": id,
                    "all_sessions": all_sessions
                }
                return result
        return None    
    
    def get_extracted_from_user_data(self, session_json):
        all_sessions = []
        if isinstance(session_json, list) and len(session_json) > 0:  
            first_item = session_json[0]  
            if 'data' in first_item and 'iPersonaSessionOverallObservers' in first_item['data']:
                session = first_item['data']['iPersonaSessionOverallObservers']['data']
                for session in session:
                    session_attributes = session.get('attributes', {}).get('attributes', {})
                    all_sessions = session_attributes 
                
                return all_sessions
        return None    

class IpersonaSessionTinderUserJobMatchSchema(LeapBaseClass):
    '''
    Schema Name:
        TinderUserJobMatches
    Attributes:
        match_score: Int
        match_level: String
    '''
    def __init__(self, **kwargs) -> None:
        self.kwargs = copy.deepcopy(kwargs)
        super().__init__(**kwargs)
        
        self.table_single = kwargs.get('table_single', "")
        self.table = kwargs.get('table', "")
        self.data = kwargs.get('data', "")
        
        if not self.table_single:
            self.table_single = "tinderUserJobMatch"
            
        if not self.table:
            self.table = "tinderUserJobMatches"
            
        if not self.data:
            logger.info(f"Using default data schema for {self.table_single} ...")
            self.data = '''
                data {
                    id
                    attributes {
                        match_score
                        match_level 
                        %s
                    }
                }
            '''
        else:
            logger.info(f"Using passed data schema for {self.table_single} ...")
     
            
        self.type_map = { 
            "match_score": "Int",
            "match_level": "String"        }

        self.id_names_map = {  }
         
        self.data_template = copy.deepcopy(self.data)
        self.data = self.data%""
        _ = self.process_extra_data(kwargs.get('extra_data', []), inplace=True)
        
    def filter_by_with_user_and_job_id(self, user_profile_id, job_profile_id, **kwargs):
        session_filter = f"""
            filters: {{
                tinder_user_profile : {{ id: {{ eq: {user_profile_id} }} }},
                tinder_job_profile : {{ id: {{ eq: {job_profile_id} }} }}
            }}
        """
        data_json = self.get_all_objects(filter=session_filter , **kwargs)
        data = self.get_extracted_from_user_job_data(data_json)
        return data
    
    def get_extracted_from_user_job_data(self, session_json):
        all_sessions = []
        if isinstance(session_json, list) and len(session_json) > 0:  
            first_item = session_json[0]  
            if 'data' in first_item and 'tinderUserJobMatches' in first_item['data']:
                session = first_item['data']['tinderUserJobMatches']['data']
                all_sessions = session
                
                return all_sessions
        return None    

class IpersonaSessionTinderUserReactionSchema(LeapBaseClass):
    '''
    Schema Name:
        TinderUserReactions
    Attributes:
        tinder_job_profile: ID,
        tinder_user_profile: ID
    '''
    def __init__(self, **kwargs) -> None:
        self.kwargs = copy.deepcopy(kwargs)
        super().__init__(**kwargs)
        
        self.table_single = kwargs.get('table_single', "")
        self.table = kwargs.get('table', "")
        self.data = kwargs.get('data', "")
        
        if not self.table_single:
            self.table_single = "tinderUserReaction"
            
        if not self.table:
            self.table = "tinderUserReactions"
            
        if not self.data:
            logger.info(f"Using default data schema for {self.table_single} ...")
            self.data = '''
                data {
                    id
                    attributes {
                        tinder_user_profile {
                            data {
                                id
                            }
                        } 
                        tinder_job_profile {
                            data {
                                id
                            }
                        } 
                        %s
                    }
                }
            '''
        else:
            logger.info(f"Using passed data schema for {self.table_single} ...")
     
            
        self.type_map = { 
            "tinder_job_profile": "ID",
            "tinder_user_profile": "ID"       
        }

        self.id_names_map = {  }
         
        self.data_template = copy.deepcopy(self.data)
        self.data = self.data%""
        _ = self.process_extra_data(kwargs.get('extra_data', []), inplace=True)
        
    def filter_by_with_user_and_job_id(self, user_profile_id, job_profile_id, **kwargs):
        session_filter = f"""
            filters: {{
                tinder_user_profile : {{ id: {{ eq: {user_profile_id} }} }},
                tinder_job_profile : {{ id: {{ eq: {job_profile_id} }} }}
            }}
        """
        data_json = self.get_all_objects(filter=session_filter , **kwargs)
        data = self.get_extracted_from_user_job_data(data_json)
        return data
    
    def get_extracted_from_user_job_data(self, session_json):
        reaction_id = None
        if isinstance(session_json, list) and len(session_json) > 0:  
            first_item = session_json[0]  
            if 'data' in first_item and 'tinderUserReactions' in first_item['data']:
                user_reactions = first_item['data']['tinderUserReactions']['data']
                if len(user_reactions) != 0:
                    reaction_id = user_reactions[0]['id']                   
                
                return reaction_id
        return None    

class IpersonaSessionMessageSchema(LeapBaseClass):
    '''
    Schema Name:
        IPersonaMessages
    Attributes:
        i_persona_session: Relation with IPersonaMessages
        attributes: Json	
    '''
    def __init__(self, **kwargs) -> None:
        self.kwargs = copy.deepcopy(kwargs)
        super().__init__(**kwargs)
        
        self.table_single = kwargs.get('table_single', "")
        self.table = kwargs.get('table', "")
        self.data = kwargs.get('data', "")
        
        if not self.table_single:
            self.table_single = "iPersonaMessage"
            
        if not self.table:
            self.table = "iPersonaMessages"
            
        if not self.data:
            logger.info(f"Using default data schema for {self.table_single} ...")
            self.data = '''
                data {
                    id
                    attributes {
                        attributes
                        i_persona_session {
                            data {
                                id
                            }
                        }
                        %s
                    }
                }
            '''
        else:
            logger.info(f"Using passed data schema for {self.table_single} ...")
     
            
        self.type_map = {   
            "attributes": "JSON",
            "i_persona_session": "ID"
        }

        self.id_names_map = {  }
         
        self.data_template = copy.deepcopy(self.data)
        self.data = self.data%""
        _ = self.process_extra_data(kwargs.get('extra_data', []), inplace=True)
    
    def get_session_msg_by_id(self, sessionId, **kwargs):
        return self.exists(scol='id', sval=sessionId, op='eq', stype="ID", **kwargs)        
    
    def filter_by_session_id(self, sessionId, **kwargs):
        session_filter = f"""
            filters: {{
                i_persona_session : {{ id: {{ eq: {sessionId} }} }}
            }}
        """
        data_json = self.get_all_objects(filter=session_filter , **kwargs)
        data = self.get_session_msg_data(data_json)
        return data
    
    def get_all_session_msg(self, **kwargs):
        session_json = self.get_all_objects(**kwargs)  
        session = self.get_msg_data(session_json)
        return session       
        
    def save_message(self, params, **kwargs):
        session_json = self.save_or_update_object(params, **kwargs)
        session = self.get_extracted_data(session_json)
        return session
    
    def get_extracted_data(self, session_json):
        if isinstance(session_json, list) and len(session_json) > 0:  
            first_item = session_json[0]  
            if 'data' in first_item and 'createIPersonaMessage' in first_item['data']:
                session = first_item['data']['createIPersonaMessage']['data']
                return session
        return None    
    
    def get_msg_data(self, session_json):
        all_sessions_msg = []
        if isinstance(session_json, list) and len(session_json) > 0:  
            first_item = session_json[0]  
            if 'data' in first_item and 'iPersonaMessages' in first_item['data']:
                session_msg = first_item['data']['iPersonaMessages']['data']
                all_sessions_msg=session_msg
                return all_sessions_msg
                
    def get_session_msg_data(self, session_json):
        all_sessions_msg = []
        if isinstance(session_json, list) and len(session_json) > 0:  
            first_item = session_json[0]  
            if 'data' in first_item and 'iPersonaMessages' in first_item['data']:
                session_msg = first_item['data']['iPersonaMessages']['data']
                all_sessions_msg=session_msg

            extracted_messages = []
            for message in all_sessions_msg:
                message_attributes = message['attributes']            
                message_data = message_attributes['attributes']['message']
                extracted_messages.append({
                    "content": message_data['content'],
                    "user_type": message_data['user_type'],
                    "content_type": message_data['content_type']
                })

                    
            result = {
                "count": len(extracted_messages),
                "total": extracted_messages
            }
            return result
        return None 

class IpersonaSessionObserverSchema(LeapBaseClass):
    '''
    Schema Name:
        IPersonaObservers
    Attributes:
        i_persona_session: Relation with IPersonaObservers
        attributes: Json	
    '''
    def __init__(self, **kwargs) -> None:
        self.kwargs = copy.deepcopy(kwargs)
        super().__init__(**kwargs)
        
        self.table_single = kwargs.get('table_single', "")
        self.table = kwargs.get('table', "")
        self.data = kwargs.get('data', "")
        
        if not self.table_single:
            self.table_single = "iPersonaObserver"
            
        if not self.table:
            self.table = "iPersonaObservers"
            
        if not self.data:
            logger.info(f"Using default data schema for {self.table_single} ...")
            self.data = '''
                data {
                    id
                    attributes {
                        attributes
                        i_persona_session {
                            data {
                                id
                            }
                        }
                        %s
                    }
                }
            '''
        else:
            logger.info(f"Using passed data schema for {self.table_single} ...")
     
            
        self.type_map = {   
            "attributes": "JSON",
            "i_persona_session": "ID"
        }

        self.id_names_map = {  }
         
        self.data_template = copy.deepcopy(self.data)
        self.data = self.data%""
        _ = self.process_extra_data(kwargs.get('extra_data', []), inplace=True)
    
    def get_session_observer_by_id(self, sessionId, **kwargs):
        return self.exists(scol='id', sval=sessionId, op='eq', stype="ID", **kwargs)        
    
    def filter_by_observer_session_id(self, sessionId, **kwargs):
        session_filter = f"""
            filters: {{
                i_persona_session : {{ id: {{ eq: {sessionId} }} }}
            }}
        """
        data_json = self.get_all_objects(filter=session_filter , **kwargs)
        data = self.get_session_observerdata(data_json)
        return data
    
    def get_all_session_observer(self, **kwargs):
        session_json = self.get_all_objects(**kwargs)  
        session = self.get_session_observer_data(session_json)
        return session       
        
    def save_observer(self, params, **kwargs):
        session_json = self.save_or_update_object(params, **kwargs)
        session = self.get_extracted_data(session_json)
        return session
    
    def get_extracted_data(self, session_json):
        if isinstance(session_json, list) and len(session_json) > 0:  
            first_item = session_json[0]  
            if 'data' in first_item and 'createIPersonaObserver' in first_item['data']:
                session = first_item['data']['createIPersonaObserver']['data']
                return session
        return None    
    
    def get_session_observer_data(self, session_json):
        all_sessions_msg = []
        if isinstance(session_json, list) and len(session_json) > 0:  
            first_item = session_json[0]  
            if 'data' in first_item and 'iPersonaObservers' in first_item['data']:
                session_msg = first_item['data']['iPersonaObservers']['data']
                all_sessions_msg=session_msg
                return all_sessions_msg
                
class IpersonaAllUserSchema(LeapBaseClass):
    '''
    Schema Name:
        AllUsers
    Attributes:
        name: text
        role: text
        Batch: text	
    '''
    def __init__(self, **kwargs) -> None:
        self.kwargs = copy.deepcopy(kwargs)
        super().__init__(**kwargs)
        
        self.table_single = kwargs.get('table_single', "")
        self.table = kwargs.get('table', "")
        self.data = kwargs.get('data', "")
        
        if not self.table_single:
            self.table_single = "allUser"
            
        if not self.table:
            self.table = "allUser"
            
        if not self.data:
            logger.info(f"Using default data schema for {self.table_single} ...")
            self.data = '''
                data {
                    id
                    attributes {
                        name
                        role
                        Batch      
                      %s                                                   
                    }
                }
            '''
        else:
            logger.info(f"Using passed data schema for {self.table_single} ...")
     
            
        self.type_map = {    
            "name": "String",
            "role": "String",
            "Batch": "String"
        }

        self.id_names_map = {  }
         
        self.data_template = copy.deepcopy(self.data)
        self.data = self.data%""
        _ = self.process_extra_data(kwargs.get('extra_data', []), inplace=True)
    
    def get_alluser_by_id(self, all_user_id, **kwargs):
        data_json = self.exists(scol='id', sval= all_user_id, op='eq', stype="ID", **kwargs)       
        data = self.get_extracted_trainee_data(data_json)   
        result = {
            "name": data['attributes']['name'],
            "role": data['attributes']['role'],
            "Batch": data['attributes']['Batch']
        }
        return result
    
    def get_extracted_trainee_data(self, data_json):
        data = []
        if isinstance(data_json, dict) and len(data_json) > 0:  
            first_item = data_json  
            if 'data' in first_item and 'allUser' in first_item['data']:
                data_json = first_item['data']['allUser']['data']
                data = data_json
                return data
        return None    
    
class IpersonaProfileInformationSchema(LeapBaseClass):
    '''
    Schema Name:
        ProfileInformations
    Attributes:
        all_users: Relation with AllUsers
        gender: text
        nationality: text
    '''
    def __init__(self, **kwargs) -> None:
        self.kwargs = copy.deepcopy(kwargs)
        super().__init__(**kwargs)
        
        self.table_single = kwargs.get('table_single', "")
        self.table = kwargs.get('table', "")
        self.data = kwargs.get('data', "")
        
        if not self.table_single:
            self.table_single = "profileInformations"
            
        if not self.table:
            self.table = "profileInformations"
            
        if not self.data:
            logger.info(f"Using default data schema for {self.table_single} ...")
            self.data = '''
                data {
                    id
                    attributes {
                        gender
                        nationality      
                      %s                                                   
                    }
                }
            '''
        else:
            logger.info(f"Using passed data schema for {self.table_single} ...")
     
            
        self.type_map = {    
            "gender": "String",
            "nationality": "String",
        }

        self.id_names_map = {  }
         
        self.data_template = copy.deepcopy(self.data)
        self.data = self.data%""
        _ = self.process_extra_data(kwargs.get('extra_data', []), inplace=True)
    
    def filter_by_all_user_id(self, all_user_id, **kwargs):
        session_filter = f"""
            filters: {{
                all_user : {{ id: {{ eq: {all_user_id} }} }}
            }}
        """
        data_json = self.get_all_objects(filter=session_filter , **kwargs)
        data = self.get_extracted_data(data_json)
        result = {
            "gender": data['attributes']['gender'],
            "nationality": data['attributes']['nationality']
        }
        return result
    
    def get_extracted_data(self, data_json):
        data = []
        if isinstance(data_json, list) and len(data_json) > 0:  
            first_item = data_json[0]
            if 'data' in first_item and 'profileInformations' in first_item['data']:
                data_json = first_item['data']['profileInformations']['data'][0]
                data = data_json
                return data
        return None    