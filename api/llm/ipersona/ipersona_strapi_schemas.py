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

    def filter_by_tinder_user_profile_id(self, user_profile_id, **kwargs):
        try:
            if not user_profile_id:
                logger.error("User Profile ID is missing!")
                return None
            
            session_filter = f"""
                filters: {{
                    tinder_user_profile : {{ id: {{ eq: {user_profile_id} }} }}
                }}
            """

            data_json = self.get_all_objects(filter=session_filter, **kwargs)

            data = self.get_sessions_data(data_json)

            if data is None:
                logger.warn(f"No session data found for Tinder User Profile ID {user_profile_id}.")
                return None
            
            return data

        except Exception as e:
            logger.error(f"Error fetching session data for User Profile ID {user_profile_id}: {str(e)}")
            return {'error': f"Error fetching session data for User Profile ID {user_profile_id}: {str(e)}"}

    
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


    def get_all_sessions(self, **kwargs):
        try:
            session_json = self.get_all_objects(**kwargs)

            session = self.get_sessions_data(session_json)

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
            if isinstance(trainee_json, list) and len( trainee_json) > 0:
                for entry in trainee_json:
                    if 'data' in entry:
                        for trainee in entry.get('data'):                            
                            return trainee
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
                    else:
                        logger.warn("No user reactions found in 'tinderUserReactions'.")
                        return None
                else:
                    logger.warn("Missing expected data or 'tinderUserReactions' field in session JSON.")
                    return None
            else:
                logger.warn("Session JSON is empty or not in the expected list format.")
                return None

            return reaction_id

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
                "role": data['attributes']['role'],
                "Batch": data['attributes']['Batch']
            }

            return result

        except Exception as e:
            logger.error(f"Error fetching user data for All User ID {all_user_id}: {str(e)}")
            return {'error': f"Error fetching user data for All User ID {all_user_id}: {str(e)}"}

    
    def get_extracted_trainee_data(self, data_json):
        try:
            if isinstance(data_json, list) and len(data_json) > 0:
                for entry in data_json:
                    if 'data' in entry:
                        data_json = entry.get('data')
                        return data_json
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
                        data_json = entry.get('data')
                        return data_json
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
    