
from api.services.strapi_ipersona import IpersonaManager
import api.modules.ipersona_parrot_gpt as util


def calculate_time_limit(response):
    accumulated_message = ""
    for chunk in response:
        accumulated_message += chunk   
    timelimit =  util.interview_question_time_limit(accumulated_message)   
    return timelimit         
 

def step1_insert_message(data):
    sessionId =  data['user_session']['id'] 
    ipersona_manager = IpersonaManager(sessionId=sessionId, run_stage="dev")
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
        "metadata": {
            "createdBy": "parrot"
        }
    }

    ipersona_manager.insert_message(message_data)
    
def step2_insert_message(data, timelimit, accumulated_message, realtime_evaluation):
    sessionId =  data['user_session']['id'] 
    ipersona_manager = IpersonaManager(sessionId=sessionId, run_stage="dev")
    message = {
                "user_type": "assistant",
                "content_type": "question",
                "content": {
                    "time_taken": "null",
                    "time_limit":  timelimit.get("time_limit"),
                    "full_response": accumulated_message,
                    "realtime_evaluation": realtime_evaluation
                }
            }
    message_data = {
        "attributes": {
            "message": message,
        },
        "metadata": {
            "createdBy": "parrot"
        }
    }
    ipersona_manager.insert_message(message_data)


def step3_insert_message(data, realtime_evaluation):
    sessionId =  data['user_session']['id'] 
    ipersona_manager = IpersonaManager(sessionId=sessionId, run_stage="dev")
    message = {
                "user_type": "assistant",
                "content_type": "question",
                "content": {
                    "time_taken": "",
                    "time_limit":  "",
                    "full_response": "",
                    "realtime_evaluation": realtime_evaluation
                }
            }
    message_data = {
        "attributes": {
            "message": message,
        },
        "metadata": {
            "createdBy": "parrot"
        }
    }

    ipersona_manager.insert_message(message_data)
