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
 

def step1_insert_message(run_stage, data, sessionId, audio_url=None):
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
                        "realtime_evaluation": "null",
                        "url": audio_url
                    }
                },
            },
            "i_persona_session": sessionId 
        }

        ipersona_message = IpersonaSessionMessageSchema(run_stage=run_stage)
        saved_message = ipersona_message.save_message(params=message_data, nopp=True, dataframe=False)
        # Return the message ID for background S3 upload
        # The response structure is: {'data': {'id': '18442', 'attributes': {...}}}
        if saved_message and isinstance(saved_message, dict):
            if 'id' in saved_message:
                message_id = saved_message['id']
                logger.info(f"[STEP2_INSERT][DEBUG] Message saved with ID: {message_id}")
                return message_id
            elif 'data' in saved_message and isinstance(saved_message['data'], dict) and 'id' in saved_message['data']:
                message_id = saved_message['data']['id']
                logger.info(f"[STEP2_INSERT][DEBUG] Message saved with ID: {message_id}")
                return message_id
            else:
                logger.warn(f"[STEP2_INSERT][DEBUG] Could not extract message ID from saved message structure: {saved_message}")
                return None
        else:
            logger.warn(f"[STEP2_INSERT][DEBUG] Could not extract message ID from saved message: {saved_message}")
            return None
            
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
        sessionId,
        audio_url=None):
    try:
        # sessionId =  data['user_session']['id'] 
        logger.info(f"[STEP2_INSERT][DEBUG] ===== STEP2 INSERT MESSAGE =====")
        logger.info(f"[STEP2_INSERT][DEBUG] sessionId: {sessionId}")
        logger.info(f"[STEP2_INSERT][DEBUG] audio_url: {audio_url}")
        logger.info(f"[STEP2_INSERT][DEBUG] accumulated_message length: {len(accumulated_message) if accumulated_message else 0}")
             
        message = {
                    "user_type": "assistant",
                    "content_type": "question",
                    "content": {
                        "time_taken": "null",
                        "time_limit":  timelimit.get("time_limit"),
                        "full_response": accumulated_message,
                        "final": final,
                        "realtime_evaluation": realtime_evaluation,
                        "url": audio_url
                    }
                }
        logger.info(f"[STEP2_INSERT][DEBUG] Message content with URL: {message['content']}")
        logger.info(f"[STEP2_INSERT][DEBUG] ===== STEP2 INSERT MESSAGE END =====")
        message_data = {
            "attributes": {
                "message": message,
            },
            "i_persona_session": sessionId
        }
        ipersona_message = IpersonaSessionMessageSchema(run_stage=run_stage)
        saved_message = ipersona_message.save_message(params=message_data, nopp=True, dataframe=False)
        
        # Return the message ID for background S3 upload
        # The response structure is: {'data': {'id': '18442', 'attributes': {...}}}
        if saved_message and isinstance(saved_message, dict):
            if 'id' in saved_message:
                message_id = saved_message['id']
                logger.info(f"[STEP2_INSERT][DEBUG] Message saved with ID: {message_id}")
                return message_id
            elif 'data' in saved_message and isinstance(saved_message['data'], dict) and 'id' in saved_message['data']:
                message_id = saved_message['data']['id']
                logger.info(f"[STEP2_INSERT][DEBUG] Message saved with ID: {message_id}")
                return message_id
            else:
                logger.warn(f"[STEP2_INSERT][DEBUG] Could not extract message ID from saved message structure: {saved_message}")
                return None
        else:
            logger.warn(f"[STEP2_INSERT][DEBUG] Could not extract message ID from saved message: {saved_message}")
            return None
        
    except Exception as e:
        logger.error(f"Saving to db failed: ${str(e)}")
        return {'error': str(e)}

def update_message_with_audio_url(message_id, audio_url):
    """Update a specific message with the audio URL."""
    try:        
        # Get the current message using the correct schema
        from api.llm.ipersona.ipersona_strapi_schemas import IpersonaSessionMessageSchema
        message_schema = IpersonaSessionMessageSchema()
        current_message = message_schema.get_session_msg_by_id(
            sessionId=message_id,
            nopp=True,
            dataframe=False
        )
    
        if not current_message:
            logger.error(f"[UPDATE_AUDIO_URL] Message {message_id} not found")
            return False
        
        # Get current message structure from the correct path
        current_attributes = current_message.get("data", {}).get("attributes", {})
        current_message_data = current_attributes.get("attributes", {}).get("message", {})

        if isinstance(current_message_data, str):
            try:
                import json
                current_message_data = json.loads(current_message_data)
            except:
                current_message_data = {}
        
        # Get current content and add the audio URL
        current_content = current_message_data.get('content', {})
        if isinstance(current_content, str):
            try:
                import json
                current_content = json.loads(current_content)
            except:
                current_content = {}
        
        # Add the audio URL to the existing content
        current_content['url'] = audio_url
        # Update the message structure with the new content
        updated_message_data = current_message_data.copy()
        updated_message_data['content'] = current_content
        
        # Update the message using save_or_update_object with correct structure
        update_data = {
            "i_persona_message_id": message_id,
            "attributes": {
               "message": updated_message_data
            }
        }
        
        updated_message = message_schema.update_session_message(
            params=update_data,
            nopp=True,
            dataframe=False
        )
        
        if updated_message:
            logger.info(f"[UPDATE_AUDIO_URL] Successfully updated message {message_id} with audio URL")
            return True
        else:
            logger.error(f"[UPDATE_AUDIO_URL] Failed to update message {message_id}")
            return False
            
    except Exception as e:
        logger.error(f"[UPDATE_AUDIO_URL] Error updating message {message_id} with audio URL: {str(e)}")
        return False

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

