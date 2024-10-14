import weaviate, os, ast
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
            "class": "iPersonaSession",
            "properties": [
                {
                    "name": "alluser", 
                    "dataType": ["string"]
                },
                {
                    "name": "userId", 
                    "dataType": ["string"]
                },
                {
                    "name": "jobId", 
                    "dataType": ["string"]
                }, 
                {
                    "name": "username", 
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
            "class": "iPersonaMessages",
            "properties": [
                {
                    "name": "sessionId", 
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
        },
        {
            "class": "iPersonaObserver",
            "properties": [
                {
                    "name": "sessionId", 
                    "dataType": ["string"]
                },
                {
                    "name": "interview_evaluation", 
                    "dataType": ["string"],  
                    "default": "null"
                },
                {
                    "name": "interview_evaluation_metrics", 
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
        persona_session_exists = any(cls['class'] == "IPersonaSession" for cls in existing_schema['classes'])
        persona_interview_history_exists = any(cls['class'] == "iPersonaMessages" for cls in existing_schema['classes'])
        persona_interview_observer_exists = any(cls['class'] == "iPersonaObserver" for cls in existing_schema['classes'])
     
        if not persona_session_exists and not persona_interview_history_exists and not persona_interview_observer_exists:
            client.schema.create(schema)  
            uploaded_uuid = await Add_session_schema_data(data)
            print("All Classes created successfully.")
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
        ipersona_session_data = {
        "alluser": data['alluser'], 
        "userId": data['userId'], 
        "jobId": data['jobId'], 
        "username": data['username'],
        "persona": data['persona'],
        "generated_questions": str(data.get('generated_questions', '')),
        "createdAt": get_current_time(),
        "updatedAt": get_current_time()
        }

        ipersona_upload = client.data_object.create(
            data_object=ipersona_session_data,
            class_name="iPersonaSession"
        )
        user_session = await fetch_session(data['userId'])

        return user_session
    except Exception as e:
        return f'Error Adding Session: {str(e)}' 
    
    
async def Add_Interview_History(sessionId, chathistory):
    print("######add interview#####")
    print(chathistory)
    session_chathistory = await fetch_chat_history(sessionId)
    try:
        if len(session_chathistory) == 0:
            print("session inteview does not exist")
            ipersona_chat_data = {
            "sessionId": sessionId, 
            "chathistory": str(chathistory),
            "createdAt": get_current_time(),
            "updatedAt": get_current_time()
            }

            ipersona_upload_history = client.data_object.create(
                data_object=ipersona_chat_data,
                class_name="iPersonaMessages"
            )
            print("session interview created", ipersona_upload_history)
            return ipersona_upload_history
        else:
            print("session interview exist")
            session_chathistory[0]['chathistory'].extend(chathistory) 

            data = {
                "sessionId": session_chathistory[0]['_additional']['id'],
                "chathistory": session_chathistory[0]['chathistory']
            }
            updated = await update_ipersona_data_new(data)     
            print("updated!", updated)
            return updated

    except Exception as e:
        return f'Error: {str(e)}' 
    
async def Add_Interview_Observer(sessionId, interview_evaluation, interview_evaluation_metrics):
    try:
        ipersona_chat_observer = {
            "sessionId": sessionId, 
            "interview_evaluation": str(interview_evaluation),
            "interview_evaluation_metrics": str(interview_evaluation_metrics),
            "createdAt": get_current_time(),
            "updatedAt": get_current_time()
        }

        ipersona_upload_history = client.data_object.create(
            data_object=ipersona_chat_observer,
            class_name="iPersonaObserver"
        )

        return ipersona_upload_history
    except Exception as e:
        return f'Error: {str(e)}'


async def update_ipersona_data_new(data):  
    update_data = {}
    
    if 'chathistory' in data:
        update_data['chathistory'] = str(data.get('chathistory', ''))    
    try:
        result = client.data_object.update(
            uuid=data['sessionId'],
            data_object=update_data,
            class_name='iPersonaMessages'
        )
        
        print("Updating Successful:", True)
        return True
    
    except Exception as e:
        return f'Error During Update: {str(e)}'

 
async def fetch_session(userId):
    try:
        sessions_with_user_id = client.query.get(
            class_name="iPersonaSession",
            properties=[
                "alluser",
                "userId",
                "jobId",
                "username",
                "persona",
                "generated_questions",
                "createdAt"
            ] 
        ).with_where({
            "path": ["userId"],
            "operator": "Equal",
            "valueString": userId 
        }).with_additional("id").do()
        
        length = len(sessions_with_user_id['data']['Get']['IPersonaSession'])
        index = length - 1
        result = sessions_with_user_id['data']['Get']['IPersonaSession'][index]
        user_data= {
            "all_data": sessions_with_user_id['data']['Get']['IPersonaSession'],
            "latest_data": result
        }
        
        if 'generated_questions' in user_data["latest_data"]:
            question_data = user_data["latest_data"]['generated_questions']
            if question_data:
                try:
                    user_data["latest_data"]['generated_questions'] = ast.literal_eval(question_data)
                except (ValueError, SyntaxError) as e:
                    print(f"Error parsing generated_questions: {e}")
                     
        data = {
            "all_user_data": user_data["all_data"],
            "latest_user_data": user_data["latest_data"]
        } 
        return data
    except Exception as e:
        print("Error fetching Sessions:", e)
        

async def fetch_chat_history(sessionId):
    try:
        job_with_session_id = client.query.get(
            class_name="iPersonaMessages",
            properties=[
                "chathistory"
                ]  
        ).with_where({
            "operator": "And", 
            "operands": [
                {
                    "path": ["sessionId"],
                    "operator": "Equal",
                    "valueString": sessionId
                }
            ]
        }).with_additional("id").do()
        
        session_chathistory = job_with_session_id['data']['Get']['IPersonaMessages']
        if isinstance(session_chathistory, list):
            for entry in session_chathistory:
                if 'chathistory' in entry:
                    chathistory_data = entry['chathistory']
                    if isinstance(chathistory_data, str) and chathistory_data:  
                        try:
                            entry['chathistory'] = ast.literal_eval(chathistory_data)
                        except (ValueError, SyntaxError) as e:
                            print(f"Error parsing chathistory for entry {entry}: {e}")
        return session_chathistory
    
    except Exception as e:
        print("Error fetching Sessions chats:", e)
        
 
