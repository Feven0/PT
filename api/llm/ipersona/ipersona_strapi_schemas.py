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
            "i_persona_observer": "ID"
        }

        self.id_names_map = {  }
         
        self.data_template = copy.deepcopy(self.data)
        self.data = self.data%""
        _ = self.process_extra_data(kwargs.get('extra_data', []), inplace=True)
    
    def get_session_by_id(self, idval, **kwargs):
        return self.exists(scol='id', sval=idval, op='eq', stype="ID", **kwargs)        
    
    def filter_by_id(self, vid, **kwargs):
        session_filter = f"""
            filters: {{
                i_persona_observer : {{ id: {{ eq: {vid} }} }}
            }}
        """
        return self.get_all_objects(filter=session_filter , **kwargs)
    
    def filter_by_with_more_ids(self, vid, tid, **kwargs):
        session_filter = f"""
            filters: {{
                i_persona_observer : {{ id: {{ eq: {vid} }} }},
                tinder_user_profile : {{ id: {{ eq: {tid} }} }}
            }}
        """
        return self.get_all_objects(filter=session_filter , **kwargs)

    def get_all_sessions(self, **kwargs):
        return self.get_all_objects(**kwargs)
        
    def save_session(self, params, **kwargs):
        return self.save_or_update_object(params, **kwargs)
    
    def save_if_new_user(self, scol, params, **kwargs):
        return self.save_if_new(scol, params, **kwargs)
    
    def update_session(self, params, **kwargs):
        if self.id_name() not in params:
            logger.error("Id is missing for update!")
            return []
        return self.save_or_update_object(params, **kwargs)

    def delete_session(self, ids, **kwargs):
        return self.delete_objects_by_id(ids, **kwargs)
