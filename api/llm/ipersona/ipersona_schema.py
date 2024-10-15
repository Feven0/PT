import weaviate, os
from dotenv import dotenv_values
import datetime
from dotenv import load_dotenv
load_dotenv("../../.env")

WEAVIATE_URL="https://e6kekvphscq3b73q4sybda.c0.us-east1.gcp.weaviate.cloud"
WEAVIATE_API_KEY="VdjnBgP8twfjgPSpejpCyuWVGjdpBgdaEaGR"
client = weaviate.Client(
    url=WEAVIATE_URL,
    auth_client_secret=weaviate.AuthApiKey(api_key=WEAVIATE_API_KEY),
)

schema = {
    "classes": [
        {
            "class": "iPersonaSessionOld",
            "properties": [
                {
                    "name": "userId", 
                    "dataType": ["string"]
                },
                {
                    "name": "sessionId", 
                    "dataType": ["string"]
                },
                {
                    "name": "username", 
                    "dataType": ["string"], 
                    "default": "null"
                },
                {
                    "name": "user_profile", 
                    "dataType": ["string"], 
                    "default": "null"
                },
                {
                    "name": "jobId", 
                    "dataType": ["string"]
                },
                {
                    "name": "job_desc", 
                    "dataType": ["string"], 
                    "default": "null"
                },                
                {
                    "name": "persona",
                    "dataType": ["string"],  
                    "default": "null"
                },
                {
                    "name": "generated_questions",
                    "dataType": ["string"],  
                    "default": "null"
                },
                {
                    "name": "createdAt", 
                    "dataType": ["date"]
                },
                {
                    "name": "updatedAt", 
                    "dataType": ["date"]
                }
            ],
            "vectorizer": "none"
        },
        {
            "class": "iPersonaInterviewHistory",
            "properties": [
                {
                    "name": "userId", 
                    "dataType": ["string"]
                },
                {
                    "name": "sessionId", 
                    "dataType": ["string"]
                },
                {
                    "name": "jobId", 
                    "dataType": ["string"]
                },
                {
                    "name": "chathistory", 
                    "dataType": ["string"],  
                    "default": "null"
                },
                {
                    "name": "createdAt", 
                    "dataType": ["date"]
                },
                {
                    "name": "updatedAt", 
                    "dataType": ["date"]
                }
            ],
            "vectorizer": "none"
        }            
    ]
}


def get_current_time():
    return datetime.datetime.utcnow().isoformat() + "Z" 


async def create_schema(data):
    try:
        existing_schema = client.schema.get()
        persona_session_exists = any(cls['class'] == "iPersonaSessionOld" for cls in existing_schema['classes'])
        persona_interview_history_exists = any(cls['class'] == "iPersonaInterviewHistory" for cls in existing_schema['classes'])
     
        if not persona_session_exists and not persona_interview_history_exists:
            client.schema.create(schema)  
            uploaded_uuid = await Add_session_schema_data(data)
            print("Classes 'iPersonaSessionOld' and 'iPersonaInterviewHistory created successfully.")
        else:
            print("Classes already exist. No new classes created.")
            uploaded_uuid = await Add_session_schema_data(data)
        
        print("Data inserted!")
        return uploaded_uuid

    except Exception as e:
        print("not working", e)
        return f'Error: {str(e)}'
     
        
async def Add_session_schema_data(data):
    try:
        ipersona_data = {
        "userId": data['userId'], 
        "sessionId": data['sessionId'],        
        "username": data['username'],
        "user_profile": str(data.get('user_profile', '')),
        "jobId": data['jobId'], 
        "job_desc": str(data.get('job_desc', '')),
        "persona": data['persona'],
        "generated_questions": str(data.get('generated_questions', '')),
        "createdAt": get_current_time(),
        "updatedAt": get_current_time()
        }

        ipersona_upload = client.data_object.create(
            data_object=ipersona_data,
            class_name="iPersonaSessionOld"
        )
        
        return ipersona_upload
    except Exception as e:
        return f'Error: {str(e)}' 
    
    
async def Add_Interview_History(data):
    try:
        ipersona_chat_data = {
        "userId": data['userId'], 
        "sessionId": data['sessionId'], 
        "jobId": data['jobId'],
        "chathistory": str(data['chathistory']),
        "createdAt": get_current_time(),
        "updatedAt": get_current_time()
        }

        ipersona_upload_history = client.data_object.create(
            data_object=ipersona_chat_data,
            class_name="iPersonaInterviewHistory"
        )
        
        return ipersona_upload_history
    except Exception as e:
        return f'Error: {str(e)}' 


async def update_ipersona_data_new(data, fields_to_update):    
    print("Updating data for ID:", data['id'])
    update_data = {}
    
    if 'chathistory' in fields_to_update:
        update_data['chathistory'] = str(data.get('chathistory', ''))    
    try:
        result = client.data_object.update(
            uuid=data['id'],
            data_object=update_data,
            class_name='iPersonaInterviewHistory'
        )
        
        print("Updating Successful:", True)
        return True
    
    except Exception as e:
        return f'Error During Update: {str(e)}'

 
async def fetch_session(userId):
    try:
        sessions_with_user_id = client.query.get(
            class_name="iPersonaSessionOld",
            properties=[
                "userId",
                "sessionId",                
                "username",
                "user_profile",
                "jobId",
                "job_desc",
                "persona",
                "generated_questions"
            ] 
        ).with_where({
            "path": ["userId"],
            "operator": "Equal",
            "valueString": str(userId)
        }).with_additional("id").do()
        
        length = len(sessions_with_user_id['data']['Get']['IPersonaSessionOld'])
        index = length - 1
        result = sessions_with_user_id['data']['Get']['IPersonaSessionOld'][index]
        data= {
            "all_data": sessions_with_user_id['data']['Get']['IPersonaSessionOld'],
            "latest_data": result
        }
        return data
    except Exception as e:
        print("Error fetching Sessions:", e)
        

async def fetch_chat_history(userId, sessionId, jobId):
    try:
        job_with_session_id = client.query.get(
            class_name="iPersonaInterviewHistory",
            properties=[
                "chathistory"
                ]  
        ).with_where({
            "operator": "And", 
            "operands": [
                {
                    "path": ["userId"],
                    "operator": "Equal",
                    "valueString": userId
                },
                {
                    "path": ["sessionId"],
                    "operator": "Equal",
                    "valueString": sessionId
                },
                {
                    "path": ["jobId"],
                    "operator": "Equal",
                    "valueString": jobId
                }
            ]
        }).with_additional("id").do()
        
        result = job_with_session_id['data']['Get']['IPersonaInterviewHistory']

        return result
    except Exception as e:
        print("Error fetching Sessions:", e)
        
 
