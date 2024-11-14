
import pandas as pd
import re
from api.services.strapi_graphql import StrapiGraphql


class IpersonaManager:
    def __init__(self, **kwargs):
        self.sessionId = kwargs.get("sessionId", 1)  
        self.alluser = kwargs.get("alluser", 16)
        self.jobId = kwargs.get("jobId", 1045)
        self.sg = StrapiGraphql(run_stage=kwargs.get("run_stage", "dev"))
    
    def get_alluser_sessions(self):
        """
        Function to get all sessions from Strapi GraphQL with pagination.

        Returns:
            List containing all the sessions filtered by `alluser`.
        """
        page_size = 100 
        page = 1  
        all_sessions = []  
        
        while True:
            sessions_query = """
                query GetIPersonaSessions($page: Int, $pageSize: Int) {
                    iPersonaSessions(
                        pagination: { page: $page, pageSize: $pageSize },
                        sort: "createdAt:desc"  # Sort by createdAt in descending order
                    ) {
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
                                # i_persona_messages {
                                #     data {
                                #         attributes {
                                #             attributes,
                                #             metadata
                                #         }
                                #     }        	
                                # }
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
                variables={"page": page, "pageSize": page_size}  
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
                
        filtered_data = [
            item for item in all_sessions 
            if item['attributes']['attributes']['alluser'] == self.alluser
        ] 
                
        extracted_observers = []
        for message in filtered_data:
            if message['attributes'].get('i_persona_observer') and message['attributes']['i_persona_observer'].get('data'):
                message_data = message['attributes']['i_persona_observer']['data']            
                message_attributes = message_data['attributes']['attributes']['interview_evaluation_metrics']
                message_attributes['createdAt'] = message['attributes']['createdAt']          
                extracted_observers.append(message_attributes)

        return extracted_observers
        
    def get_job_sessions_observers(self):
        """
        Function to get all sessions from Strapi GraphQL with pagination.

        Returns:
            List containing filtered sessions in ascending order based on createdAt.
        """
        page_size = 100 
        page = 1  
        all_sessions = []  
        
        while True:
            sessions_query = """
                query GetIPersonaSessions($page: Int, $pageSize: Int) {
                    iPersonaSessions(pagination: { page: $page, pageSize: $pageSize }, sort: "createdAt:desc") {
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
                variables={"page": page, "pageSize": page_size}  
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
            
        filtered_data = [
            item for item in all_sessions
            if item['attributes']['attributes']['alluser'] == self.alluser and item['attributes']['attributes']['jobId'] == self.jobId
        ]   
                    
        extracted_observers = []
        for message in filtered_data:
            if message['attributes'].get('i_persona_observer') and message['attributes']['i_persona_observer'].get('data'):
                message_data = message['attributes']['i_persona_observer']['data']
                message_attributes = message_data['attributes']['attributes']['interview_evaluation_metrics']
                message_attributes['createdAt'] = message['attributes']['createdAt']
                extracted_observers.append(message_attributes)

        return extracted_observers
    
    def get_job_sessions(self):
        """
        Function to get all sessions from Strapi GraphQL with pagination.

        Returns:
            List containing filtered sessions in ascending order based on createdAt.
        """
        page_size = 100 
        page = 1  
        all_sessions = []  
        
        while True:
            sessions_query = """
                query GetIPersonaSessions($page: Int, $pageSize: Int) {
                    iPersonaSessions(pagination: { page: $page, pageSize: $pageSize }, sort: "createdAt:desc") {
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
                variables={"page": page, "pageSize": page_size}  
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
            
        filtered_data = [
            item for item in all_sessions
            if item['attributes']['attributes']['alluser'] == self.alluser and item['attributes']['attributes']['jobId'] == self.jobId
        ]   
                    
        return filtered_data

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
    
    def create_session(self, message_data):
        """
        Function to insert a new session into the iPersonaSession table in Strapi using a GraphQL mutation.

        Args:
            message_data (dict): A dictionary containing the data to be inserted, including slug, attributes, and metadata.

        Returns:
            result_json (Json): The response from Strapi after the mutation.
        """

        mutation_query = """
            mutation CreateIPersonaSession($slug: String!, $attributes: JSON!, $metadata: JSON!, $status: String!) {
                createIPersonaSession(data: {
                    slug: $slug,
                    attributes: $attributes,
                    metadata: $metadata,
                    status: $status
                }) {
                    data {
                        id
                        attributes {
                            slug
                            attributes
                            metadata
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
            "status": 'Incomplete'  
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
                    i_persona_session: $sessionId  # Fix typo here
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