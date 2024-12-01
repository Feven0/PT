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


class AllUserSchema(LeapBaseClass):
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
            self.table_single = "gmeet"
            
        if not self.table:
            self.table = "gmeets"
            
        if not self.data:
            logger.info(f"Using default data schema for {self.table_single} ...")
            self.data = '''
                data {
                    id
                    attributes {
                        number_days
                        week
                        trainee {
                            data {
                                attributes {
                                email
                                all_user {
                                    data {
                                        id
                                        attributes {
                                            name
                                            email
                                        }
                                    }
                                }
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
            "rank": "String",
            "week_detail": "JSON",
            "trainee": "ID",
            "week": "String",
            "number_days": "INT",
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
        res = self.exists(scol='all_user', sval=auid, op='eq', stype="ID", **kwargs)
        if res:
            if isinstance(res, list):
                res = res[0]
            return res.get('trainee_id', "")
        else:
            logger.error(f"Trainee not found for all_user: {auid}")            
            return ""
        
    def get_users(self,  **kwargs):
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
    
    
    
     
# class GmeetSchema(LeapBaseClass):
#     '''
#     Schema Name:
#         gmeets
#     Attributes:
#         rank: Text
#         week_detail: JSON
#         week: Text
#         trainee: Relation with Trainee   
#         number_days: Number
#     '''
#     def init(self, **kwargs) -> None:
#         self.kwargs = copy.deepcopy(kwargs)
#         super().init(**kwargs)
        
#         self.table_single = kwargs.get('table_single', "")
#         self.table = kwargs.get('table', "")
#         self.data = kwargs.get('data', "")
        
#         if not self.table_single:
#             self.table_single = "gmeet"
            
#         if not self.table:
#             self.table = "gmeets"
            
#         if not self.data:
#             logger.info(f"Using default data schema for {self.table_single} ...")
#             self.data = '''
#                 data {
#                     id
#                     attributes {
#                         number_days
#                         week
#                         trainee {
#                             data {
#                                 attributes {
#                                 email
#                                 all_user {
#                                     data {
#                                         id
#                                         attributes {
#                                             name
#                                             email
#                                         }
#                                     }
#                                 }
#                                 }
#                             }
#                         }
#                         %s
#                     }
#                 }
#             '''
#         else:
#             logger.info(f"Using passed data schema for {self.table_single} ...")
     
            
#         self.type_map = {
#             "rank": "String",
#             "week_detail": "JSON",
#             "trainee": "ID",
#             "week": "String",
#             "number_days": "INT",
#         }

#         self.id_names_map = {}
         
#         # process extra data
#         self.data_template = copy.deepcopy(self.data)
#         self.data = self.data%""
#         _ = self.process_extra_data(kwargs.get('extra_data', []), inplace=True)


#     def get_gmeet(self, gmeet_id, **kwargs): 
#         kwargs['scol'] = 'id'
#         kwargs['sval'] = gmeet_id
#         kwargs['op'] = 'eq'
#         kwargs['stype'] = "ID"       
#         return self.exists(**kwargs)
    
    def get_all_gmeets(self, limit=0, filter="", **kwargs):
        gmeets = self.get_all_objects(limit=limit,  filter=filter, **kwargs)        
        return gmeets
    
    def get_all_trainees_gmeets_data(self,week,batch, limit=0, filter="", **kwargs):
        print("________________ this is called ___________")
        gmeet_filter = f"""
                filters: {{
                    week: {{ eq: "week{week}" }},
                    trainee: {{ 
                        Status: {{ eq: "Accepted" }}, 
                        batch: {{ Batch: {{ eq: {batch} }} }}
                        }} 
                    }}
            """
        gmeets = self.get_all_gmeets(limit=limit,  filter=gmeet_filter,dataframe=False, **kwargs) 
        print('gmeets',gmeets)       
        trainee_info = []
        
        # Process each trainee's data
        for trainee_data in gmeets:
            # Extract required information
            all_user_id = trainee_data['trainee_all_user_id']
            name = trainee_data['trainee_all_user_name']
            email = trainee_data['trainee_email']
            number_days = trainee_data['number_days']
            
            # Append the information to the list
            trainee_info.append({
                'all_user_id': all_user_id,
                'email': email,
                'name': name,
                'number_days': number_days
            })    


        return trainee_info
        
#     def delete_gmeets(self, gmeet_ids, **kwargs):
#         return self.delete_objects_by_id(gmeet_ids, **kwargs)
    
#     def save_gmeet(self, gmeet_params, **kwargs):
#         return self.save_or_update_object(gmeet_params, **kwargs)
    
#     def save_if_new_gmeet(self, params, **kwargs):
#         logger.info('Saving gmeet item ...')
#         id_name = self.id_name()
#         id_val = kwargs.get(id_name, "")
#         scol = kwargs.pop('scol', 'slug')
        
#         kwargs['overwrite'] = kwargs.get('overwrite', True) 
#         if id_val:
#             logger.info(f'{id_name}={id_val} is passed, updating table={self.table_single} entry ...')
#             params[id_name] = kwargs[id_name]
#             added_item_ids = self.save_gmeet(params, **kwargs)
#         else:                                        
#             added_item_ids = self.save_if_new(scol, params, **kwargs)
            
#         if added_item_ids:
#             params[id_name] = added_item_ids[0]
                        
#         return params

#     def update_gmeet(self, params, **kwargs):
#         if self.id_name() not in params:
#             logger.error("gmeet ID is missing for update!")
#             return []
#         return self.save_or_update_object(params, **kwargs)




# import os, sys
# import re
# import copy
# import json
# from datetime import datetime, timedelta


# #from .pathfig import *


# from api import config
# from api.modules.eagle_base import LeapBaseClass
# #from api.modules.leap_trainee import TraineeSchema
# #
# from api.utils.logger import LLPackerLogger
# logger = LLPackerLogger(os.path.basename(file))
# from collections import defaultdict

# #
# capitalize = lambda x: x[0].upper() + x[1:]

   
# class AssignmentSchema(LeapBaseClass):
#     '''
#     Schema Name:
#         assignments
#     Attributes:
#         assignment_type: Text
#         assignment_submission_content: Text
#         gclass_submission_identifier: Text
#         trainee: Relation with Trainee   
#         assignment_responses: Relation with AssignmentResponse
#         assignment_category: Relation with AssignmentCategory
#     '''
#     def init(self, **kwargs) -> None:
#         self.kwargs = copy.deepcopy(kwargs)
#         super().init(**kwargs)
        
#         self.table_single = kwargs.get('table_single', "")
#         self.table = kwargs.get('table', "")
#         self.data = kwargs.get('data', "")
        
#         if not self.table_single:
#             self.table_single = "assignment"
            
#         if not self.table:
#             self.table = "assignments"
            
#         if not self.data:
#             logger.info(f"Using default data schema for {self.table_single} ...")
#             self.data = '''
#                 data {
#                     id
#                     attributes {
#                         gclass_submission_identifier
#                         assignment_submission_content
#                         trainee {
#                             data {
#                                 id
#                                 attributes {
#                                     email
#                                     all_user {
#                                         data {
#                                             id
#                                             attributes {
#                                                 name
#                                                 email
#                                                 profile_information{
#                                                     data {
#                                                         id
#                                                         attributes {
#                                                             gender
#                                                         }
#                                                     }
#                                                 }
#                                             }
#                                         }
#                                     }
#                                 }
#                             }
#                         }
#                         assignment_category {
#                             data {
#                                 id
#                                 attributes {
#                                     topic
#                                     name
#                                 }
#                             }
#                         }
#                         %s
#                     }
#                 }
#             '''
#         else:
#             logger.info(f"Using passed data schema for {self.table_single} ...")
     
            
#         self.type_map = {
#             "assignment_type": "String",
#             "assignment_submission_content": "String",
#             "gclass_submission_identifier": "String",
#             "trainee": "ID",
#             "assignment_responses": "ID",
#             "assignment_category": "ID"
#         }

#         self.id_names_map = {}
         
#         # process extra data
#         self.data_template = copy.deepcopy(self.data)
#         self.data = self.data%""
#         _ = self.process_extra_data(kwargs.get('extra_data', []), inplace=True)


#     def get_assignment(self, assignment_id, **kwargs): 
#         kwargs['scol'] = 'id'
#         kwargs['sval'] = assignment_id
#         kwargs['op'] = 'eq'
#         kwargs['stype'] = "ID"       
#         return self.exists(**kwargs)


#     def get_all_assignments(self, limit=0, filter="", **kwargs):
#         assignments = self.get_all_objects(limit=limit,  filter=filter, **kwargs, )        
#         return assignments 
    
#     def get_all_trainees_assignments_data(self, week,batch, limit=0, filter="", **kwargs):
#         assignment_filter = f"""
#             filters:
#                     {{
#                         trainee: {{ Status: {{ eq: "Accepted" }} }},
#                         assignment_category: {{
#                             topic: {{ eq: "{week}" }},
#                             batch: {{ Batch: {{ eq: {batch} }} }}
#                         }}
#                     }}
#                 """
#         assignments = self.get_all_assignments(limit=limit,  filter=assignment_filter,dataframe=False, **kwargs)        
#         trainee_info = defaultdict(lambda: {"id": None, "submissions": 0})
    
#         # Process each assignment submission
#         for assignment in assignments:
#             email = assignment['trainee_email']
#             name = assignment['trainee_all_user_name']

#             all_user_id = assignment['trainee_all_user_id']
#             has_submission_content = bool(assignment.get('assignment_submission_content_url', []))
#             # Update trainee information
#             trainee_info[email]["id"] = all_user_id
#             trainee_info[email]["name"] = name

#             if has_submission_content:
#                 trainee_info[email]["submissions"] += 1

#         trainee_list = [
#             {"email": email, "all_user_id": info["id"], "submissions": info["submissions"], "name":info['name']}
#             for email, info in trainee_info.items()
#         ]

#         return trainee_list
    
#     def get_assignments_by_categories(self, assignment_category_ids, limit=0, **kwargs):
       
#         category_filter = f"""
#             filters: {{
#                 trainee: {{ Status: {{ eq: "Accepted" }} }},
#                 assignment_category: {{ id: {{ in: {assignment_category_ids} }} }}
#             }}
#         """
#         # returns the most recent assignment response
#         name = '''assignment_responses(
#           sort: "createdAt:desc"
#           pagination: { limit: 1 }
#         )'''
#         value = '''
#             data { 
#                 id  
#                 attributes { content, mark,llm_response } 
#             }
#         '''

#         extra_data = [{'name':name, 'value':value, 'type':'ID'}]
#         assignments = self.get_all_assignments(limit=limit, filter=category_filter,extra_data=extra_data, **kwargs)
#         # assignment_grouper = AssignmentDataGrouper()
#         # assignments = [assignment_grouper.group_data(assignment) for assignment in assignments] 
#         return assignments
        
#     def delete_assignments(self, assignment_ids, **kwargs):
#         return self.delete_objects_by_id(assignment_ids, **kwargs)
    
#     def save_assignment(self, assignment_params, **kwargs):
#         return self.save_or_update_object(assignment_params, **kwargs)
    
#     def save_if_new_assignment(self, params, **kwargs):
#         logger.info('Saving assignment item ...')
#         id_name = self.id_name()
#         id_val = kwargs.get(id_name, "")
#         scol = kwargs.pop('scol', 'slug')
        
#         kwargs['overwrite'] = kwargs.get('overwrite', True) 
#         if id_val:
#             logger.info(f'{id_name}={id_val} is passed, updating table={self.table_single} entry ...')
#             params[id_name] = kwargs[id_name]
#             added_item_ids = self.save_assignment(params, **kwargs)
#         else:                                        
#             added_item_ids = self.save_if_new(scol, params, **kwargs)
            
#         if added_item_ids:
#             params[id_name] = added_item_ids[0]
                        
#         return params

#     def update_assignment(self, params, **kwargs):
#         if self.id_name() not in params:
#             logger.error("Assignment ID is missing for update!")
#             return []
#         return self.save_or_update_object(params, **kwargs)
