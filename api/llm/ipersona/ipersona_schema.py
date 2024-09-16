import weaviate, os
from dotenv import dotenv_values
import datetime
from dotenv import load_dotenv
load_dotenv("../../.env")

WEAVIATE_URL="https://z4crjyuqsr6sgo87nujlta.c0.us-east1.gcp.weaviate.cloud"
WEAVIATE_API_KEY="tHvAYZHC9Q8OzUXsL6wVFkhDViT0YKNKBwL9"
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
                    "name": "email", 
                    "dataType": ["string"], 
                    "indexInverted": True
                },
                {
                    "name": "userId", 
                    "dataType": ["string"]
                },
                {
                    "name": "sessionId", 
                    "dataType": ["string"]
                },
                {
                    "name": "fileName", 
                    "dataType": ["string"], 
                    "default": "null"
                },
                {
                    "name": "cvPath", 
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
            "class": "iPersonaSessionJob",
            "properties": [
                {
                    "name": "sessionId", 
                    "dataType": ["string"]
                },
                {
                    "name": "jbId", 
                    "dataType": ["string"]
                },
                {
                    "name": "jbPath", 
                    "dataType": ["string"], 
                    "default": "null"
                },
                {
                    "name": "persona",
                    "dataType": ["string"],  
                    "default": "null"
                },
                {
                    "name": "analysis",
                    "dataType": ["string"],  
                    "default": "null"
                },
                {
                    "name": "analysischat",
                    "dataType": ["string"],  
                    "default": "null"
                },
                {
                    "name": "interviewchat", 
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
        persona_session_job_exists = any(cls['class'] == "IPersonaSessionJob" for cls in existing_schema['classes'])
     
        if not persona_session_exists and not persona_session_job_exists:
            client.schema.create(schema)  
            uploaded_uuid = await Add_session_schema_data(data)
            print("Classes 'iPersonaSession' and 'iPersonaSessionJob' created successfully.")
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
        "email": data['email'],
        "userId": data['userId'], #'a82d3efe-0289-4acf-a93b-fcc768355e5b',
        "sessionId": data['sessionId'],        
        "fileName": data['fileName'],
        "cvPath": data['cvPath'],
        "createdAt": get_current_time(),
        "updatedAt": get_current_time()
        }

        ipersona_upload = client.data_object.create(
            data_object=ipersona_data,
            class_name="iPersonaSession"
        )
        
        return ipersona_upload
    except Exception as e:
        return f'Error: {str(e)}' 
    
    
async def Add_session_Job_schema_data(data):
    try:
        ipersona_data = {
        "sessionId": data['sessionId'], 
        "jbId": data['jbId'],
        "jbPath": data['jbPath'],
        "persona": data['persona'],
        "analysis": str(data['analysis']), 
        "analysischat": str(data['analysischat']),
        "interviewchat": str(data['interviewchat']),
        "createdAt": get_current_time(),
        "updatedAt": get_current_time()
        }

        ipersona_upload = client.data_object.create(
            data_object=ipersona_data,
            class_name="iPersonaSessionJob"
        )
        
        return ipersona_upload
    except Exception as e:
        return f'Error: {str(e)}' 

 
async def fetch_session(userId):
    try:
        sessions_with_user_id = client.query.get(
            class_name="iPersonaSession",
            properties=[
                "email",
                "sessionId",
                "cvPath",
                "fileName",
            ] 
        ).with_where({
            "path": ["userId"],
            "operator": "Equal",
            "valueString": userId 
        }).with_additional("id").do()
        
        length = len(sessions_with_user_id['data']['Get']['IPersonaSession'])
        index = length - 1
        result = sessions_with_user_id['data']['Get']['IPersonaSession'][index]
        data= {
            "all_data": sessions_with_user_id['data']['Get']['IPersonaSession'],
            "latest_data": result
        }
        return data
    except Exception as e:
        print("Error fetching Sessions:", e)
        

async def fetch_job(sessionId, jbId):
    print("Fetching job data:", jbId)
    try:
        job_with_session_id = client.query.get(
            class_name="iPersonaSessionJob",
            properties=[
                "sessionId",
                "jbId",
                "jbPath",
                "persona",
                "analysis", 
                "analysischat",
                "interviewchat"
                ]  
        ).with_where({
            "operator": "And", 
            "operands": [
                {
                    "path": ["sessionId"],
                    "operator": "Equal",
                    "valueString": sessionId
                },
                {
                    "path": ["jbId"],
                    "operator": "Equal",
                    "valueString": jbId
                }
            ]
        }).with_additional("id").do()
        
        length = len(job_with_session_id['data']['Get']['IPersonaSessionJob'])
        index = length - 1
        result = job_with_session_id['data']['Get']['IPersonaSessionJob'][index]
        
        return result
    except Exception as e:
        print("Error fetching Sessions:", e)
        

async def update_ipersona_data_new(data, fields_to_update):
    print("Updating data for ID:", data['id'])
    update_data = {}
    
    if 'persona' in fields_to_update:
        update_data['persona'] = str(data.get('persona', ''))
    if 'analysis' in fields_to_update:
        update_data['analysis'] = str(data.get('analysis', ''))
    if 'analysischat' in fields_to_update:
        update_data['analysischat'] = str(data.get('analysischat', ''))
    if 'interviewchat' in fields_to_update:
        update_data['interviewchat'] = str(data.get('interviewchat', ''))
    if 'jbId' in fields_to_update:
        update_data['jbId'] = str(data.get('jbId', ''))
    if 'jbPath' in fields_to_update:
        update_data['jbPath'] = str(data.get('jbPath', ''))
    
    try:
        result = client.data_object.update(
            uuid=data['id'],
            data_object=update_data,
            class_name='iPersonaSessionJob'
        )
        return True
    
    except Exception as e:
        return f'Error: {str(e)}'
