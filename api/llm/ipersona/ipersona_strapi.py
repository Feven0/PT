import os
import api.modules.ipersona_parrot_gpt as util
from api.llm.ipersona.ipersona_strapi_schemas import IpersonaSessionMessageSchema
from api.utils.logger import LLPackerLogger
logger = LLPackerLogger(os.path.basename(__file__))

def calculate_time_limit(response):
    try:
        accumulated_message = ""
        for chunk in response:
            accumulated_message += chunk   
        timelimit =  util.interview_question_time_limit(accumulated_message)   
        return timelimit      
     
    except Exception as e:
        logger.error(f"Process failed: ${str(e)}")
        return {'error': str(e)}  
 

def step1_insert_message(run_stage, data, sessionId):
    try:
        # sessionId =  data['user_session']['id']      
        
        message_data = {
            "attributes": {
                "message": {
                    "user_type": "candidate",
                    "content_type": "answer",
                    "content": {
                        "response": data['response'],
                        "time_taken": data['time_taken'],
                        "realtime_evaluation": "null"
                    }
                },
            },
            "i_persona_session": sessionId 
        }

        ipersona_message = IpersonaSessionMessageSchema(run_stage=run_stage)
        ipersona_message.save_message(params=message_data, nopp=True, dataframe=False)
        
    except Exception as e:
        logger.error(f"Saving to db failed: ${str(e)}")
        return {'error': str(e)}
    

def step2_insert_message(
        run_stage, 
        data, 
        timelimit, 
        accumulated_message, 
        realtime_evaluation, 
        final, 
        sessionId):
    try:
        # sessionId =  data['user_session']['id'] 
             
        message = {
                    "user_type": "assistant",
                    "content_type": "question",
                    "content": {
                        "time_taken": "null",
                        "time_limit":  timelimit.get("time_limit"),
                        "full_response": accumulated_message,
                        "final": final,
                        "realtime_evaluation": realtime_evaluation
                    }
                }
        message_data = {
            "attributes": {
                "message": message,
            },
            "i_persona_session": sessionId
        }
        ipersona_message = IpersonaSessionMessageSchema(run_stage=run_stage)
        ipersona_message.save_message(params=message_data, nopp=True, dataframe=False)
        
    except Exception as e:
        logger.error(f"Saving to db failed: ${str(e)}")
        return {'error': str(e)}

def step3_insert_message(run_stage, realtime_evaluation, final, sessionId):
    try:
     
        message = {
                    "user_type": "assistant",
                    "content_type": "question",
                    "content": {
                        "time_taken": "",
                        "time_limit":  "",
                        "full_response": "",
                        "final": final,
                        "realtime_evaluation": realtime_evaluation
                    }
                }
        message_data = {
            "attributes": {
                "message": message,
            },
            "i_persona_session": sessionId
        }

        ipersona_message = IpersonaSessionMessageSchema(run_stage=run_stage)
        ipersona_message.save_message(params=message_data, nopp=True, dataframe=False)
        
    except Exception as e:
        logger.error(f"Saving to db failed: ${str(e)}")
        return {'error': str(e)}


def insert_message(message, sessionId):
    try: 
        print('Saving message to DB...')

        message_data = {
            "attributes": {
                "message": message,
            },
            "i_persona_session": sessionId,
            "metadata": {
                "template": False,
                "generate": False,
                "external": True
            }
        }
        ipersona_message = IpersonaSessionMessageSchema()
        chat_saved = ipersona_message.save_message(params=message_data, nopp=True, dataframe=False)
     
        return True 

    except Exception as e:
        logger.error(f"Saving to DB failed: {str(e)}")
        return False  # Ensure a False value is returned in case of failure


def save_messages_to_db(data, sessionId):
    try:
        saved = []
        errors = []

        if isinstance(data, dict):
            for key, value in data.items():
                message = f"{key}: {value}"
                if insert_message(message, sessionId):
                    print('one')
                    saved.append(message)
                else:
                    print('two')
                    errors.append(message)
        elif isinstance(data, list):
            for item in data:
                if insert_message(item, sessionId):
                    print('three')
                    saved.append(item)
                else:
                    print('four')
                    errors.append(item)
        else:
            logger.error("Invalid data format. Must be a dictionary or list.")
            return {'error': 'Invalid data format'}

        # Check if all messages were saved successfully
        if not errors:
            return saved
        
        # Partial success or complete failure
        return saved

    except Exception as e:
        logger.error(f"Error in saving messages to DB: {str(e)}")
        return {'error': str(e)}
