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


class IpersonaSchema(LeapBaseClass):
    '''
    Schema Name:
        AllUser
    Attributes:
        all_user: Relation with Trainee 	
        batch: Relation with Job 	
        email: Text 	
        trainee_id: Text
    '''
    def __init__(self, **kwargs) -> None:
        self.kwargs = copy.deepcopy(kwargs)
        super().__init__(**kwargs)
        
        #
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
                                attributes {
                                    attributes
                                    metadata
                                }
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

        self.id_names_map = {
            # 'Batch': 'batch',
            # 'createdAt': 'created_at',
            # 'updatedAt': 'updated_at'            
            }
         
        # process extra data
        self.data_template = copy.deepcopy(self.data)
        self.data = self.data%""
        _ = self.process_extra_data(kwargs.get('extra_data', []), inplace=True)
    
    def get_trainee(self, idval, **kwargs):
        return self.exists(scol='id', sval=idval, op='eq', stype="ID", **kwargs)        
    
    def get_tid_from_auid(self, auid, **kwargs):
        res = self.exists(scol='slug', sval=auid, op='eq', stype="ID", **kwargs)
        if res:
            if isinstance(res, list):
                res = res[0]
            return res.get('trainee_id', "")
        else:
            logger.error(f"Trainee not found for iPersonaSession: {auid}")            
            return ""
        
    def get_sessions(self,  **kwargs):
        return self.get_all_objects(**kwargs)
    
    def get_all_users(self, **kwargs):
        return self.get_all_objects(**kwargs)
    
    def delete_users(self, ids, **kwargs):
        return self.delete_objects_by_id(ids, **kwargs)
    
    def save_user(self, params, **kwargs):
        return self.save_or_update_object(params, **kwargs)
    
    def save_if_new_user(self, scol, params, **kwargs):
        return self.save_if_new(scol, params, **kwargs)
    
    def update_user(self, params, **kwargs):
        if self.id_name() not in params:
            logger.error("Id is missing for update!")
            return []
        return self.save_or_update_object(params, **kwargs)

    
    def preprocess_single_user_entry(self, payload, **kwargs):
        pass
    
    def create_single_entry(self, payload, **kwargs):
        pass
    
    def create_multiple_entries(self, payload, **kwargs):
        pass
    
