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
 

def step1_insert_message(data):
    try:
        sessionId =  data['user_session']['id']      
        
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

        ipersona_message = IpersonaSessionMessageSchema()
        ipersona_message.save_message(params=message_data, nopp=True, dataframe=False)
        
    except Exception as e:
        logger.error(f"Saving to db failed: ${str(e)}")
        return {'error': str(e)}
    
def step2_insert_message(data, timelimit, accumulated_message, realtime_evaluation):
    try:
        sessionId =  data['user_session']['id'] 
        message = {
                    "user_type": "assistant",
                    "content_type": "question",
                    "content": {
                        "time_taken": "null",
                        "time_limit":  timelimit.get("time_limit"),
                        "full_response": accumulated_message,
                        "final": data['final'],
                        "realtime_evaluation": realtime_evaluation
                    }
                }
        message_data = {
            "attributes": {
                "message": message,
            },
            "i_persona_session": sessionId
        }
        ipersona_message = IpersonaSessionMessageSchema()
        ipersona_message.save_message(params=message_data, nopp=True, dataframe=False)
        
    except Exception as e:
        logger.error(f"Saving to db failed: ${str(e)}")
        return {'error': str(e)}

def step3_insert_message(data, realtime_evaluation):
    try:
        sessionId =  data['user_session']['id'] 
        message = {
                    "user_type": "assistant",
                    "content_type": "question",
                    "content": {
                        "time_taken": "",
                        "time_limit":  "",
                        "full_response": "",
                        "final": data['final'],
                        "realtime_evaluation": realtime_evaluation
                    }
                }
        message_data = {
            "attributes": {
                "message": message,
            },
            "i_persona_session": sessionId
        }

        ipersona_message = IpersonaSessionMessageSchema()
        ipersona_message.save_message(params=message_data, nopp=True, dataframe=False)
        
    except Exception as e:
        logger.error(f"Saving to db failed: ${str(e)}")
        return {'error': str(e)}
