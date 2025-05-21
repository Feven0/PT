import os, sys
import re
import copy
import json
from datetime import datetime, timedelta
import logging


from api import config
from api.modules.leap_base import LeapBaseClass
from api.utils.logger import LLPackerLogger
logger = LLPackerLogger(__file__)

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
    def __init__(self, run_stage='', **kwargs) -> None:
        self.kwargs = copy.deepcopy(kwargs)
        super().__init__(run_stage=run_stage, **kwargs)   

        
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
                        i_persona_messages(pagination:{start: 0, limit:-1}){
                            data {
                                id
                                attributes {
                                    attributes
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
                        tinder_template {
                            data {
                                id
                            }
                        }
                        challenge_document {
                            data {
                                id
                            }
                        }
                        metadata
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
            "i_persona_messages": "ID",
            "tinder_job_profile": "ID",
            "tinder_user_profile": "ID",
            "tinder_template": "ID",
            "challenge_document": "ID",
            "metadata": "JSON"
        }

        self.id_names_map = {  }
         
        self.data_template = copy.deepcopy(self.data)
        self.data = self.data%""
        _ = self.process_extra_data(kwargs.get('extra_data', []), inplace=True)
    
    def get_session_by_id(self, sessionId, **kwargs):
        data = self.exists(scol='id', sval=sessionId, op='eq', stype="ID", **kwargs)  
        data = self.get_session_data(data)   
        return data
    
    def get_by_id(self, sessionId, **kwargs):
        data_json = self.exists(scol='id', sval=sessionId, op='eq', stype="ID", **kwargs)  
        data = self.get_session_data(data_json)  

        data_msg = data.get('attributes', {}).get('i_persona_messages', {}).get('data', {}) if data else None 
        data_msg = self.get_session_msg_data(data_msg)
        response = {
            "id": data.get('id', {}),
            "status": data.get('attributes', {}).get('status', {}),
            "template_id": data.get('attributes', {}).get('attributes', {}).get('template_id', {}),
            "challenge_id": data.get('attributes', {}).get('attributes', {}).get('challenge_id', {}),
            "chat": data_msg
        }
        return response
    
    def filter_by_observer_id(self, vid, **kwargs):
        try:
            if not vid:
                logger.error("Observer ID (vid) is missing!")
                return None
            
            session_filter = f"""
                filters: {{
                    i_persona_observer : {{ id: {{ eq: {vid} }} }}
                }}
            """

            data_json = self.get_all_objects(filter=session_filter, **kwargs)

            if not data_json:
                logger.warn(f"No data found for Observer ID: {vid}")
                return None
            
            return data_json

        except Exception as e:
            logger.error(f"Error fetching data for Observer ID {vid}: {str(e)}")
            return {'error': f"Error fetching data for Observer ID {vid}: {str(e)}"}
    
    def filter_by_tinder_user_profile_id(self, user_profile_id, cursor={}, since=None, limit=None, **kwargs):
        try:
            if not user_profile_id:
                logger.error("User Profile ID is missing!")
                return None

            # Step 1: Build the filter for 'tinder_user_profile'
            session_filter = f"""
                filters: {{
                    tinder_user_profile : {{ id: {{ eq: {user_profile_id} }} }}
            """

            # Step 2: Add 'since' filter if provided
            if since:
                since_date = (datetime.utcnow() - timedelta(days=since)).isoformat() + 'Z'
                session_filter += f', createdAt: {{ gte: "{since_date}" }}'

            session_filter += " }"

            # Step 3: Fetch data with the filter
            data_json, cursors = self.get_all_objects(filter=session_filter, cursor=cursor, **kwargs)

            # Step 4: Extract session data
            data = self.get_sessions_data(data_json)

            # Step 5: Apply 'limit' if provided
            if limit and data:
                data = data[:limit]

            return data, cursors

        except Exception as e:
            logger.error(f"Error filtering by tinder_user_profile_id: {e}")
            return None
    
    def filter_by_template_id(self, template_id, cursor={}, since=None, limit=None, **kwargs):
        try:
            if not template_id:
                logger.error("Template ID is missing!")
                return None

            # Step 1: Build the filter for 'tinder_user_profile'
            session_filter = f"""
                filters: {{
                    tinder_template : {{ id: {{ eq: {template_id} }} }}
            """

            # Step 2: Add 'since' filter if provided
            if since:
                since_date = (datetime.utcnow() - timedelta(days=since)).isoformat() + 'Z'
                session_filter += f', createdAt: {{ gte: "{since_date}" }}'

            session_filter += " }"

            # Step 3: Fetch data with the filter
            data_json, cursors = self.get_all_objects(
                filter=session_filter, 
                cursor=cursor,
                **kwargs)
            
            # Step 4: Extract session data
            data = self.get_sessions_data(data_json)

            # Step 5: Apply 'limit' if provided
            if limit and data:
                data = data[:limit]

            return data, cursors

        except Exception as e:
            logger.error(f"Error filtering by template_id: {e}")
            return None
        
    def filter_by_with_user_job_id(self, user_profile_id, job_profile_id, **kwargs):
        try:
            if not user_profile_id or not job_profile_id:
                logger.error("User Profile ID or Job Profile ID is missing!")
                return None
            
            session_filter = f"""
                filters: {{
                    tinder_user_profile : {{ id: {{ eq: {user_profile_id} }} }},
                    tinder_job_profile : {{ id: {{ eq: {job_profile_id} }} }}
                }}
            """
            data_json = self.get_all_objects(filter=session_filter, **kwargs)

            data = self.get_sessions_data(data_json)

            if data is None:
                logger.warn(f"No session data found for User Profile ID {user_profile_id} and Job Profile ID {job_profile_id}.")
                return None
            
            return data

        except Exception as e:
            logger.error(f"Error fetching session data for User Profile ID {user_profile_id} and Job Profile ID {job_profile_id}: {str(e)}")
            return {'error': f"Error fetching session data for User Profile ID {user_profile_id} and Job Profile ID {job_profile_id}: {str(e)}"}
    
    def filter_by_with_user_template_id(self, user_profile_id, template_id, **kwargs):
        try:
            if not user_profile_id or not template_id:
                logger.error("User Profile ID or Template ID is missing!")
                return None
            
            session_filter = f"""
                filters: {{
                    tinder_user_profile : {{ id: {{ eq: {user_profile_id} }} }},
                    tinder_template : {{ id: {{ eq: {template_id} }} }}
                }}
            """

            data_json = self.get_all_objects(filter=session_filter, **kwargs)

            data = self.get_sessions_data(data_json)

            if data is None:
                logger.warn(f"No session data found for User Profile ID {user_profile_id} and Template ID {template_id}.")
                return None
            
            return data

        except Exception as e:
            logger.error(f"Error fetching session data for User Profile ID {user_profile_id} and Template ID {template_id}: {str(e)}")
            return {'error': f"Error fetching session data for User Profile ID {user_profile_id} and Template ID {template_id}: {str(e)}"}
    
    def filter_by_with_user_challenge_id(self, user_profile_id, challenge_id, **kwargs):
        try:
            if not user_profile_id or not challenge_id:
                logger.error("User Profile ID or Challenge ID is missing!")
                return None
            
            session_filter = f"""
                filters: {{
                    tinder_user_profile : {{ id: {{ eq: {user_profile_id} }} }},
                    challenge_document : {{ id: {{ eq: {challenge_id} }} }}
                }}
            """

            data_json = self.get_all_objects(filter=session_filter, **kwargs)

            data = self.get_sessions_data(data_json)

            if data is None:
                logger.warn(f"No session data found for User Profile ID {user_profile_id} and Challenge ID {challenge_id}.")
                return None
            
            return data

        except Exception as e:
            logger.error(f"Error fetching session data for User Profile ID {user_profile_id} and Challenge ID {challenge_id}: {str(e)}")
            return {'error': f"Error fetching session data for User Profile ID {user_profile_id} and Challenge ID {challenge_id}: {str(e)}"}
    
    def get_all_sessions(self, cursor={}, **kwargs):
        try:
            if not cursor:
                cursor = True
                
            data, cursor = self.get_all_objects(cursor=cursor, **kwargs)
 
            session = self.get_sessions_data(data)

            if session is None:
                logger.warn("No session data found.")
                return None
            
            return session, cursor

        except Exception as e:
            logger.error(f"Error fetching all sessions: {str(e)}")
            return {'error': f"Error fetching all sessions: {str(e)}"}
    
    def get_alladmin_sessions(self, **kwargs):
        try:
            data = self.get_all_objects(**kwargs)
 
            session = self.get_sessions_data(data)

            if session is None:
                logger.warn("No session data found.")
                return None
            
            return session

        except Exception as e:
            logger.error(f"Error fetching all sessions: {str(e)}")
            return {'error': f"Error fetching all sessions: {str(e)}"}
        
    def save_session(self, params, **kwargs):
        try:
            session_json = self.save_or_update_object(params, **kwargs)

            session = self.get_extracted_data(session_json)

            if session is None:
                logger.warn("Failed to save session, no data extracted.")
                return None
            
            return session

        except Exception as e:
            logger.error(f"Error saving session: {str(e)}")
            return {'error': f"Error saving session: {str(e)}"}
        
    def save_if_new_user(self, scol, params, **kwargs):
        return self.save_if_new(scol, params, **kwargs)
    
    def update_session(self, params, **kwargs):
        try:
            if self.id_name() not in params:
                logger.error("Id is missing for update!")
                return []
            
            return self.save_or_update_object(params, **kwargs)

        except Exception as e:
            logger.error(f"Error updating session: {str(e)}")
            return {'error': f"Error updating session: {str(e)}"}

    def delete_session(self, ids, **kwargs):
        try:
            if not ids:
                logger.error("No IDs provided for deletion!")
                return {'error': "No IDs provided for deletion!"}
            
            return self.delete_objects_by_id(ids, **kwargs)

        except Exception as e:
            logger.error(f"Error deleting session(s) with IDs {ids}: {str(e)}")
            return {'error': f"Error deleting session(s) with IDs {ids}: {str(e)}"}

    def get_extracted_data(self, session_json):
        try:
            if isinstance(session_json, list) and len(session_json) > 0:
                for entry in session_json:
                    if 'data' in entry:
                        session = entry.get('data')
                        return session
                        
            # if isinstance(session_json, list) and len(session_json) > 0:  
            #     first_item = session_json[0]  
            #     if 'data' in first_item and 'createIPersonaSession' in first_item['data']:
            #         session = first_item['data']['createIPersonaSession']['data']
            #         return session
            
            logger.warn("No valid data found in the session JSON.")
            return None

        except Exception as e:
            logger.error(f"Error extracting data from session JSON: {str(e)}")
            return {'error': f"Error extracting data from session JSON: {str(e)}"}
  
    def get_sessions_data(self, session_json):
        try:
            all_sessions = []
            if isinstance(session_json, list) and len( session_json) > 0:
                for entry in session_json:
                    if 'data' in entry:
                        trainee = entry.get('data')                            
                        return trainee
            # if isinstance(session_json, list) and len(session_json) > 0:  
            #     first_item = session_json[0]  
            #     if 'data' in first_item and 'iPersonaSessions' in first_item['data']:
            #         session = first_item['data']['iPersonaSessions']['data']
            #         all_sessions = session
            #         return all_sessions

            logger.warn("No sessions data found in the session JSON.")
            return None

        except Exception as e:
            logger.error(f"Error extracting session data from session JSON: {str(e)}")
            return {'error': f"Error extracting session data from session JSON: {str(e)}"}
    
    def get_session_data(self, session_json):
        try:
            all_sessions = []
            if isinstance(session_json, dict) and len(session_json) > 0:
                if 'data' in session_json:
                    return session_json['data']
                        
            # if isinstance(session_json, dict) and len(session_json) > 0:  
            #     first_item = session_json  
            #     if 'data' in first_item and 'iPersonaSession' in first_item['data']:
            #         session = first_item['data']['iPersonaSession']['data']
            #         all_sessions = session
            #         return all_sessions
            
            logger.warn("No session data found in the session JSON.")
            return None

        except Exception as e:
            logger.error(f"Error extracting session data from session JSON: {str(e)}")
            return {'error': f"Error extracting session data from session JSON: {str(e)}"}

    def get_session_msg_data(self, all_sessions_msg):
            try:
                # all_sessions_msg = []
            
                if isinstance(all_sessions_msg, list) and len( all_sessions_msg) > 0:
                    # for entry in session_json:
                    #     if 'data' in entry:
                    #         all_sessions_msg = entry.get('data')                         

                    extracted_messages = []
                    for message in all_sessions_msg:
                        message_attributes = message.get('attributes', {}).get('attributes', {})
                        if message_attributes:
                            message_data = message_attributes.get('message', {})
                            extracted_messages.append({
                                "content": message_data.get('content', ""),
                                "user_type": message_data.get('user_type', ""),
                                # "template_id": message_data.get('template_id', ""),
                                "content_type": message_data.get('content_type', "")
                            })

                    return extracted_messages

                logger.warn("No session message data found in session JSON.")
                return None

            except Exception as e:
                logger.error(f"Error extracting session message data: {str(e)}")
                return {'error': f"Error extracting session message data: {str(e)}"}

class IpersonaTraineeSchema(LeapBaseClass):
    '''
    Schema Name:
        TinderUserProfiles
    Attributes:
        all_users: Relation with AllUsers
        attributes: Json	
    '''
    def __init__(self, run_stage='', **kwargs) -> None:
        self.kwargs = copy.deepcopy(kwargs)
        super().__init__(run_stage=run_stage, **kwargs)   

        
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
        """
        Fetches trainee data by user profile ID.

        Parameters:
        ----------
        user_profile_id : int or str
            The user profile ID to fetch trainee data.
        kwargs : dict
            Additional filtering arguments.

        Returns:
        -------
        dict or None
            Trainee data if found, otherwise None.
        """
        try:
            if not user_profile_id:
                logger.warn("Invalid or missing user_profile_id")
                return None
            
            data_json = self.exists(scol='id', sval=user_profile_id, op='eq', stype="ID", **kwargs)
            if not data_json:
                logger.warn(f"No data found for user_profile_id: {user_profile_id}")
                return None

            data = self.get_extracted_trainee_data(data_json)
            if not data:
                logger.warn(f"No extracted data for user_profile_id: {user_profile_id}")
                return None

            return data

        except Exception as e:
            logger.error(f"Error fetching trainee by ID {user_profile_id}: {e}")
            return None
 
    
    def filter_by_alluser_id(self, all_user_id, **kwargs):
        """
        Fetches trainee data filtered by all user ID.

        Parameters:
        ----------
        all_user_id : int or str
            The ID of the user to filter sessions by.
        kwargs : dict
            Additional keyword arguments.

        Returns:
        -------
        list or None
            Filtered trainee data or None if an error occurs.
        """
        try:
            if not all_user_id:
                logger.warn("Invalid or missing all_user_id")
                return None

            session_filter = f"""
                filters: {{
                    all_users : {{ id: {{ eq: {all_user_id} }} }}
                }}
            """
            data_json = self.get_all_objects(filter=session_filter, **kwargs)
            if not data_json:
                logger.warn(f"No trainee profile data found for all_user_id: {all_user_id}")
                return None

            data = self.get_extracted_data(data_json)
            if not data:
                logger.warn(f"No extracted data for all_user_id: {all_user_id}")
                return None

            return data

        except Exception as e:
            logger.error(f"Error filtering trainee by all_user_id {all_user_id}: {e}")
            return None


    def get_all_trainees_info(self, **kwargs):
        """
        Fetches all trainees' information.

        Parameters:
        ----------
        kwargs : dict
            Additional arguments to filter the trainees.

        Returns:
        -------
        list or None
            A list of all trainees' information or None if an error occurs.
        """
        try:
            trainee_json = self.get_all_objects(**kwargs)
            if not trainee_json:
                logger.warn("No trainee data found for all trainees.")
                return None

            trainee = self.get_extracted_data(trainee_json)
            if not trainee:
                logger.warn("No extracted data for all trainees.")
                return None

            return trainee

        except Exception as e:
            logger.error(f"Error fetching all trainees' info: {e}")
            return None

    
    def get_extracted_data(self, trainee_json):
        """
        Extracts relevant trainee data from a JSON response.

        Parameters:
        ----------
        trainee_json : dict
            The JSON data containing trainee information.

        Returns:
        -------
        list or None
            A list of extracted trainee data or None if no data is found.
        """
        try:
            if isinstance(trainee_json, list) and len( trainee_json) > 0:
                for entry in trainee_json:
                    if 'data' in entry:
                        for trainee in entry.get('data'):                            
                            return trainee
                # first_item =  trainee_json[0]
                # if 'data' in first_item and 'tinderUserProfiles' in first_item['data']:
                #     trainee = first_item['data']['tinderUserProfiles']['data']
                #     if not trainee:
                #         logger.warn("No trainee profile data found in the extracted data.")
                #         return None
                #     return trainee

            logger.warn("Invalid trainee_json format or missing data.")
            return None

        except Exception as e:
            logger.error(f"Error extracting trainee profile data: {e}")
            return None
    
    
    def get_extracted_trainee_data(self, trainee_json):
        """
        Extracts relevant trainee data from a JSON response.

        Parameters:
        ----------
        data_json : dict
            The JSON data containing trainee information.

        Returns:
        -------
        dict or None
            A dictionary of trainee data or None if no data is found.
        """
        try:
            # if isinstance(trainee_json, dict) and len( trainee_json) > 0:
            #     for entry in trainee_json:
            #         if 'data' in entry:
            #             for trainee in entry.get('data'):                            
            #                 return trainee
            
            if isinstance(trainee_json, dict) and 'data' in trainee_json:
                # Return the entire 'data' object
                return trainee_json['data']
            
            # if isinstance(data_json, dict) and len(data_json) > 0:
            #     first_item = data_json
            #     if 'data' in first_item and 'tinderUserProfile' in first_item['data']:
            #         trainee_data = first_item['data']['tinderUserProfile']['data']
            #         if not trainee_data:
            #             logger.warn("No trainee data found in the extracted data.")
            #             return None
            #         return trainee_data

            logger.warn("Invalid data_json format or missing data.")
            return None

        except Exception as e:
            logger.error(f"Error extracting trainee data: {e}")
            return None  

class IpersonaJobSchema(LeapBaseClass):
    '''
    Schema Name:
        TinderJobProfiles
    Attributes:
        id: ID,
        attributes: Json	
    '''
    def __init__(self, run_stage='', **kwargs) -> None:
        self.kwargs = copy.deepcopy(kwargs)
        super().__init__(run_stage=run_stage, **kwargs)   

        
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
                        title
                        applyLink
                        level
                        attributes    
                        i_persona_sessions {
                            data {
                                id
                                attributes {
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
                                }
                            }
                        } 
                        tinder_templates(pagination:{start:0, limit:-1}) {
                            data {
                                id
                            }
                        }
                        createdAt
                      %s                                                   
                    }
                }
            '''
        else:
            logger.info(f"Using passed data schema for {self.table_single} ...")
     
            
        self.type_map = {    
            "id": "ID",
            "attributes": "JSON",
            "i_persona_sessions": "ID",
            "tinder_templates": "ID"
        }

        self.id_names_map = {  }
         
        self.data_template = copy.deepcopy(self.data)
        self.data = self.data%""
        _ = self.process_extra_data(kwargs.get('extra_data', []), inplace=True)
    
    def get_job_by_id(self, idval, **kwargs):
        return self.exists(scol='id', sval=idval, op='eq', stype="ID", **kwargs)        
    
    def filter_by_job_id(self, job_profile_id, **kwargs):
        """
        Fetches job data filtered by job profile ID.

        Parameters:
        ----------
        job_profile_id : int or str
            The job profile ID to filter jobs by.
        kwargs : dict
            Additional filtering arguments.

        Returns:
        -------
        list or None
            Filtered job data or None if an error occurs.
        """
        try:
            if not job_profile_id:
                logger.warn("Invalid or missing job_profile_id")
                return None

            job_filter = f"""
                filters: {{
                    id : {{ eq: {job_profile_id} }} 
                }}
            """
            data_json = self.get_all_objects(filter=job_filter, **kwargs)
            if not data_json:
                logger.warn(f"No job data found for job_profile_id: {job_profile_id}")
                return None
            
            data = self.get_extracted_data(data_json)
            if not data:
                logger.warn(f"No extracted data for job_profile_id: {job_profile_id}")
                return None

            return data

        except Exception as e:
            logger.error(f"Error filtering jobs by job_profile_id {job_profile_id}: {e}")
            return None

    def get_extracted_data(self, job_json):
        """
        Extracts relevant job or job data from a JSON response.

        Parameters:
        ----------
        job_json : dict
            The JSON data containing job or job information.

        Returns:
        -------
        list or None
            A list of extracted job or job data or None if no data is found.
        """
        try:
            if isinstance(job_json, list) and len(job_json) > 0:
                for entry in job_json:
                    if 'data' in entry:
                        job_data = entry.get('data')
                        return job_data
                        
            # if isinstance(job_json, list) and len(job_json) > 0:
            #     first_item = job_json[0]
            #     if 'data' in first_item:
            #         if 'tinderJobProfiles' in first_item['data']:
            #             job_data = first_item['data']['tinderJobProfiles']['data']
            #             if not job_data:
            #                 logger.warn("No job data found in the extracted data.")
            #                 return None
            #             return job_data
                    
            #         elif 'tinderUserProfiles' in first_item['data']:
            #             job_data = first_item['data']['tinderUserProfiles']['data']
            #             if not job_data:
            #                 logger.warn("No job data found in the extracted data.")
            #                 return None
            #             return job_data

            logger.warn("Invalid job_json format or missing data.")
            return None

        except Exception as e:
            logger.error(f"Error extracting data: {e}")
            return None
      
        # Initialize logging
    
    def filter_by_template_id(self, template_id, cursor={}, since=None, limit=None, **kwargs):
        try:
            if not cursor:
                cursor = True

            if not template_id:
                logger.warn("Invalid or missing template_id")
                return None

            template_id_filter = f"""
                filters: {{
                    tinder_templates : {{ id: {{ eq: {template_id} }} }}
                }}
            """
            data_json, cursor = self.get_all_objects(
                filter=template_id_filter, 
                cursor=cursor, 
                **kwargs)
            
            # return data_json, cursor

            if not data_json:
                logger.warn(f"No job data found for template_id: {template_id}")
                return None
            
            data = self.get_extracted_data(data_json)
            data = self.job_extracted_data(data)
            # data = self.get_extracted_from_user_job_data(data_json)
            if not data:
                logger.warn(f"No extracted data for template_id: {template_id}")
                return None

            return data, cursor

        except Exception as e:
            logger.error(f"Error filtering jobs by template_id {template_id}: {e}")
            return None
    
    def job_extracted_data(self, data):
        """
        Extracts relevant job data from a JSON response.

        Parameters:
        ----------
        data : dict
            The JSON data containing job information.

        Returns:
        -------
        dict or None
            A dictionary of job data or None if no data is found.
        """
        try:
            # Extracted results
            simplified_jobs = []

            for job in data:
                job_id = job.get("id")
                attr = job.get("attributes", {})
                nested_attr = attr.get("attributes", {})

                job_info = {
                    "job_id": job_id,
                    "title": attr.get("title") or nested_attr.get("title"),
                    "company": nested_attr.get("company_name") or nested_attr.get("company_info", {}).get("name"),
                    "level": attr.get("level") or nested_attr.get("level"),
                    "job_link": attr.get("applyLink")
                }

                simplified_jobs.append(job_info)

            return simplified_jobs

        except Exception as e:
            logger.error(f"Error extracting job data: {e}")
            return None
    
    def get_all_jobs_info(self, **kwargs):
        """
        Fetches all jobs' information.

        Parameters:
        ----------
        kwargs : dict
            Additional arguments to filter the jobs.

        Returns:
        -------
        list or None
            A list of all jobs' information or None if an error occurs.
        """
        try:
            job_json = self.get_all_objects(**kwargs)
            if not job_json:
                logger.warn("No job data found for all jobs.")
                return None

            job_data = self.get_extracted_data(job_json)
            if not job_data:
                logger.warn("No extracted data found for all jobs.")
                return None

            return job_data

        except Exception as e:
            logger.error(f"Error fetching all jobs' info: {e}")
            return None


    def get_trainee_job_profile(self, limit, since, cursor, filter_data, job_profile_id):
        # Default page size and pagination
        page_size = cursor.get('pageSize', 400)
        page = cursor.get('page', 1)
        
        all_sessions = []
        
        # Calculate the timestamp for filtering based on 'since' days (if provided)
        since_date = None
        if since:
            dt = datetime.utcnow().replace(hour=23, minute=59, second=59, microsecond=0) - timedelta(days=since)
            since_date = dt.isoformat() + 'Z'

        # Build the filter string for logging purposes
        filter_str = f'filters: {{createdAt: {{gt: "{since_date}"}} }}' if since_date else ""

        # Fetch all the tinderJobProfiles pages
        try:
    # Step 1: Query TinderJobProfiles with pagination at the top level
            while True:
                profiles_query = f"""
                query GetTinderJobProfiles($job_profile_id: ID!, $page: Int, $pageSize: Int, $sessionLimit: Int, $sessionStart: Int) {{
                    tinderJobProfiles(
                        filters: {{
                            id: {{ eq: $job_profile_id }}
                        }},
                        pagination: {{ page: $page, pageSize: $pageSize }}
                    ) {{
                        data {{
                            id
                            attributes {{
                                i_persona_sessions {{
                                    data {{
                                        id
                                        attributes {{
                                            createdAt
                                            i_persona_observer {{
                                                data {{
                                                    id
                                                    attributes {{
                                                        createdAt
                                                    }}
                                                }}
                                            }}
                                            tinder_job_profile {{
                                                data {{
                                                    id
                                                }}
                                            }}
                                            tinder_user_profile {{
                                                data {{
                                                    id
                                                }}
                                            }}
                                        }}
                                    }}
                                    meta {{
                                        pagination {{
                                            total
                                            page
                                            pageSize
                                            pageCount
                                        }}
                                    }}
                                }}
                            }}
                        }}
                        meta {{
                            pagination {{
                                total
                                page
                                pageSize
                                pageCount
                            }}
                        }}
                    }}
                }}
                """

                # Execute the query for TinderJobProfiles
                res_json = self.sg.Select_from_table(
                    query=profiles_query,
                    variables={
                        "job_profile_id": str(job_profile_id),
                        "page": page,
                        "pageSize": page_size,
                        "sessionLimit": 10,
                        "sessionStart": 10
                    }
                )

                # Check if response is as expected
                if 'data' in res_json and 'tinderJobProfiles' in res_json['data']:
                    profiles = res_json['data']['tinderJobProfiles']['data']

                    if profiles:
                        for profile in profiles:
                            persona_sessions = profile['attributes']['i_persona_sessions']['data']

                            for session in persona_sessions:
                                created_at = session['attributes']['CreatedAt']

                                # Filter based on 'since' days (if provided)
                                if since_date and created_at < since_date:
                                    continue  # Skip sessions older than the 'since' date

                                all_sessions.append(session)

                                # Stop if the limit is reached
                                if limit and len(all_sessions) >= limit:
                                    break

                        # Break if the limit is reached
                        if limit and len(all_sessions) >= limit:
                            break

                    pagination = res_json['data']['tinderJobProfiles']['meta']['pagination']

                    # Break if the last page has been reached
                    if pagination['page'] >= pagination['pageCount']:
                        break
                    else:
                        page += 1  # Move to the next page

                else:
                    logger.error("No data received or unexpected structure in response.")
                    break

        except Exception as e:
            logger.error(f"Unexpected error: {e}")

        # Return paginated results
        try:
            return self.paginate_sessions(all_sessions, page=1, page_size=page_size, since_date=since_date, filter_str=filter_str)
        except Exception as e:
            logger.error(f"Error during pagination: {e}")
            return {"error": "Pagination failed. Please check logs for more details."}

    def paginate_sessions(self, all_sessions, page=1, page_size=14, since_date=None, filter_str=None):
        """ Paginate through i_persona_sessions manually """
        try:
            start = (page - 1) * page_size
            end = start + page_size
            paginated_sessions = all_sessions[start:end]

            # Add filter and query information
            cursor_info = {
                "filter": filter_str,
                "page": page,
                "pageSize": page_size,
                "page_count": (len(all_sessions) + page_size - 1) // page_size,
                "query": f"""query getIPersonaSessions($offsetStart: Int!, $pageSize: Int!) {{
                    iPersonaSessions( pagination: {{ start: {start}, limit: {page_size} }} , sort: "createdAt:desc" {filter_str} ) {{
                        meta {{
                            pagination {{
                                page
                                pageSize
                                total
                                pageCount
                            }}
                        }}
                        data {{
                            id
                            attributes {{                         
                                createdAt                            
                            }}
                        }}
                    }}
                }}""",
                "total": len(all_sessions)
            }
            return paginated_sessions, cursor_info
            return {
                "data": paginated_sessions,
                "cursor": cursor_info
            }

        except Exception as e:
            logger.error(f"Error during pagination: {e}")
            return {"error": "Pagination failed. Please check logs for more details."}

class IpersonaTraineeSessionSchema(LeapBaseClass):
    '''
    Schema Name:
        TinderJobProfiles
    Attributes:
        id: ID,
        attributes: Json
    '''
    def __init__(self, run_stage='', **kwargs) -> None:
        self.kwargs = copy.deepcopy(kwargs)
        super().__init__(run_stage=run_stage, **kwargs)
        
        self.table_single = kwargs.get('table_single', "")
        self.table = kwargs.get('table', "")
        self.data = kwargs.get('data', "")
        self.start = kwargs.get('start', 0)
        self.limit = kwargs.get('limit', 10)
        self.since_days = kwargs.get('since', 10)
        self.sort_order = kwargs.get('sort_order', 'desc')  
      
        if not self.table_single:
            self.table_single = "tinderUserProfile"
        
        if not self.table:
            self.table = "tinderUserProfiles"
        
        if not self.data:
            logger.info(f"Using default data schema for {self.table_single} ...")
            
            # Construct the date filter if since_days is provided
            date_filter = ""
            if self.since_days:
                # Add a date filter for sessions created within the specified number of days
                date_filter = f'filters: {{createdAt: {{gte: "{self._get_date_since(self.since_days)}" }}}}'
            
            # Add sorting option (default to descending by createdAt)
            sort_clause = f'sort: "createdAt:{self.sort_order}"'
            
            # Combine parameters with proper commas
            params = [f'pagination: {{start: {self.start}, limit: {self.limit}}}']
            if date_filter:
                params.append(date_filter)
            params.append(sort_clause)
            
            # Join parameters with commas
            all_params = ", ".join(params)
            
            self.data = f'''
                data {{
                    id
                    attributes {{
                        # attributes
                        i_persona_sessions({all_params}) {{
                            data {{
                                id
                                attributes {{
                                    status
                                    attributes
                                    createdAt
                                    i_persona_observer {{
                                        data {{
                                            id
                                            attributes {{
                                                attributes
                                                metadata
                                            }}
                                        }}
                                    }}
                                    tinder_job_profile {{
                                        data {{
                                            id
                                        }}
                                    }}
                                    tinder_user_profile {{
                                        data {{
                                            id
                                        }}
                                    }}
                                }}
                            }}
                        }}
                     %s
                    }}
                }}
            '''
        else:
            logger.info(f"Using passed data schema for {self.table_single} ...")
            
        self.type_map = {
            "id": "ID",
            "attributes": "JSON"
        }
        
        self.id_names_map = { }
        
        self.data_template = copy.deepcopy(self.data)
        self.data = self.data%""
        _ = self.process_extra_data(kwargs.get('extra_data', []), inplace=True)
    
    def _get_date_since(self, days):
        """
        Calculate the date 'days' ago from the current date.
        Returns ISO format string to use in GraphQL query.
        """
        try:            
            date_since = datetime.now() - timedelta(days=int(days))
            return date_since.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        except Exception as e:
            logger.error(f"Error calculating date filter: {str(e)}", exc_info=True)
            return (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            
    def get_user_by_id(self, idval, **kwargs):
        return self.exists(scol='id', sval=idval, op='eq', stype="ID", **kwargs)        
    
    def filter_by_user_id(self, user_profile_id, start=0, limit=20, **kwargs):
        try:
            self.start = start if start is not None else self.start
            self.limit = limit if limit is not None else self.limit
     
            if not user_profile_id:
                logger.warn("Invalid or missing job_profile_id")
                return None

            job_filter = f"""
                filters: {{
                    id : {{ eq: {user_profile_id} }} 
                }}
            """
            data_json = self.get_all_objects(filter=job_filter, **kwargs)
            if not data_json:
                logger.warn(f"No job data found for job_profile_id: {user_profile_id}")
                return None
            
            data = self.get_extracted_data(data_json)
            if not data:
                logger.warn(f"No extracted data for job_profile_id: {user_profile_id}")
                return None
            cursor = {
                    "filter": f'{{createdAt: {{gte: "{self._get_date_since(self.since_days)}" }}}}', 
                    "limit": limit,
                    "start": start,
                    "query": {},
                    "total": len(data)
                }
            return data, cursor

        except Exception as e:
            logger.error(f"Error filtering jobs by job_profile_id {user_profile_id}: {e}")
            return cursor
        
    def get_extracted_data(self, data_json):
        """
        Extracts relevant job or job data from a JSON response.

        Parameters:
        ----------
        job_json : dict
            The JSON data containing job or job information.

        Returns:
        -------
        list or None
            A list of extracted job or job data or None if no data is found.
        """
        try:
            if isinstance(data_json, list) and len(data_json) > 0:
                for entry in data_json:
                    if 'data' in entry:
                        list_data = entry.get('data')
                        return list_data
                        
            logger.warn("Invalid job_json format or missing data.")
            return None

        except Exception as e:
            logger.error(f"Error extracting data: {e}")
            return None

class IpersonaJobSessionSchema(LeapBaseClass):
    '''
    Schema Name:
        TinderJobProfiles
    Attributes:
        id: ID,
        attributes: Json
    '''
    def __init__(self, run_stage='', **kwargs) -> None:
        self.kwargs = copy.deepcopy(kwargs)
        super().__init__(run_stage=run_stage, **kwargs)
        
        self.table_single = kwargs.get('table_single', "")
        self.table = kwargs.get('table', "")
        self.data = kwargs.get('data', "")
        self.start = kwargs.get('start', 0)
        self.limit = kwargs.get('limit', 10)
        self.since_days = kwargs.get('since', 10)
        self.sort_order = kwargs.get('sort_order', 'desc')  
      
        if not self.table_single:
            self.table_single = "tinderJobProfile"
        
        if not self.table:
            self.table = "tinderJobProfiles"
        
        if not self.data:
            logger.info(f"Using default data schema for {self.table_single} ...")
            
            # Construct the date filter if since_days is provided
            date_filter = ""
            if self.since_days:
                # Add a date filter for sessions created within the specified number of days
                date_filter = f'filters: {{createdAt: {{gte: "{self._get_date_since(self.since_days)}" }}}}'
            
            # Add sorting option (default to descending by createdAt)
            sort_clause = f'sort: "createdAt:{self.sort_order}"'
            
            # Combine parameters with proper commas
            params = [f'pagination: {{start: {self.start}, limit: {self.limit}}}']
            if date_filter:
                params.append(date_filter)
            params.append(sort_clause)
            
            # Join parameters with commas
            all_params = ", ".join(params)
            
            self.data = f'''
                data {{
                    id
                    attributes {{
                        attributes
                        i_persona_sessions({all_params}) {{
                            data {{
                                id
                                attributes {{
                                    status
                                    attributes
                                    createdAt
                                    i_persona_observer {{
                                        data {{
                                            id
                                            attributes {{
                                                attributes
                                                metadata
                                            }}
                                        }}
                                    }}
                                    tinder_job_profile {{
                                        data {{
                                            id
                                        }}
                                    }}
                                    tinder_user_profile {{
                                        data {{
                                            id
                                        }}
                                    }}
                                }}
                            }}
                        }}
                     %s
                    }}
                }}
            '''
        else:
            logger.info(f"Using passed data schema for {self.table_single} ...")
            
        self.type_map = {
            "id": "ID",
            "attributes": "JSON"
        }
        
        self.id_names_map = { }
        
        self.data_template = copy.deepcopy(self.data)
        self.data = self.data%""
        _ = self.process_extra_data(kwargs.get('extra_data', []), inplace=True)
    
    def _get_date_since(self, days):
        """
        Calculate the date 'days' ago from the current date.
        Returns ISO format string to use in GraphQL query.
        """
        try:            
            date_since = datetime.now() - timedelta(days=int(days))
            return date_since.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        except Exception as e:
            logger.error(f"Error calculating date filter: {str(e)}", exc_info=True)
            return (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            
    def get_job_by_id(self, idval, **kwargs):
        return self.exists(scol='id', sval=idval, op='eq', stype="ID", **kwargs)        
    
    def filter_by_job_id(self, job_profile_id, start=0, limit=20, **kwargs):
        try:
            self.start = start if start is not None else self.start
            self.limit = limit if limit is not None else self.limit
     
            if not job_profile_id:
                logger.warn("Invalid or missing job_profile_id")
                return None

            job_filter = f"""
                filters: {{
                    id : {{ eq: {job_profile_id} }} 
                }}
            """
            data_json = self.get_all_objects(filter=job_filter, **kwargs)
            if not data_json:
                logger.warn(f"No job data found for job_profile_id: {job_profile_id}")
                return None
            
            data = self.get_extracted_data(data_json)
            if not data:
                logger.warn(f"No extracted data for job_profile_id: {job_profile_id}")
                return None
            cursor = {
                    "filter": f'{{createdAt: {{gte: "{self._get_date_since(self.since_days)}" }}}}', 
                    "limit": limit,
                    "start": start,
                    "query": {},
                    "total": len(data)
                }
            return data, cursor

        except Exception as e:
            logger.error(f"Error filtering jobs by job_profile_id {job_profile_id}: {e}")
            return cursor
        
    def get_extracted_data(self, job_json):
        """
        Extracts relevant job or job data from a JSON response.

        Parameters:
        ----------
        job_json : dict
            The JSON data containing job or job information.

        Returns:
        -------
        list or None
            A list of extracted job or job data or None if no data is found.
        """
        try:
            if isinstance(job_json, list) and len(job_json) > 0:
                for entry in job_json:
                    if 'data' in entry:
                        job_data = entry.get('data')
                        return job_data
                        
            logger.warn("Invalid job_json format or missing data.")
            return None

        except Exception as e:
            logger.error(f"Error extracting data: {e}")
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
    def __init__(self, run_stage='', **kwargs) -> None:
        self.kwargs = copy.deepcopy(kwargs)
        super().__init__(run_stage=run_stage, **kwargs)   
        
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
    
    def filter_by_tinder_user_profile_id(self, user_profile_id, since=0, limit=0, **kwargs):
        try:
            session_overall_observer_filter = f"""
                filters: {{
                    tinder_user_profile : {{ id: {{ eq: {user_profile_id} }} }}
                }}
            """
            data_json = self.get_all_objects(filter=session_overall_observer_filter, **kwargs)

            if not data_json:
                logger.warn(f"No data returned for user profile ID: {user_profile_id}")
                return None

            data = self.get_extracted_from_user_data(data_json)
            
            if not data:
                logger.warn(f"No extracted data found for user profile ID: {user_profile_id}")
                return None
            
            return data

        except Exception as e:
            logger.error(f"Error filtering by tinder user profile ID {user_profile_id}: {str(e)}")
            return {'error': f"Error processing request: {str(e)}"}

    
    def filter_by_with_user_and_job_id(self, user_profile_id, job_profile_id, **kwargs):
        try:
            session_overall_observer_filter = f"""
                filters: {{
                    tinder_user_profile : {{ id: {{ eq: {user_profile_id} }} }},
                    tinder_job_profile : {{ id: {{ eq: {job_profile_id} }} }}
                }}
            """
            data_json = self.get_all_objects(filter=session_overall_observer_filter, **kwargs)
            
            if not data_json:
                logger.warn(f"No data returned for user profile ID: {user_profile_id} and job profile ID: {job_profile_id}")
                return None

            data = self.get_extracted_from_user_job_data(data_json)
            
            if not data:
                logger.warn(f"No extracted data found for user profile ID: {user_profile_id} and job profile ID: {job_profile_id}")
                return None
            
            return data

        except Exception as e:
            logger.error(f"Error filtering by user profile ID {user_profile_id} and job profile ID {job_profile_id}: {str(e)}")
            return {'error': f"Error processing request: {str(e)}"}

    def save_Session_Overall_Observer(self, params, **kwargs):
        try:
            session_json = self.save_or_update_object(params, **kwargs)

            session = self.get_extracted_from_user_job_data(session_json)
            if not session:
                logger.warn(f"No session data extracted for params: {params}")
                return {"error": "No session data found."}

            logger.info(f"Session data saved and extracted successfully for params: {params}")
            return session

        except KeyError as e:
            logger.error(f"Key error during save or update: {str(e)}")
            return {"error": f"Key error: {str(e)}"}

        except TypeError as e:
            logger.error(f"Type error in session data extraction: {str(e)}")
            return {"error": f"Type error: {str(e)}"}

        except Exception as e:
            logger.error(f"Unexpected error during save_Session_Overall_Observer: {str(e)}")
            return {"error": f"An unexpected error occurred: {str(e)}"}

    
    def update_session(self, params, **kwargs):
        try:
            if self.id_name() not in params:
                logger.error("ID is missing for update operation.")
                return {'error': 'ID is required for updating the session.'}

            result = self.save_or_update_object(params, **kwargs)

            if not result:
                logger.warn(f"Failed to update session with params: {params}")
                return {'error': 'Failed to update session.'}

            return result

        except Exception as e:
            logger.error(f"Error updating session: {str(e)}")
            return {'error': f"Error updating session: {str(e)}"}


    def get_extracted_data(self, session_json):
        try:
            if isinstance(session_json, list) and len(session_json) > 0:  
                # first_item = session_json[0]

                # if 'data' in first_item and 'createIPersonaSessionOverallObserver' in first_item['data']:
                #     session = first_item['data']['createIPersonaSessionOverallObserver']['data']
                
                if isinstance(session_json, list) and len(session_json) > 0:
                    for entry in session_json:
                        if 'data' in entry:
                            session = entry.get('data')
                        
                    if not session:
                        logger.warn("No session data found in the extracted data.")
                        return None

                    return session
                else:
                    logger.warn("No valid data structure found in session JSON.")
                    return None

            logger.warn("Session JSON is empty or not in expected format.")
            return None

        except Exception as e:
            logger.error(f"Error extracting data from session JSON: {str(e)}")
            return {'error': f"Error extracting data from session JSON: {str(e)}"}

    
    def get_extracted_from_user_job_data(self, session_json):
        try:
            all_sessions = []

            if not isinstance(session_json, list):
                logger.error(f"Expected session_json to be a list, but got {type(session_json).__name__}")
                return {"error": "Invalid data format: expected a list."}

            if len(session_json) == 0:
                logger.warn("session_json list is empty")
                return {"error": "No session data provided."}

            # first_item = session_json[0]
            # if 'data' not in first_item:
            #     logger.error("First item in session_json is missing the 'data' key")
            #     return {"error": "Invalid session data: missing 'data' key."}

            # if 'iPersonaSessionOverallObservers' not in first_item['data']:
            #     logger.error("First item 'data' does not contain 'iPersonaSessionOverallObservers'")
            #     return {"error": "Invalid session data: missing 'iPersonaSessionOverallObservers' key."}

            # observer_data = first_item['data']['iPersonaSessionOverallObservers'].get('data', [])
            if isinstance(session_json, list) and len(session_json) > 0:
                for entry in session_json:
                    if 'data' in entry:
                        observer_data = entry.get('data')
                        
            if len(observer_data) == 0:
                logger.warn("Trainee does not have session overall observer data")
                return {"error": "No observer data found."}

            for session in observer_data:
                attributes = session.get('attributes', {}).get('attributes', {})
                session_id = session.get('id', '')
                all_sessions.append(attributes)

            if len(all_sessions) == 0:
                logger.warn("No valid session attributes were extracted")
                return {"error": "No valid session attributes found."}

            result = {
                "id": session_id,  
                "all_sessions": all_sessions
            }
            logger.info(f"Successfully extracted {len(all_sessions)} overall observer sessions for user job data")
            return result

        except (KeyError, TypeError, AttributeError) as e:
            logger.error(f"Error extracting user job data: {str(e)}")
            return {"error": f"Data extraction error: {str(e)}"}

        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return {"error": f"An unexpected error occurred: {str(e)}"}

        
    def get_extracted_from_user_data(self, data_json):
        try:
            all_datas = []

            # if isinstance(data_json, list) and len(data_json) > 0:  
            #     first_item = data_json[0]

            #     if 'data' in first_item and 'iPersonaSessionOverallObservers' in first_item['data']:
            #         data = first_item['data']['iPersonaSessionOverallObservers']['data']
                    
            if isinstance(data_json, list) and len(data_json) > 0:
                for entry in data_json:
                    if 'data' in entry:
                        data = entry.get('data')                           
                            # return trainee
                    if data:
                        for session_item in data:
                            data_attributes = session_item.get('attributes', {}).get('attributes', {})
                            if data_attributes:
                                all_datas.append(data_attributes)
                            else:
                                logger.warn("No attributes found for data item.")
                        return all_datas
                    else:
                        logger.warn("No data data found in 'iPersonaSessionOverallObservers'.")
                        return None
                else:
                    logger.warn("Missing expected data or 'iPersonaSessionOverallObservers' field in data JSON.")
                    return None
            else:
                logger.warn("Session JSON is empty or not in the expected list format.")
                return None

        except Exception as e:
            logger.error(f"Error extracting data from data JSON: {str(e)}")
            return {'error': f"Error extracting data from data JSON: {str(e)}"}
    
class IpersonaSessionTinderUserJobMatchSchema(LeapBaseClass):
    '''
    Schema Name:
        TinderUserJobMatches
    Attributes:
        match_score: Int
        match_level: String
    '''
    def __init__(self, run_stage='', **kwargs) -> None:
        self.kwargs = copy.deepcopy(kwargs)
        super().__init__(run_stage=run_stage, **kwargs)   
        
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
        try:
            if not user_profile_id or not job_profile_id:
                logger.error("User profile ID or Job profile ID is missing!")
                return []

            session_filter = f"""
                filters: {{
                    tinder_user_profile : {{ id: {{ eq: {user_profile_id} }} }},
                    tinder_job_profile : {{ id: {{ eq: {job_profile_id} }} }}
                }}
            """

            data_json = self.get_all_objects(filter=session_filter, **kwargs)

            data = self.get_extracted_from_user_job_data(data_json)

            if not data:
                logger.warn(f"No data found for user profile ID {user_profile_id} and job profile ID {job_profile_id}.")
                return []

            return data

        except Exception as e:
            logger.error(f"Error filtering by user and job ID: {str(e)}")
            return {'error': f"Error filtering by user and job ID: {str(e)}"}

    def get_extracted_from_user_job_data(self, data_json):
        try:
            all_datas = []

            # if isinstance(data_json, list) and len(data_json) > 0:  
            #     first_item = data_json[0]

            #     if 'data' in first_item and 'tinderUserJobMatches' in first_item['data']:
            #         data = first_item['data']['tinderUserJobMatches']['data']
            if isinstance(data_json, list) and len(data_json) > 0:
                for entry in data_json:
                    if 'data' in entry:
                        data = entry.get('data')                      
                        
                if data:
                    all_datas = data
                else:
                    logger.warn("No data data found in 'tinderUserJobMatches'.")
                    return None
            # else:
            #     logger.warn("Missing expected data or 'tinderUserJobMatches' field in data JSON.")
            #     return None
            else:
                logger.warn("Session JSON is empty or not in the expected list format.")
                return None

            return all_datas

        except Exception as e:
            logger.error(f"Error extracting data from user job data: {str(e)}")
            return {'error': f"Error extracting data from user job data: {str(e)}"}

class IpersonaSessionTinderUserReactionSchema(LeapBaseClass):
    '''
    Schema Name:
        TinderUserReactions
    Attributes:
        tinder_job_profile: ID,
        tinder_user_profile: ID
    '''
    def __init__(self, run_stage='', **kwargs) -> None:
        self.kwargs = copy.deepcopy(kwargs)
        super().__init__(run_stage=run_stage, **kwargs)   
        
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
        try:
            if not user_profile_id or not job_profile_id:
                logger.error("User profile ID or Job profile ID is missing!")
                return None

            session_filter = f"""
                filters: {{
                    tinder_user_profile : {{ id: {{ eq: {user_profile_id} }} }},
                    tinder_job_profile : {{ id: {{ eq: {job_profile_id} }} }}
                }}
            """

            data_json = self.get_all_objects(filter=session_filter, **kwargs)
            
            data = self.get_extracted_from_user_job_data(data_json)

            if data is None:
                logger.warn(f"No reaction data found for user profile ID {user_profile_id} and job profile ID {job_profile_id}.")
                return None

            return data

        except Exception as e:
            logger.error(f"Error filtering by user and job ID: {str(e)}")
            return {'error': f"Error filtering by user and job ID: {str(e)}"}
    
    def get_extracted_from_user_job_data(self, session_json):
        try:
            reaction_id = None

            # if isinstance(session_json, list) and len(session_json) > 0:  
            #     first_item = session_json[0]

            #     if 'data' in first_item and 'tinderUserReactions' in first_item['data']:
            #         user_reactions = first_item['data']['tinderUserReactions']['data']
            if isinstance(session_json, list) and len(session_json) > 0:
                for entry in session_json:
                    if 'data' in entry:
                        user_reactions = entry.get('data')
                        
                    if len(user_reactions) != 0:
                        reaction_id = user_reactions[0]['id']  
                        return reaction_id
                    else:
                        logger.warn("No user reactions found in 'data'.")
                        return None
            else:
                logger.warn("Session JSON is empty or not in the expected list format.")
                return None


        except Exception as e:
            logger.error(f"Error extracting reaction data from user job data: {str(e)}")
            return {'error': f"Error extracting reaction data from user job data: {str(e)}"}
   
class IpersonaSessionMessageSchema(LeapBaseClass):
    '''
    Schema Name:
        IPersonaMessages
    Attributes:
        i_persona_session: Relation with IPersonaMessages
        attributes: Json	
    '''
    def __init__(self, run_stage='', **kwargs) -> None:
        self.kwargs = copy.deepcopy(kwargs)
        super().__init__(run_stage=run_stage, **kwargs)   

        
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
                        metadata
                        %s
                    }
                }
            '''
        else:
            logger.info(f"Using passed data schema for {self.table_single} ...")
     
            
        self.type_map = {   
            "attributes": "JSON",
            "i_persona_session": "ID",
            "metadata": "JSON"
        }

        self.id_names_map = {  }
         
        self.data_template = copy.deepcopy(self.data)
        self.data = self.data%""
        _ = self.process_extra_data(kwargs.get('extra_data', []), inplace=True)
    
    def get_session_msg_by_id(self, sessionId, **kwargs):
        return self.exists(scol='id', sval=sessionId, op='eq', stype="ID", **kwargs)        
    
    def filter_by_session_id(self, sessionId, **kwargs):
        try:
            if not sessionId:
                logger.error("Session ID is missing!")
                return None

            session_filter = f"""
                filters: {{
                    i_persona_session : {{ id: {{ eq: {sessionId} }} }}
                }}
            """
            
            data_json = self.get_all_objects(filter=session_filter, **kwargs)
            
            data = self.get_session_msg_data(data_json)

            if data is None:
                logger.warn(f"No session message data found for session ID {sessionId}.")
                return None

            return data

        except Exception as e:
            logger.error(f"Error filtering by session ID: {str(e)}")
            return {'error': f"Error filtering by session ID: {str(e)}"}

    
    def get_all_session_msg(self, **kwargs):
        try:
            session_json = self.get_all_objects(**kwargs)
            
            session = self.get_msg_data(session_json)

            if session is None:
                logger.warn("No session message data found.")
                return None
            
            return session

        except Exception as e:
            logger.error(f"Error fetching all session messages: {str(e)}")
            return {'error': f"Error fetching all session messages: {str(e)}"}
   
        
    def save_message(self, params, **kwargs):
        try:
            if not params:
                logger.error("Params are missing for saving message!")
                return None
            
            session_json = self.save_or_update_object(params, **kwargs)

            session = self.get_extracted_data(session_json)

            if session is None:
                logger.warn("No data extracted from saved session.")
                return None

            return session

        except Exception as e:
            logger.error(f"Error saving message: {str(e)}")
            return {'error': f"Error saving message: {str(e)}"}

    
    def get_extracted_data(self, session_json):
        try:
            if isinstance(session_json, list) and len(session_json) > 0:  
                first_item = session_json[0]
                if 'data' in first_item and 'createIPersonaMessage' in first_item['data']:
                    session = first_item['data']['createIPersonaMessage']['data']
                    return session

            logger.warn("No valid extracted data found.")
            return None

        except Exception as e:
            logger.error(f"Error extracting data from session JSON: {str(e)}")
            return {'error': f"Error extracting data from session JSON: {str(e)}"}
    
    
    def get_msg_data(self, session_json):
        try:
            all_sessions_msg = []

            if isinstance(session_json, list) and len(session_json) > 0:  
                first_item = session_json[0]
                if 'data' in first_item and 'iPersonaMessages' in first_item['data']:
                    session_msg = first_item['data']['iPersonaMessages']['data']
                    all_sessions_msg = session_msg

                    return all_sessions_msg

            logger.warn("No message data found in session JSON.")
            return None

        except Exception as e:
            logger.error(f"Error extracting message data: {str(e)}")
            return {'error': f"Error extracting message data: {str(e)}"}

    def get_session_msg_data(self, session_json):
        try:
            all_sessions_msg = []

            # if isinstance(session_json, list) and len(session_json) > 0:  
            #     first_item = session_json[0]
            #     if 'data' in first_item and 'iPersonaMessages' in first_item['data']:
            #         session_msg = first_item['data']['iPersonaMessages']['data']
            #         all_sessions_msg = session_msg
                    
            if isinstance(session_json, list) and len( session_json) > 0:
                for entry in session_json:
                    if 'data' in entry:
                        all_sessions_msg = entry.get('data')                         

                extracted_messages = []
                for message in all_sessions_msg:
                    message_attributes = message.get('attributes', {}).get('attributes', {})
                    if message_attributes:
                        message_data = message_attributes.get('message', {})
                        extracted_messages.append({
                            "content": message_data.get('content', ""),
                            "user_type": message_data.get('user_type', ""),
                            "template_id": message_data.get('template_id', ""),
                            "content_type": message_data.get('content_type', "")
                        })

                result = {
                    "count": len(extracted_messages),
                    "total": extracted_messages
                }
                return result

            logger.warn("No session message data found in session JSON.")
            return None

        except Exception as e:
            logger.error(f"Error extracting session message data: {str(e)}")
            return {'error': f"Error extracting session message data: {str(e)}"}

class IpersonaSessionObserverSchema(LeapBaseClass):
    '''
    Schema Name:
        IPersonaObservers
    Attributes:
        i_persona_session: Relation with IPersonaObservers
        attributes: Json	
    '''
    def __init__(self, run_stage='', **kwargs) -> None:
        self.kwargs = copy.deepcopy(kwargs)
        super().__init__(run_stage=run_stage, **kwargs)   

        
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
        try:
            if not sessionId:
                logger.error("Session ID is missing for observer session filter!")
                return None

            session_filter = f"""
                filters: {{
                    i_persona_session : {{ id: {{ eq: {sessionId} }} }}
                }}
            """
            
            data_json = self.get_all_objects(filter=session_filter, **kwargs)
            
            data = self.get_session_observer_data(data_json)

            if data is None:
                logger.warn(f"No observer session data found for session ID {sessionId}.")
                return None

            return data

        except Exception as e:
            logger.error(f"Error filtering by observer session ID: {str(e)}")
            return {'error': f"Error filtering by observer session ID: {str(e)}"}

    def get_all_session_observer(self, **kwargs):
        try:
            session_json = self.get_all_objects(**kwargs)
            
            session = self.get_session_observer_data(session_json)

            if session is None:
                logger.warn("No observer session data found.")
                return None
            
            return session

        except Exception as e:
            logger.error(f"Error fetching all session observers: {str(e)}")
            return {'error': f"Error fetching all session observers: {str(e)}"}   
        
    def save_observer(self, params, **kwargs):
        try:
            if not params:
                logger.error("Params are missing for saving observer!")
                return None
            
            session_json = self.save_or_update_object(params, **kwargs)

            session = self.get_extracted_data(session_json)

            if session is None:
                logger.warn("No data extracted from saved observer session.")
                return None

            return session

        except Exception as e:
            logger.error(f"Error saving observer session: {str(e)}")
            return {'error': f"Error saving observer session: {str(e)}"}

    
    def get_extracted_data(self, session_json):
        try:
            if isinstance(session_json, list) and len(session_json) > 0:
                for entry in session_json:
                    if 'data' in entry:
                        session = entry.get('data')
                        return session
                        
            # if isinstance(session_json, list) and len(session_json) > 0:  
            #     first_item = session_json[0]
            #     if 'data' in first_item and 'createIPersonaObserver' in first_item['data']:
            #         session = first_item['data']['createIPersonaObserver']['data']
            #         return session

            logger.warn("No valid extracted data found for observer session.")
            return None

        except Exception as e:
            logger.error(f"Error extracting data from session JSON: {str(e)}")
            return {'error': f"Error extracting data from session JSON: {str(e)}"}
    
    def get_session_observer_data(self, session_json):
        try:
            all_sessions_msg = []
            if isinstance(session_json, list) and len(session_json) > 0:
                for entry in session_json:
                    if 'data' in entry:
                        for session in entry.get('data'):                            
                            return session
                        
            # if isinstance(session_json, list) and len(session_json) > 0:  
            #     first_item = session_json[0]
            #     if 'data' in first_item and 'iPersonaObservers' in first_item['data']:
            #         session_msg = first_item['data']['iPersonaObservers']['data']
            #         all_sessions_msg = session_msg

            #         return all_sessions_msg

            logger.warn("No session observer data found in session JSON.")
            return None

        except Exception as e:
            logger.error(f"Error extracting observer session data: {str(e)}")
            return {'error': f"Error extracting observer session data: {str(e)}"}
                
class IpersonaAllUserSchema(LeapBaseClass):
    '''
    Schema Name:
        AllUsers
    Attributes:
        name: text
        role: text
        Batch: text	
    '''
    def __init__(self, run_stage='', **kwargs) -> None:
        self.kwargs = copy.deepcopy(kwargs)
        super().__init__(run_stage=run_stage, **kwargs)   
        
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
                        email
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
            "email": "String",
            "role": "String",
            "Batch": "String"
        }

        self.id_names_map = {  }
         
        self.data_template = copy.deepcopy(self.data)
        self.data = self.data%""
        _ = self.process_extra_data(kwargs.get('extra_data', []), inplace=True)
    
    def get_alluser_by_id(self, all_user_id, **kwargs):
        try:
            if not all_user_id:
                logger.error("All User ID is missing for fetching user data!")
                return None
            
            data_json = self.exists(scol='id', sval=all_user_id, op='eq', stype="ID", **kwargs)
            
            data = self.get_extracted_trainee_data(data_json)

            if data is None:
                logger.warn(f"No data found for All User ID {all_user_id}.")
                return None

            result = {
                "name": data['attributes']['name'],
                "email": data['attributes']['email'],
                "role": data['attributes']['role'],
                "Batch": data['attributes']['Batch']
            }

            return result

        except Exception as e:
            logger.error(f"Error fetching user data for All User ID {all_user_id}: {str(e)}")
            return {'error': f"Error fetching user data for All User ID {all_user_id}: {str(e)}"}

    
    def get_extracted_trainee_data(self, data_json):
        try:
            # if isinstance(data_json, dict) and len(data_json) > 0:
            #     for entry in data_json:
            #         if 'data' in entry:
            #             data_json = entry.get('data')
            #             return data_json
            if isinstance(data_json, dict) and 'data' in data_json:
                # Return the entire 'data' object
                return data_json['data']
            # if isinstance(data_json, dict) and len(data_json) > 0:  
            #     first_item = data_json
            #     if 'data' in first_item and 'allUser' in first_item['data']:
            #         data_json = first_item['data']['allUser']['data']
            #         return data_json

            logger.warn("No valid extracted trainee data found.")
            return None

        except Exception as e:
            logger.error(f"Error extracting trainee data: {str(e)}")
            return {'error': f"Error extracting trainee data: {str(e)}"}
    
class IpersonaProfileInformationSchema(LeapBaseClass):
    '''
    Schema Name:
        ProfileInformations
    Attributes:
        all_users: Relation with AllUsers
        gender: text
        nationality: text
    '''
    def __init__(self, run_stage='', **kwargs) -> None:
        self.kwargs = copy.deepcopy(kwargs)
        super().__init__(run_stage=run_stage, **kwargs)   
        
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
        try:
            if not all_user_id:
                logger.error("All User ID is missing for fetching user profile data!")
                return None
           
            session_filter = f"""
                filters: {{
                    all_user : {{ id: {{ eq: {all_user_id} }} }}
                }}
            """
            
            data_json = self.get_all_objects(filter=session_filter, **kwargs)
            data = self.get_extracted_data(data_json)

            if data is None:
                logger.warn(f"No profile data found for All User ID {all_user_id}.")
                return None

            result = {
                "gender": data['attributes']['gender'],
                "nationality": data['attributes']['nationality']
            }
            return result

        except Exception as e:
            logger.error(f"Error fetching profile data for All User ID {all_user_id}: {str(e)}")
            return {'error': f"Error fetching profile data for All User ID {all_user_id}: {str(e)}"}

    
    def get_extracted_data(self, data_json):
        try:
            if isinstance(data_json, list) and len(data_json) > 0:
                for entry in data_json:
                    if 'data' in entry:
                        data_entries = entry.get('data')
                        if isinstance(data_entries, list) and len(data_entries) > 0:
                            return data_entries[0]
            
            # if isinstance(data_json, list) and 'data' in data_json:
            #     # Return the entire 'data' object
            #     return data_json['data']
            
            # if isinstance(data_json, list) and len(data_json) > 0:  
            #     first_item = data_json[0]
            #     if 'data' in first_item and 'profileInformations' in first_item['data']:
            #         data_json = first_item['data']['profileInformations']['data'][0]
            #         return data_json

            logger.warn("No valid profile information found in the extracted data.")
            return None

        except Exception as e:
            logger.error(f"Error extracting profile data: {str(e)}")
            return {'error': f"Error extracting profile data: {str(e)}"}  



class IpersonaTinderTemplateSchema(LeapBaseClass):
    '''
    Schema Name:
        TinderTemplate
    Attributes:
        name: Relation with name
        type: Relation with type
        metadata: Json   
        attributes: Json
        config: Json		
        tinder_job_profile: Relation with TinderJobProfile
    '''
    def __init__(self, run_stage='', **kwargs) -> None:
        self.kwargs = copy.deepcopy(kwargs)
        super().__init__(run_stage=run_stage, **kwargs)   

        self.table_single = kwargs.get('table_single', "")
        self.table = kwargs.get('table', "")
        self.data = kwargs.get('data', "")
        
        # Default table names
        if not self.table_single:
            self.table_single = "tinderTemplate"
            
        if not self.table:
            self.table = "tinderTemplates"
        
        # Default query schema if not provided
        if not self.data:
            logger.info(f"Using default data schema for {self.table_single} ...")
            self.data = '''
                data {
                    id
                    attributes {
                        name
                        type
                        tag
                        description
                        tinder_job_profiles {
                            data {
                                id
                            }
                        } 
                        challenge_documents {
                            data {
                                id
                            }
                        }
                        smg_criterion_metrics {
                            data {
                                id
                            }
                        }
                        i_persona_sessions {
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
            "name": "String",
            "type": "String",
            "tag": "String",
            "description": "String",
            "attributes": "JSON",
            "metadata": "JSON",
            "config": "JSON",
            "tinder_job_profiles": "[ID!]",
            "challenge_documents": "[ID!]",
            "smg_criterion_metrics": "[ID!]",
            "i_persona_sessions": "[ID!]"
        }

        self.id_names_map = {}

        self.default_data_template = copy.deepcopy(self.data)  # Preserve default schema
        self.data = self.data % ""
        _ = self.process_extra_data(kwargs.get('extra_data', []), inplace=True)
    
    def save_session(self, params, **kwargs):
        try:
            session_json = self.save_or_update_object(params, **kwargs)
            session = self.get_extracted_data(session_json)

            if session is None:
                logger.warn("Failed to save session, no data extracted.")
                return None
            
            return session

        except Exception as e:
            logger.error(f"Error saving session: {str(e)}")
            return {'error': f"Error saving session: {str(e)}"}

    def get_tinder_template_id(self, templateId, **kwargs):
        # Temporarily override self.data to customize the query for this function
        original_data = self.data  # Backup the existing self.data

        try:
            # Customize the query for this specific function
            self.data = '''
                data {
                    id
                    attributes {
                        name
                        type
                        tag
                        description
                        attributes
                        smg_criterion_metrics(pagination:{start:0, limit:-1}) {
                            data {
                                id
                                attributes {
                                    title
                                    tag
                                    content
                                }
                            }
                        } 
                        %s
                    }
                }
            '''
            data_json = self.exists(scol='id', sval=templateId, op='eq', stype="ID", **kwargs)  
            data = self.get_session_data(data_json)
            data = self.flatten_prompt_data(data)
   
            return data

        finally:
            # Restore the original self.data after the query
            self.data = original_data

    def flatten_prompt_data(self, data):
        try:
            modified_template = copy.deepcopy(data)
            metrics = modified_template["attributes"].get("smg_criterion_metrics", {}).get("data", [])

            flattened_metrics = [
                {
                    "id": metric["id"],
                    "title": metric["attributes"].get("title"),
                    "tag": metric["attributes"].get("tag"),
                    "content": metric["attributes"].get("content")
                }
                for metric in metrics
            ]
            modified_template["attributes"]["smg_criterion_metrics"]["data"] = flattened_metrics

            return modified_template

        except Exception as e:
            logger.error(f"Error flattening the cretrion prompt data: {str(e)}")
            return {'error': f"Error flattening the cretrion prompt data: {str(e)}"}

    def get_all_templates(self, cursor={}, **kwargs):
        try:
            if not cursor:
                cursor = True

            data, cursor = self.get_all_objects(cursor=cursor, **kwargs)
            template = self.get_templates_data(data)

            if template is None:
                logger.warn("No template data found.")
                return None
            
            return template, cursor

        except Exception as e:
            logger.error(f"Error fetching all templates: {str(e)}")
            return {'error': f"Error fetching all templates: {str(e)}"}
    
    def filter_by_with_job_id(self, job_profile_id, cursor={}, **kwargs):
        try:
            if not cursor:
                cursor = True

            if not job_profile_id:
                logger.error("User Profile ID or Job Profile ID is missing!")
                return None
            
            session_filter = f"""
                filters: {{
                    tinder_job_profiles : {{ id: {{ eq: {job_profile_id} }} }}
                }}
            """

            data_json, cursor = self.get_all_objects(filter=session_filter, cursor=cursor, **kwargs)
            data = self.get_sessions_data(data_json)

            if data is None:
                logger.warn(f"No session data found for Job Profile ID {job_profile_id}.")
                return None
            return data, cursor

        except Exception as e:
            logger.error(f"Error fetching session data for Job Profile ID {job_profile_id}: {str(e)}")
            return {'error': f"Error fetching session data for Job Profile ID {job_profile_id}: {str(e)}"}
    
    def filter_by_with_challenge_id(self, challenge_id, cursor={}, **kwargs):
        try:
            if not cursor:
                cursor = True

            if not challenge_id:
                logger.error("Challenge id is missing!")
                return None
            
            session_filter = f"""
                filters: {{
                    challenge_documents : {{ id: {{ eq: {challenge_id} }} }}
                }}
            """

            data_json, cursor = self.get_all_objects(filter=session_filter, cursor=cursor, **kwargs)
            data = self.get_sessions_data(data_json)

            if data is None:
                logger.warn(f"No session data found for challenge ID {challenge_id}.")
                return None
            return data, cursor

        except Exception as e:
            logger.error(f"Error fetching session data for challenge ID {challenge_id}: {str(e)}")
            return {'error': f"Error fetching session data for challenge ID {challenge_id}: {str(e)}"}

    def filter_by_with_prompt_id(self, prompt_id, cursor={}, **kwargs):
        try:
            if not cursor:
                cursor = True

            if not prompt_id:
                logger.error("Prompt id is missing!")
                return None
            
            session_filter = f"""
                filters: {{
                    smg_criterion_metrics : {{ id: {{ eq: {prompt_id} }} }}
                }}
            """

            data_json, cursor = self.get_all_objects(filter=session_filter, cursor=cursor, **kwargs)
            data = self.get_sessions_data(data_json)

            if data is None:
                logger.warn(f"No session data found for prompt ID {prompt_id}.")
                return None
            return data, cursor

        except Exception as e:
            logger.error(f"Error fetching session data for prompt ID {prompt_id}: {str(e)}")
            return {'error': f"Error fetching session data for prompt ID {prompt_id}: {str(e)}"}

    def filter_by_type(self, type, cursor={}, **kwargs):
        try:
            if not cursor:
                cursor = True

            if not type:
                logger.error("User Profile ID or Job Profile ID is missing!")
                return None
            
            session_filter = f"""
                filters: {{
                    type: {{ eq: "{type}" }}
                }}
            """

            data_json, cursor = self.get_all_objects(filter=session_filter, cursor=cursor, **kwargs)
            data = self.get_sessions_data(data_json)

            if data is None:
                logger.warn(f"No template data found for the {type}.")
                return None
            
            return data, cursor

        except Exception as e:
            logger.error(f"Error fetching templates for the type {type}: {str(e)}")
            return {'error': f"Error fetching templates for the type {type}: {str(e)}"}
    
    def filter_by_type_without_cursor(self, type, **kwargs):
        try:
            self.data = '''
                data {
                    id
                    attributes {
                        name
                        attributes
                        smg_criterion_metrics(pagination:{start:0,limit:1000}) {
                            data {
                                id
                                attributes {
                                    title
                                    tag
                                    content
                                }
                            }
                        } 
                        %s
                    }
                }
            '''
            if not type:
                logger.warn("type is missing!")
                return None
            
            session_filter = f"""
                filters: {{
                    type: {{ eq: "{type}" }}
                }}
            """

            data_json = self.get_all_objects(filter=session_filter, **kwargs)
            data = self.get_sessions_data(data_json)

            if data is None:
                logger.warn(f"No template data found for the {type}.")
                return None
            
            return data

        except Exception as e:
            logger.error(f"Error fetching templates for the type {type}: {str(e)}")
            return {'error': f"Error fetching templates for the type {type}: {str(e)}"}
    
    def get_templates_data(self, templates_json):
        try:
            all_templates = []
            if isinstance(templates_json, list) and len( templates_json) > 0:
                for entry in templates_json:
                    if 'data' in entry:
                        trainee = entry.get('data')                            
                        return trainee
            logger.warn("No challenges data found in the challenge JSON.")
            return None

        except Exception as e:
            logger.error(f"Error extracting challenge data from challenge JSON: {str(e)}")
            return {'error': f"Error extracting challenge data from challenge JSON: {str(e)}"}
    
    def get_all_sessions(self, cursor={}, **kwargs):
        try:
            if not cursor:
                cursor = True
                
            data, cursor = self.get_all_objects(cursor=cursor, **kwargs)
 
            session = self.get_sessions_data(data)

            if session is None:
                logger.warn("No session data found.")
                return None
            
            return session, cursor

        except Exception as e:
            logger.error(f"Error fetching all sessions: {str(e)}")
            return {'error': f"Error fetching all sessions: {str(e)}"}
        
    def save_if_new_user(self, scol, params, **kwargs):
        return self.save_if_new(scol, params, **kwargs)

    def get_extracted_data(self, session_json):
        try:
            if isinstance(session_json, list) and len(session_json) > 0:
                for entry in session_json:
                    if 'data' in entry:
                        session = entry.get('data')
                        return session
                        
            logger.warn("No valid data found in the session JSON.")
            return None

        except Exception as e:
            logger.error(f"Error extracting data from session JSON: {str(e)}")
            return {'error': f"Error extracting data from session JSON: {str(e)}"}  
  
    def get_sessions_data(self, session_json):
        try:
            all_sessions = []
            if isinstance(session_json, list) and len( session_json) > 0:
                for entry in session_json:
                    if 'data' in entry:
                        trainee = entry.get('data')                            
                        return trainee
            logger.warn("No sessions data found in the session JSON.")
            return None

        except Exception as e:
            logger.error(f"Error extracting session data from session JSON: {str(e)}")
            return {'error': f"Error extracting session data from session JSON: {str(e)}"}
    
    def get_session_data(self, session_json):
        try:
            all_sessions = []
            if isinstance(session_json, dict) and len(session_json) > 0:
                if 'data' in session_json:
                    return session_json['data']
                        
                logger.warn("No session data found in the session JSON.")
            return None

        except Exception as e:
            logger.error(f"Error extracting session data from session JSON: {str(e)}")
            return {'error': f"Error extracting session data from session JSON: {str(e)}"}

        
    def create_template(self, name, type, tag, description, template_questions, job_profile_ids, smgIds, challengeIds):
        mutation_query = """
            mutation CreateTinderTemplate(
            $name: String!, 
            $type: String!, 
            $tag: String!, 
            $description: String!,
            $attributes: JSON!, 
            $jobProfileIds: [ID!],
            $challengeIds: [ID!],
            $smgIds: [ID!]) {
                createTinderTemplate(data: {
                    name: $name
                    type: $type
                    tag: $tag
                    description: $description
                    attributes: $attributes
                    tinder_job_profiles: $jobProfileIds 
                    challenge_documents: $challengeIds
                    smg_criterion_metrics: $smgIds
                }) {
                    data {
                    id
                    attributes {
                        name
                        type
                        tag
                        description
                        createdAt
                        tinder_job_profiles {
                            data {
                                id
                            }
                        }
                        challenge_documents {
                            data {
                                id
                            }
                        }
                        smg_criterion_metrics {
                            data {
                                id
                            }
                        }
                        i_persona_sessions {
                            data {
                                id
                            }
                        }
                    }
                    }
                }
            }
        """

        variables = {
            "name": name,
            "type": type,
            "tag": tag or "",  
            "description": description or "",  
            "attributes": {
                "template_questions": template_questions
            },
            "jobProfileIds": job_profile_ids,
            "challengeIds": challengeIds,
            "smgIds": smgIds
        }
        
        # Execute the GraphQL mutation
        res_json = self.sg.insert_table(query=mutation_query, variables=variables)

        # Parse the response
        try:
            response = json.loads(res_json)
            template_data = response.get("data", {}).get("createTinderTemplate", {}).get("data", {})
            
            if template_data:
                # Extract details
                template_id = template_data.get("id", "N/A")
                attributes = template_data.get("attributes", {})
                name = attributes.get("name", "N/A")
                template_type = attributes.get("type", "N/A")
                created_at = attributes.get("createdAt", "N/A")
                job_profile_ids = [job_profile.get("id") for job_profile in attributes.get("tinder_job_profiles", {}).get("data", [])]
                
                return {
                    "status": "success",
                    "message": "Template created successfully.",
                    "data": {
                        "id": template_id,
                        "name": name,
                        "type": template_type,
                        "createdAt": created_at
                        # "jobProfileIds": job_profile_ids,
                        # "challengeIds": challengeIds,
                        # "smgIds": smgIds
                    }
                }
            else:
                return {
                    "status": "error",
                    "message": "Failed to create template. No data returned."
                }
        
        except json.JSONDecodeError:
            return {
                "status": "error",
                "message": "Invalid JSON response from the server."
            }

    def update_template(self, template_id, name=None, type=None, tag=None, description=None, 
                    template_questions=None, job_profile_ids=None, smgIds=None, 
                    challengeIds=None, sessionIds=None):
        """
        Updates the given template by merging new values with the existing structure.
        
        :param template_id: ID of the template to update.
        :param name, type, tag, description: Optional fields to update.
        :param template_questions: Updated template questions.
        :param job_profile_ids, smgIds, challengeIds, sessionIds: Lists of updated IDs (if provided).
        :return: API response after mutation.
        """
        
        # Step 1: Fetch the existing template data
        existing_template = self.get_tinder_template_id(
            templateId=template_id, 
            return_object=True, 
            nopp=True, 
            dataframe=False)  # Assuming this returns the full structure

        if not existing_template:
            return {"status": "error", "message": "Template not found."}

        # Extract attributes
        attributes = existing_template.get("attributes", {})

        # Preserve current values if no update is provided
        updated_data = {
            "id": template_id,
            "name": name if name is not None else attributes.get("name", ""),
            "type": type if type is not None else attributes.get("type", ""),
            "tag": tag if tag is not None else attributes.get("tag", ""),
            "description": description if description is not None else attributes.get("description", ""),
            "attributes": {
                "template_questions": template_questions if template_questions else attributes.get("attributes", {}).get("template_questions", {})
            },

            "jobProfileIds": job_profile_ids if job_profile_ids is not None else [
                job["id"] for job in attributes.get("tinder_job_profiles", {}).get("data", [])
            ],
            "smgIds": smgIds if smgIds is not None else [
                metric["id"] for metric in attributes.get("smg_criterion_metrics", {}).get("data", [])
            ],
            "challengeIds": challengeIds if challengeIds is not None else [
                challenge["id"] for challenge in attributes.get("challenge_documents", {}).get("data", [])
            ],
            "sessionIds": sessionIds if sessionIds is not None else [
                session["id"] for session in attributes.get("i_persona_sessions", {}).get("data", [])
            ],
        }
        # return updated_data
        # Step 3: Send the GraphQL mutation
        mutation_query = """
            mutation UpdateTinderTemplate(
                $id: ID!, 
                $name: String!, 
                $type: String!, 
                $tag: String!,
                $description: String!,
                $attributes: JSON!, 
                $jobProfileIds: [ID!],
                $smgIds: [ID!],
                $challengeIds: [ID!],
                $sessionIds: [ID!]
            ) {
                updateTinderTemplate(id: $id, data: {
                    name: $name
                    type: $type
                    tag: $tag
                    description: $description
                    attributes: $attributes
                    tinder_job_profiles: $jobProfileIds 
                    smg_criterion_metrics: $smgIds
                    challenge_documents: $challengeIds
                    i_persona_sessions: $sessionIds
                }) {
                    data {
                        id
                        attributes {
                            name
                            type
                            tag
                            description
                            updatedAt
                            tinder_job_profiles { data { id } }
                            challenge_documents { data { id } }
                            smg_criterion_metrics { data { id } }
                            i_persona_sessions { data { id } }
                        }
                    }
                }
            }
        """

        # Step 4: Execute mutation
        res_json = self.sg.insert_table(query=mutation_query, variables=updated_data)

        # Step 5: Parse the response
        try:
            response = json.loads(res_json)
            template_data = response.get("data", {}).get("updateTinderTemplate", {}).get("data", {})
            
            if template_data:
                return {
                    "status": "success",
                    "message": "Template updated successfully.",
                    "data": {
                        "id": template_data.get("id"),
                        "name": template_data["attributes"].get("name"),
                        "type": template_data["attributes"].get("type"),
                        "updatedAt": template_data["attributes"].get("updatedAt"),
                    }
                }
            else:
                return {"status": "error", "message": "Failed to update template. No data returned."}

        except json.JSONDecodeError:
            return {"status": "error", "message": "Invalid JSON response from the server."}

    def add_job_profiles_to_template(
            self, 
            template_id, 
            new_job_profile_ids, 
            new_smg_criterion_metric_ids=[], 
            new_challenge_document_ids=[],
            new_session_ids=[]):
        # Step 1: Fetch the existing template data
        query = """
            query GetTemplate($id: ID!) {
                tinderTemplate(id: $id) {
                    data {
                        id
                        attributes {
                            name
                            type
                            tag
                            description
                            tinder_job_profiles(pagination:{start: 0, limit:-1}) {
                                data {
                                    id
                                }
                            }
                            challenge_documents(pagination:{start: 0, limit:-1}) {
                                data {
                                    id
                                }
                            }
                            smg_criterion_metrics(pagination:{start: 0, limit:-1}) {
                                data {
                                    id
                                }
                            }
                            i_persona_sessions(pagination:{start: 0, limit:-1}) {
                                data {
                                    id
                                }
                            }
                        }
                    }
                }
            }
        """
        
        variables = {"id": template_id}
        res_json = self.sg.Select_from_table(query=query, variables=variables)

        try:
            response = res_json
            
            # The correct path based on the log output
            if "data" in response and "tinderTemplate" in response["data"]:
                tinder_template = response["data"]["tinderTemplate"]
                
                if "data" in tinder_template:
                    template_data = tinder_template["data"]

                    if "attributes" in template_data:
                        attributes = template_data["attributes"]
                        tinder_job_profiles = attributes.get("tinder_job_profiles", {})  
                    
                        existing_job_profile_ids = [job.get("id") for job in tinder_job_profiles['data'] if isinstance(job, dict)]
                        #return existing_job_profile_ids
                        challenge_docs = attributes.get("challenge_documents", {})
                        doc_data = challenge_docs
                        existing_challenge_document_ids = [doc.get("id") for doc in doc_data['data'] if isinstance(doc, dict)]

                        metrics = attributes.get("smg_criterion_metrics", {})
                        metrics_data = metrics
                        existing_smg_criterion_metric_ids = [metric.get("id") for metric in metrics_data['data'] if isinstance(metric, dict)]

                        sessions = attributes.get("i_persona_sessions", {})
                        sessions_data = sessions
                        existing_i_persona_sessions_ids = [session.get("id") for session in sessions_data['data'] if isinstance(session, dict)]
                       
                        updated_job_profile_ids = list(set(existing_job_profile_ids + new_job_profile_ids))
                        updated_challenge_document_ids = list(set(existing_challenge_document_ids + new_challenge_document_ids))
                        updated_smg_criterion_metric_ids = list(set(existing_smg_criterion_metric_ids + new_smg_criterion_metric_ids))
                        updated_session_ids = list(set(existing_i_persona_sessions_ids + new_session_ids))
                        

                        # Handle None values for tag and description
                        tag = attributes.get("tag", "") or ""
                        description = attributes.get("description", "") or ""
                        
                        # Step 3: Update the template with the new lists
                        return self.update_template(
                            template_id=template_id,
                            name=attributes["name"],
                            type=attributes["type"],
                            tag=tag,
                            description=description,
                            template_questions={},
                            job_profile_ids=updated_job_profile_ids,
                            smgIds=updated_smg_criterion_metric_ids,
                            challengeIds=updated_challenge_document_ids,
                            sessionIds=updated_session_ids
                        )
                    else:
                        return {"status": "error", "message": "No attributes found in template data."}
                else:
                    return {"status": "error", "message": "No data field found in tinderTemplate."}
            else:
                return {"status": "error", "message": "Required data structure not found in response."}
        
        except Exception as e:
            return {"status": "error", "message": f"Error processing template data: {str(e)}"}            

class IpersonaChallengeDocumentSchema(LeapBaseClass):
    def __init__(self, run_stage='', **kwargs) -> None:
        self.kwargs = copy.deepcopy(kwargs)
        super().__init__(run_stage=run_stage, **kwargs)   

        
        self.table_single = kwargs.get('table_single', "")
        self.table = kwargs.get('table', "")
        self.data = kwargs.get('data', "")
        
        if not self.table_single:
            self.table_single = "challengeDocument"
            
        if not self.table:
            self.table = "challengeDocuments"
            
        if not self.data:
            logger.info(f"Using default data schema for {self.table_single} ...")
            self.data = '''
                data {
                    id
                    attributes {
                        Title
                        subtitle
                        challenge_sections(pagination:{start:0,limit:-1}) {
                            data {
                                id
                                attributes {
                                    content
                                }
                            }
                        } 
                        tinder_templates(pagination:{start:0, limit:-1}) {
                            data {
                                id
                            }
                        }
                        createdAt
                        updatedAt
                        %s
                    }
                }
            '''
        else:
            logger.info(f"Using passed data schema for {self.table_single} ...")
     
            
        self.type_map = {   
            "Title": "String",
            "subtitle": "String",
            "challenge_sections": "ID",
            "tinder_templates": "[ID!]"
        }

        self.id_names_map = {  }
         
        self.data_template = copy.deepcopy(self.data)
        self.data = self.data%""
        _ = self.process_extra_data(kwargs.get('extra_data', []), inplace=True)
    
    def get_challenge_by_id(self, challengeId, **kwargs):
        data_json = self.exists(scol='id', sval=challengeId, op='eq', stype="ID", **kwargs)  
        data = self.get_challenge_data(data_json)   
        return data
    
    def get_all_challenges(self, **kwargs):
        try:
          
            data = self.get_all_objects(**kwargs)
 
            challenge = self.get_challenges_data(data)

            if challenge is None:
                logger.warn("No challenge data found.")
                return None
            
            return challenge

        except Exception as e:
            logger.error(f"Error fetching all challenges: {str(e)}")
            return {'error': f"Error fetching all challenges: {str(e)}"}
        
    def save_if_new_user(self, scol, params, **kwargs):
        return self.save_if_new(scol, params, **kwargs)
    
    def get_extracted_data(self, challenge_json):
        try:
            if isinstance(challenge_json, list) and len(challenge_json) > 0:
                for entry in challenge_json:
                    if 'data' in entry:
                        challenge = entry.get('data')
                        return challenge
                        
            logger.warn("No valid data found in the challenge JSON.")
            return None

        except Exception as e:
            logger.error(f"Error extracting data from challenge JSON: {str(e)}")
            return {'error': f"Error extracting data from challenge JSON: {str(e)}"}  
  
    def get_challenges_data(self, challenge_json):
        try:
            all_challenges = []
            if isinstance(challenge_json, list) and len( challenge_json) > 0:
                for entry in challenge_json:
                    if 'data' in entry:
                        trainee = entry.get('data')                            
                        return trainee
            logger.warn("No challenges data found in the challenge JSON.")
            return None

        except Exception as e:
            logger.error(f"Error extracting challenge data from challenge JSON: {str(e)}")
            return {'error': f"Error extracting challenge data from challenge JSON: {str(e)}"}
    
    def get_challenge_data(self, challenge_json):
        try:
            all_challenges = []
            if isinstance(challenge_json, dict) and len(challenge_json) > 0:
                if 'data' in challenge_json:
                    return challenge_json['data']
                        
                logger.warn("No challenge data found in the challenge JSON.")
            return None

        except Exception as e:
            logger.error(f"Error extracting challenge data from challenge JSON: {str(e)}")
            return {'error': f"Error extracting challenge data from challenge JSON: {str(e)}"}

    def filter_by_template_id(self, template_id, cursor={}, **kwargs):
        try:
            if not cursor:
                cursor = True

            if not template_id:
                logger.warn("Invalid or missing template_id")
                return None

            template_id_filter = f"""
                filters: {{
                    tinder_templates : {{ id: {{ eq: {template_id} }} }}
                }}
            """
            data_json, cursor = self.get_all_objects(filter=template_id_filter, cursor=cursor, **kwargs)
            

            if not data_json:
                logger.warn(f"No job data found for template_id: {template_id}")
                return None
            
            data = self.get_extracted_data(data_json)
            data = self.challenge_extracted_data(data)
            # data = self.get_extracted_from_user_job_data(data_json)
            if not data:
                logger.warn(f"No extracted data for template_id: {template_id}")
                return None

            return data, cursor

        except Exception as e:
            logger.error(f"Error filtering challenges by template_id {template_id}: {e}")
            return None

    def challenge_extracted_data(self, data):
        """
        Extracts relevant challenge data from a JSON response.

        Parameters:
        ----------
        data : dict
            The JSON data containing challenge information.

        Returns:
        -------
        dict or None
            A dictionary of challenge data or None if no data is found.
        """
        try:
            # Extracted results
            simplified_challenges = []

            for challenge in data:
                challenge_id = challenge.get("id")
                attr = challenge.get("attributes", {})
                nested_attr = attr.get("attributes", {})

                challenge_info = {
                    "challenge_id": challenge_id,
                    "title": attr.get("Title") or nested_attr.get("Title"),
                    "subtitle": attr.get("subtitle") or nested_attr.get("subtitle"),
                }

                simplified_challenges.append(challenge_info)

            return simplified_challenges

        except Exception as e:
            logger.error(f"Error extracting challenge data: {e}")
            return None

    def filter_by_job_id(self, job_profile_id, **kwargs):
        """
        Fetches job data filtered by job profile ID.

        Parameters:
        ----------
        job_profile_id : int or str
            The job profile ID to filter jobs by.
        kwargs : dict
            Additional filtering arguments.

        Returns:
        -------
        list or None
            Filtered job data or None if an error occurs.
        """
        try:
            if not job_profile_id:
                logger.warn("Invalid or missing job_profile_id")
                return None

            job_filter = f"""
                filters: {{
                    id : {{ eq: {job_profile_id} }} 
                }}
            """
            data_json = self.get_all_objects(filter=job_filter, **kwargs)
            if not data_json:
                logger.warn(f"No job data found for job_profile_id: {job_profile_id}")
                return None
            
            data = self.get_extracted_data(data_json)
            if not data:
                logger.warn(f"No extracted data for job_profile_id: {job_profile_id}")
                return None

            return data

        except Exception as e:
            logger.error(f"Error filtering jobs by job_profile_id {job_profile_id}: {e}")
            return None

    def get_extracted_data(self, job_json):
        """
        Extracts relevant job or job data from a JSON response.

        Parameters:
        ----------
        job_json : dict
            The JSON data containing job or job information.

        Returns:
        -------
        list or None
            A list of extracted job or job data or None if no data is found.
        """
        try:
            if isinstance(job_json, list) and len(job_json) > 0:
                for entry in job_json:
                    if 'data' in entry:
                        job_data = entry.get('data')
                        return job_data
                        
            # if isinstance(job_json, list) and len(job_json) > 0:
            #     first_item = job_json[0]
            #     if 'data' in first_item:
            #         if 'tinderJobProfiles' in first_item['data']:
            #             job_data = first_item['data']['tinderJobProfiles']['data']
            #             if not job_data:
            #                 logger.warn("No job data found in the extracted data.")
            #                 return None
            #             return job_data
                    
            #         elif 'tinderUserProfiles' in first_item['data']:
            #             job_data = first_item['data']['tinderUserProfiles']['data']
            #             if not job_data:
            #                 logger.warn("No job data found in the extracted data.")
            #                 return None
            #             return job_data

            logger.warn("Invalid job_json format or missing data.")
            return None

        except Exception as e:
            logger.error(f"Error extracting data: {e}")
            return None
      
        # Initialize logging
     
class IpersonaSmgCretrionMetricSchema(LeapBaseClass):
    def __init__(self, run_stage='', **kwargs) -> None:
        self.kwargs = copy.deepcopy(kwargs)
        super().__init__(run_stage=run_stage, **kwargs)   

        
        self.table_single = kwargs.get('table_single', "")
        self.table = kwargs.get('table', "")
        self.data = kwargs.get('data', "")
        
        if not self.table_single:
            self.table_single = "smgCriterionMetric"
            
        if not self.table:
            self.table = "smgCriterionMetrics"
            
        if not self.data:
            logger.info(f"Using default data schema for {self.table_single} ...")
            self.data = '''
                data {
                    id
                    attributes {
                        title
                        tag
                        content
                        %s
                    }
                }
            '''
        else:
            logger.info(f"Using passed data schema for {self.table_single} ...")
     
            
        self.type_map = {   
            "title": "String",
            "tag": "String",
            "content": "String"
        }

        self.id_names_map = {  }
         
        self.data_template = copy.deepcopy(self.data)
        self.data = self.data%""
        _ = self.process_extra_data(kwargs.get('extra_data', []), inplace=True)
    
    def get_smgCriterionMetric_by_id(self, metricId, **kwargs):
        data_json = self.exists(scol='id', sval=metricId, op='eq', stype="ID", **kwargs)  
        data = self.get_smgCriterionMetric_data(data_json)   
        return data
    
    def get_all_smgCriterionMetrics(self, **kwargs):
        try:
          
            data = self.get_all_objects(**kwargs)
            metric = self.get_smgCriterionMetrics_data(data)

            if metric is None:
                logger.warn("No metric data found.")
                return None
            
            return metric

        except Exception as e:
            logger.error(f"Error fetching all metrics: {str(e)}")
            return {'error': f"Error fetching all metrics: {str(e)}"}
    
    def get_extracted_data(self, metric_json):
        try:
            if isinstance(metric_json, list) and len(metric_json) > 0:
                for entry in metric_json:
                    if 'data' in entry:
                        metric = entry.get('data')
                        return metric
                        
            logger.warn("No valid data found in the metric JSON.")
            return None

        except Exception as e:
            logger.error(f"Error extracting data from metric JSON: {str(e)}")
            return {'error': f"Error extracting data from metric JSON: {str(e)}"}  
  
    def get_smgCriterionMetrics_data(self, metric_json):
        try:
            all_metrics = []
            if isinstance(metric_json, list) and len( metric_json) > 0:
                for entry in metric_json:
                    if 'data' in entry:
                        trainee = entry.get('data')                            
                        return trainee
            logger.warn("No metrics data found in the metric JSON.")
            return None

        except Exception as e:
            logger.error(f"Error extracting metric data from metric JSON: {str(e)}")
            return {'error': f"Error extracting metric data from metric JSON: {str(e)}"}
    
    def get_smgCriterionMetric_data(self, metric_json):
        try:
            all_metrics = []
            if isinstance(metric_json, dict) and len(metric_json) > 0:
                if 'data' in metric_json:
                    return metric_json['data']
                        
                logger.warn("No metric data found in the metric JSON.")
            return None

        except Exception as e:
            logger.error(f"Error extracting metric data from metric JSON: {str(e)}")
            return {'error': f"Error extracting metric data from metric JSON: {str(e)}"}
