
import copy, os
from api.services.strapi_graphql import StrapiGraphql
from api.modules.leap_base import LeapBaseClass
from api.utils.logger import LLPackerLogger
logger = LLPackerLogger(os.path.basename(__file__))
from collections import defaultdict
capitalize = lambda x: x[0].upper() + x[1:]


class IpersonaManager(LeapBaseClass):
    def __init__(self, **kwargs):
        self.sessionId = kwargs.get("sessionId", 1)  
        self.alluserId = kwargs.get("alluserId", 1974)
        self.jobId = kwargs.get("jobId", 46)
        self.sg = StrapiGraphql(run_stage=kwargs.get("run_stage", "dev"))        
    
    def get_alluser_sessions(self):
        """
        Function to get all sessions from Strapi GraphQL with pagination, 
        filtered by `alluserId`'s `tinder_user_profile_id`.

        Returns:
            List containing session data with extracted observer attributes.
        """
        page_size = 100
        page = 1  
        all_sessions = []  

        # Getting the `tinder_user_profile_id` from the trainee user profile
        data = self.get_trainee_user_profile()
        if not data:
            logger.warn("No trainee user profiles found.")
            return []

        tinder_user_profile_id = data[0]['id']

        while True:
            sessions_query = """
                query GetIPersonaSessions($tinder_user_profile_id: ID!, $page: Int, $pageSize: Int) {
                    iPersonaSessions(
                        filters: {
                            tinder_user_profile: {
                                id: { eq: $tinder_user_profile_id }  
                            }
                        },
                        pagination: { page: $page, pageSize: $pageSize },
                        sort: "createdAt:desc"
                    ) {
                        data {
                            id
                            attributes {
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
                                tinder_job_profile {
                                    data {
                                        id
                                    }
                                }                               
                            }
                        }
                        meta {
                            pagination {
                                total
                                page
                                pageSize
                                pageCount
                            }
                        }
                    }
                }
            """
            
            sessions_json = self.sg.Select_from_table(
                query=sessions_query,
                variables={"tinder_user_profile_id": tinder_user_profile_id, "page": page, "pageSize": page_size}
            )

            if 'data' in sessions_json and 'iPersonaSessions' in sessions_json['data']:
                sessions_data = sessions_json['data']['iPersonaSessions']['data']
                all_sessions.extend(sessions_data)

                pagination = sessions_json['data']['iPersonaSessions']['meta']['pagination']
                if pagination['page'] >= pagination['pageCount']:
                    break
                else:
                    page += 1  
            else:
                logger.error("No data received or error in response.")
                break
        
        return all_sessions

    def get_job_sessions(self):
        """
        Function to get all sessions from Strapi GraphQL with pagination.

        Returns:
            List containing filtered sessions in ascending order based on createdAt.
        """
        page_size = 100 
        page = 1  
        all_sessions = []  
        
        # Getting the `tinder_user_profile_id` from the trainee user profile
        data = self.get_trainee_user_profile()
        if not data:
            logger.warn("No trainee user profiles found.")
            return []

        tinder_user_profile_id = data[0]['id']
        tinder_job_profile_id = self.jobId
        while True:
            sessions_query = """
                query GetIPersonaSessions($tinder_user_profile_id: ID!, $tinder_job_profile_id: ID!, $page: Int, $pageSize: Int) {
                    iPersonaSessions(
                        filters: {
                            tinder_user_profile: {
                                id: { eq: $tinder_user_profile_id }  
                            },
                            tinder_job_profile: {
                                id: { eq: $tinder_job_profile_id }  
                            }
                        },
                        pagination: { page: $page, pageSize: $pageSize }, sort: "createdAt:desc") {
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
                                tinder_job_profile {
                                    data {
                                        id
                                    }
                                } 
                            }     
                        }
                        meta {
                            pagination {
                                total
                                page
                                pageSize
                                pageCount
                            }
                        }
                    }
                }
            """
            
            sessions_json = self.sg.Select_from_table(
                query=sessions_query,
                variables={"tinder_user_profile_id": str(tinder_user_profile_id), "tinder_job_profile_id": str(tinder_job_profile_id), "page": page, "pageSize": page_size}           
            )

            if 'data' in sessions_json and 'iPersonaSessions' in sessions_json['data']:
                sessions_data = sessions_json['data']['iPersonaSessions']['data']
                all_sessions.extend(sessions_data) 

                pagination = sessions_json['data']['iPersonaSessions']['meta']['pagination']
                if pagination['page'] >= pagination['pageCount']:
                    break  
                else:
                    page += 1  
            else:
                print("No data received or error in response.")
                break
            
                 
        return all_sessions

    def get_session(self):
        """
        Function to get session from Strapi GraphQL

        Args:
            self.sessionId (Int): Number that represents the current session.

        Returns:
            DataFrame containing the requested session and related data.
        """

        session_query = """
            query GetIPersonaSession($sessionId: ID!) {
                iPersonaSession(id: $sessionId) {
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
                        }
                    }
                }
            }
        """

        session_json = self.sg.Select_from_table(
            query=session_query,
            variables={"sessionId": str(self.sessionId)}  
        )

        session = session_json['data']['iPersonaSession']['data']
        
        return session
    
    def get_observers(self):
        all_observers = [] 
        page = 1  
        page_size = 100  
        
        while True:
            session_messages_query = f"""
                query GetIPersonaObservers($sessionId: ID!, $page: Int, $pageSize: Int) {{
                    iPersonaObservers(
                        filters: {{
                            i_persona_session: {{ 
                                id: {{ eq: $sessionId }} 
                            }} 
                        }},
                        pagination: {{ page: $page, pageSize: $pageSize }}
                    ) {{
                        data {{
                            id
                            attributes {{
                                attributes
                                metadata
                                i_persona_session {{
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
            """
            
            res_json = self.sg.Select_from_table(
                query=session_messages_query,
                variables={"sessionId": str(self.sessionId), "page": page, "pageSize": page_size}
            )
            
            if 'data' in res_json and 'iPersonaObservers' in res_json['data']:
                messages = res_json['data']['iPersonaObservers']['data']
                if messages:
                    all_observers.extend(messages)  
                
                pagination = res_json['data']['iPersonaObservers']['meta']['pagination']
                
                if pagination['page'] >= pagination['pageCount']:
                    break  
                else:
                    page += 1 
            else:
                print("No data received or error in response.")
                break
                        
        return all_observers
     
    def get_messages(self):
        all_messages = [] 
        page = 1  
        page_size = 100  
        
        while True:
            session_messages_query = f"""
                query GetIPersonaMessages($sessionId: ID!, $page: Int, $pageSize: Int) {{
                    iPersonaMessages(
                        filters: {{
                            i_persona_session: {{ 
                                id: {{ eq: $sessionId }} 
                            }} 
                        }},
                        pagination: {{ page: $page, pageSize: $pageSize }},
                        sort: "createdAt:asc"  
                    ) {{
                        data {{
                            id
                            attributes {{
                                attributes
                                metadata
                                i_persona_session {{
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
            """
            
            res_json = self.sg.Select_from_table(
                query=session_messages_query,
                variables={"sessionId": str(self.sessionId), "page": page, "pageSize": page_size}
            )
            
            if 'data' in res_json and 'iPersonaMessages' in res_json['data']:
                messages = res_json['data']['iPersonaMessages']['data']
                if messages:
                    all_messages.extend(messages)  
                
                pagination = res_json['data']['iPersonaMessages']['meta']['pagination']
                
                if pagination['page'] >= pagination['pageCount']:
                    break  
                else:
                    page += 1 
            else:
                print("No data received or error in response.")
                break
            
        # Extract the required fields from the messages
        extracted_messages = []
        for message in all_messages:
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
    
    def get_trainee_user_profile(self):
        page_size = 10
        page = 1  
        all_sessions = [] 
        
        while True:
            query = """
            query GetTinderUserProfiles($alluserId: ID!, $page: Int, $pageSize: Int) {
                    tinderUserProfiles(
                        filters: {
                            all_users: {
                                id: { 
                                    eq: $alluserId
                                }  
                            }                            
                        },
                        pagination: { page: $page, pageSize: $pageSize }
                    ) {
                        data {
                            id
                            attributes {
                                attributes
                                all_users {
                                    data {
                                        id
                                    }        	
                                }                                 
                            }
                        }
                        meta {
                            pagination {
                                total
                                page
                                pageSize
                                pageCount
                            }
                        }
                    }
                }                
            """
            
            res_json = self.sg.Select_from_table(
                query=query,
                variables={"alluserId": str(self.alluserId), "page": page, "pageSize": page_size}
            )
            
            if 'data' in res_json and 'tinderUserProfiles' in res_json['data']:
                messages = res_json['data']['tinderUserProfiles']['data']
                if messages:
                    all_sessions.extend(messages)  
                
                pagination = res_json['data']['tinderUserProfiles']['meta']['pagination']
                
                if pagination['page'] >= pagination['pageCount']:
                    break  
                else:
                    page += 1 
            else:
                print("No data received or error in response.")
                break
                        
        return all_sessions
    
    def get_trainee_job_profile(self):
        page_size = 10
        page = 1  
        all_sessions = []  
        
        while True:
            sessions_query = """
            query GetTinderJobProfiles($jobId: ID!, $page: Int, $pageSize: Int) {
                    tinderJobProfiles(
                        filters: {
                            id: { 
                                eq: $jobId
                            } 
                        },
                        pagination: { page: $page, pageSize: $pageSize }
                    ) {
                        data {
                            id
                            attributes {
                                attributes                                
                            }
                        }
                        meta {
                            pagination {
                                total
                                page
                                pageSize
                                pageCount
                            }
                        }
                    }
                }
            """
            
            res_json = self.sg.Select_from_table(
                query=sessions_query,
                variables={"jobId": str(self.jobId), "page": page, "pageSize": page_size}
            )
            
            if 'data' in res_json and 'tinderJobProfiles' in res_json['data']:
                messages = res_json['data']['tinderJobProfiles']['data']
                if messages:
                    all_sessions.extend(messages)  
                
                pagination = res_json['data']['tinderJobProfiles']['meta']['pagination']
                
                if pagination['page'] >= pagination['pageCount']:
                    break  
                else:
                    page += 1 
            else:
                print("No data received or error in response.")
                break
                        
        return all_sessions
    
    def get_match(self, tinder_user_profile_id, tinder_job_profile_id):
        page_size = 10
        page = 1  
        all_matches = []  
        
        while True:
            query = """
            query GetTinderUserJobMatch($tinder_user_profile_id: ID!, $tinder_job_profile_id: ID!, $page: Int, $pageSize: Int) {
                tinderUserJobMatches(
                    filters: {
                        tinder_user_profile: {
                            id: { eq: $tinder_user_profile_id }  
                        },
                        tinder_job_profile: {
                            id: { eq: $tinder_job_profile_id }  
                        }
                    },
                    pagination: { page: $page, pageSize: $pageSize }
                ) {
                    data {
                        id
                        attributes {
                            match_score
                            match_level                               
                        }
                    }
                    meta {
                        pagination {
                            total
                            page
                            pageSize
                            pageCount
                        }
                    }
                }
            }
            """
            
            res_json = self.sg.Select_from_table(
                query=query,
                variables={"tinder_user_profile_id": str(tinder_user_profile_id), "tinder_job_profile_id": str(tinder_job_profile_id), "page": page, "pageSize": page_size}
            )
            
            
            if 'data' in res_json and 'tinderUserJobMatches' in res_json['data']:
                matches = res_json['data']['tinderUserJobMatches']['data']
                if matches:
                    all_matches.extend(matches)
                
                pagination = res_json['data']['tinderUserJobMatches']['meta']['pagination']
                
                if pagination['page'] >= pagination['pageCount']:
                    break  
                else:
                    page += 1 
            else:
                print("No data received or error in response.")
                break
                        
        return all_matches

             
    def session_overall_observer_by_user_and_job(self):
        page_size = 100
        page = 1
        all_sessions = []
        id = None
        
        # Getting the `tinder_user_profile_id` from the trainee user profile
        data = self.get_trainee_user_profile()
        if not data:
            logger.warn("No trainee user profiles found.")
            return []

        tinder_user_profile_id = data[0]['id']
        tinder_job_profile_id = self.jobId
            

        while True:
            sessions_query = """
                query GetIPersonaSessionOverallObservers($tinder_user_profile_id: ID!, $tinder_job_profile_id: ID!, $page: Int, $pageSize: Int) {
                    iPersonaSessionOverallObservers(
                        filters: {
                            tinder_user_profile: {
                                id: { eq: $tinder_user_profile_id }  
                            },
                            tinder_job_profile: {
                                id: { eq: $tinder_job_profile_id }  
                            }
                        },
                        pagination: { page: $page, pageSize: $pageSize },
                        sort: "createdAt:desc"
                    ) {
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
                            }
                        }
                        meta {
                            pagination {
                                total
                                page
                                pageSize
                                pageCount
                            }
                        }
                    }
                }
            """
            
            sessions_json = self.sg.Select_from_table(
                query=sessions_query,
                variables={"tinder_user_profile_id": str(tinder_user_profile_id), "tinder_job_profile_id": str(tinder_job_profile_id), "page": page, "pageSize": page_size}  
            )            

            #return sessions_json
            if 'data' in sessions_json and 'iPersonaSessionOverallObservers' in sessions_json['data']:
                sessions_data = sessions_json['data']['iPersonaSessionOverallObservers']['data']

                for session in sessions_data:
                    attributes = session.get('attributes', {}).get('attributes', {})
                    id = session.get('id', '')
                    all_sessions.append(attributes)            

                if page >= sessions_json['data']['iPersonaSessionOverallObservers']['meta']['pagination']['pageCount']:
                    break
                
                page += 1
            else:
                break
            
        result = {
            "id": id,
            "all_sessions": all_sessions
        }
        return result
    
    
    def session_overall_observer_by_user(self):
        page_size = 100
        page = 1
        all_sessions = []

        # Getting the `tinder_user_profile_id` from the trainee user profile
        data = self.get_trainee_user_profile()
        if not data:
            logger.warn("No trainee user profiles found.")
            return []

        tinder_user_profile_id = data[0]['id']
        
        while True:
            sessions_query = """
                query GetIPersonaSessionOverallObservers($tinder_user_profile_id: ID!, $page: Int, $pageSize: Int) {
                    iPersonaSessionOverallObservers(
                        filters: {
                            tinder_user_profile: {
                                id: { eq: $tinder_user_profile_id }  
                            }
                        },
                        pagination: { page: $page, pageSize: $pageSize },
                        sort: "createdAt:desc"
                    ) {
                        data {
                            id
                            attributes {
                                attributes
                                tinder_user_profile {
                                    data {
                                        id
                                    }
                                }
                            }
                        }
                        meta {
                            pagination {
                                total
                                page
                                pageSize
                                pageCount
                            }
                        }
                    }
                }
            """

            sessions_json = self.sg.Select_from_table(
                query=sessions_query,
                variables={"tinder_user_profile_id": tinder_user_profile_id, "page": page, "pageSize": page_size}
            )

            #return sessions_json
            if 'data' in sessions_json and 'iPersonaSessionOverallObservers' in sessions_json['data']:
                sessions_data = sessions_json['data']['iPersonaSessionOverallObservers']['data']
                for session in sessions_data:
                    session_attributes = session.get('attributes', {}).get('attributes', {})
                    all_sessions = session_attributes 
                
                if page >= sessions_json['data']['iPersonaSessionOverallObservers']['meta']['pagination']['pageCount']:
                    break
                
                page += 1
            else:
                break
        
        return all_sessions


    def create_session(self, message_data):
        """
        Function to insert a new session into the iPersonaSession table in Strapi using a GraphQL mutation.

        Args:
            message_data (dict): A dictionary containing the data to be inserted, including slug, attributes, and metadata.

        Returns:
            result_json (Json): The response from Strapi after the mutation.
        """

        mutation_query = """
            mutation CreateIPersonaSession($slug: String!, $attributes: JSON!, $metadata: JSON!, $status: String!, $jobId: ID!, $alluserId: ID!) {
                createIPersonaSession(data: {
                    slug: $slug,
                    attributes: $attributes,
                    metadata: $metadata,
                    tinder_user_profile: $alluserId,
                    tinder_job_profile: $jobId,
                    status: $status
                }) {
                    data {
                        id
                        attributes {
                            slug
                            attributes
                            metadata                            
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
                            status
                        }                        
                    }
                }
            }
        """

        variables = {
            "slug": message_data.get("slug"),
            "attributes": message_data.get("attributes"),
            "metadata": message_data.get("metadata"),
            "status": 'Incomplete',
            "alluserId": message_data.get("alluserId"),
            "jobId": message_data.get("jobId"),  
        }

        res_json = self.sg.insert_table(query=mutation_query, variables=variables)

        if 'data' in res_json and 'createIPersonaSession' in res_json['data']:
            res_json = res_json['data']['createIPersonaSession']['data']
        else:
            raise ValueError("Failed to create session. Response: {}".format(res_json))

        return res_json
    
    def insert_message(self, message_data):
        """
        Function to insert a new message into the iPersonaMessages table in Strapi using a GraphQL mutation.

        Args:
            message_data (dict): A dictionary containing the data to be inserted, including attributes, metadata, and i_persona_session.

        Returns:
            result_json (Json): The response from Strapi after the mutation.
        """
        
        mutation_query = """
            mutation CreateIPersonaMessage($attributes: JSON!, $metadata: JSON, $sessionId: ID!) {
                createIPersonaMessage(data: {
                    attributes: $attributes,
                    metadata: $metadata,
                    i_persona_session: $sessionId  
                }) {
                    data {
                        id
                        attributes {
                            attributes
                            metadata
                            i_persona_session {
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
            "attributes": message_data.get("attributes"),
            "metadata": message_data.get("metadata"),
            "sessionId": str(self.sessionId)  
        }
        
        res_json = self.sg.insert_table(query=mutation_query, variables=variables)

        if 'data' in res_json and 'createIPersonaMessage' in res_json['data']:
            return res_json['data']['createIPersonaMessage']['data']
        else:
            print("Error inserting message:", res_json)  
            raise ValueError("Failed to insert message. Response: {}".format(res_json))

    def insert_observer(self, message_data):
        """
        Function to insert a new observer into the iPersonaObserver table in Strapi using a GraphQL mutation.

        Args:
            message_data (dict): A dictionary containing the data to be inserted, including attributes, metadata, and i_persona_session.

        Returns:
            result_json (Json): The response from Strapi after the mutation.
        """
        
        mutation_query = """
            mutation CreateIPersonaObserver($attributes: JSON!, $metadata: JSON, $sessionId: ID!) {
                createIPersonaObserver(data: {
                    attributes: $attributes,
                    metadata: $metadata,
                    i_persona_session: $sessionId
                }) {
                    data {
                        id
                        attributes {
                            attributes
                            metadata
                            i_persona_session {
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
            "attributes": message_data.get("attributes"),
            "metadata": message_data.get("metadata"),
            "sessionId": str(self.sessionId)  
        }
        
        res_json = self.sg.insert_table(query=mutation_query, variables=variables)

        if 'data' in res_json and 'createIPersonaObserver' in res_json['data']:
            return res_json['data']['createIPersonaObserver']['data']
        else:
            print("Error inserting observer:", res_json)  
            raise ValueError("Failed to insert observer. Response: {}".format(res_json))
    
    def create_session_overall_observer(self, message_data):
        """
        Function to insert a new overall session status metrics into the iPersonSessionOverallObserver table in Strapi.

        Args:
            message_data (dict): A dictionary containing the data to be inserted, including slug, attributes, and metadata.

        Returns:
            result_json (Json): The response from Strapi after the mutation.
        """

        mutation_query = """
            mutation CreateIPersonaSessionOverallObserver($attributes: JSON!, $metadata: JSON!, $jobId: ID!, $alluserId: ID!, $sessionIds: [ID]!) {
                createIPersonaSessionOverallObserver(data: {
                    attributes: $attributes,
                    metadata: $metadata,
                    tinder_user_profile: $alluserId,
                    tinder_job_profile: $jobId,
                    i_persona_observers: $sessionIds
                }) {
                    data {
                        id
                        attributes {
                            attributes
                            metadata
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
                            i_persona_observers {
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
            "attributes": message_data.get("attributes"),
            "metadata": message_data.get("metadata"),
            "alluserId": message_data.get("alluserId"),
            "jobId": message_data.get("jobId"),  
            "sessionIds": message_data.get("sessionIds")       
        }

        # Execute the GraphQL mutation
        res_json = self.sg.insert_table(query=mutation_query, variables=variables)

        return res_json
    
    def update_session_job_observer(self, attributes):
        """
        Function to update the status of a session job in Strapi GraphQL.

        Args:
            attributes (dict): The new attributes to update in the session.

        Returns:
            JSON response of the updated session.
        """

        uquery = """
            mutation UpdateIPersonaSessionOverallObserver(
                $sessionId: ID!,
                $attributes: JSON!
            ) {
                updateIPersonaSessionOverallObserver(
                    id: $sessionId,
                    data: {
                        attributes: $attributes
                    }
                ) {
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
                        }
                    }
                }
            }
        """

        variables = {
            "sessionId": str(self.sessionId),
            "attributes": attributes 
        }

        updatedSession = self.sg.Select_from_table(query=uquery, variables=variables)

        return updatedSession


    def update_session_status(self):
        """
        Function to update the status of a session in Strapi GraphQL.

        Returns:
            JSON response of the updated session.
        """
        uquery = """
            mutation UpdateIPersonaSession($sessionId: ID!, $status: String!) {
                updateIPersonaSession(id: $sessionId, data: { status: $status }) {
                    data {
                        id
                        attributes {
                            slug
                            status  
                            i_persona_observer {
                                data {
                                    id
                                    attributes {
                                        attributes
                                        metadata
                                    }
                                }
                            }
                            i_persona_messages {
                                data {
                                    id
                                    attributes {
                                        attributes
                                        metadata
                                    }
                                }
                            }
                            createdAt
                        }
                    }
                }
            }
        """

        updatedSession = self.sg.Select_from_table(query=uquery, variables={"sessionId": str(self.sessionId), "status": 'Complete'})
        return updatedSession