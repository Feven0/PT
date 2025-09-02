import asyncio, os, json
import socketio, time
from openai import OpenAI
import assemblyai as aai
from typing import Dict, Any

from api import config
import api.modules.ipersona_parrot_gpt as util
import api.llm.ipersona.ipersona_strapi as strapi
from api.llm.ipersona.ipersona_strapi_schemas import (
    IpersonaSessionMessageSchema, 
    IpersonaSessionSchema, 
    IpersonaTinderTemplateSchema,
    IpersonaChallengeDocumentSchema
)

import urllib.parse  
from api.utils.logger import LLPackerLogger

logger = LLPackerLogger(os.path.basename(__file__))


aai.settings.api_key = config.assemblyai.api_key


OPENAI_API_KEY = config.openai.api_key
client = OpenAI(api_key=OPENAI_API_KEY)

# Improved transcriber management - track per session
transcribers: Dict[str, Any] = {}

sio = socketio.AsyncServer(cors_allowed_origins="*", 
                           async_mode="asgi",
                           logger=False,
                           engineio_logger=False)


socket_app = socketio.ASGIApp(sio)

@sio.event
async def connect(sid, environ):
    print(f"####### Socket Connected with SID: {sid} #######")
    await sio.emit("initial connect", {"message": "socket connection started"}, room=sid)
    
    query_string = environ.get('QUERY_STRING', '')
    print(f"Query string: {query_string}")
    
    asgi_scope = environ.get('asgi.scope', {})
    scope_query = asgi_scope.get('query_string', b'').decode('utf-8')
    print(f"ASGI scope query string: {scope_query}")
    
    parsed_query = urllib.parse.parse_qs(query_string)
    run_stage = parsed_query.get('run_stage', [''])[0]
    print(f"Parsed run_stage: {run_stage}")
        
    # Also try the session method
    try:
        await sio.save_session(sid, {'run_stage': run_stage})
        session = await sio.get_session(sid)
        print(f"Session after save: {session}")
    except Exception as e:
        print(f"Session error: {e}")
    
@sio.on("initial connect")
async def connect(sid):
    print("####### Socket Connected #######")
    await sio.emit(
        "initial connect",
        {"message": "socket connection started"}, 
        room=sid)
    
@sio.on("disconnect")
async def disconnect(sid):
    logger.info(f"Client disconnected with SID: {sid}")
    # Clean up any active transcribers for this session
    existing = transcribers.pop(sid, None)
    if existing is not None:
        try:
            if hasattr(existing, 'close') and callable(getattr(existing, 'close')):
                existing.close()
            elif hasattr(existing, 'disconnect') and callable(getattr(existing, 'disconnect')):
                existing.disconnect()
            elif hasattr(existing, 'terminate') and callable(getattr(existing, 'terminate')):
                existing.terminate()
            logger.info(f"Session closed cleanly on disconnect (sid={sid})")
        except Exception as e:
            logger.warn(f"Error while closing session on disconnect (sid={sid}): {e}")
 
# Improved assembly streaming with proper session management
@sio.on("audio transcribe")
async def audio_endpoint(sid, data):
    """Handle audio transcribe event with improved session management."""
    loop = asyncio.get_event_loop()
    audioblob = data.get('audioblob')

    # Log incoming audio data
    if audioblob:
        blob_length = len(audioblob) if hasattr(audioblob, '__len__') else 'unknown'
        logger.info(f"[AUDIO RECEIVED] sid={sid}, audioblob length={blob_length}, type={type(audioblob)}")
    else:
        logger.info(f"[AUDIO RECEIVED] sid={sid}, audioblob=None (stop signal)")

    # Treat None audioblob as an explicit stop signal from client
    if audioblob is None:
        logger.info(f"Stop requested by client (sid={sid}). Closing session if active...")
        existing = transcribers.pop(sid, None)
        if existing is not None:
            try:
                if hasattr(existing, 'close') and callable(getattr(existing, 'close')):
                    existing.close()
                elif hasattr(existing, 'disconnect') and callable(getattr(existing, 'disconnect')):
                    existing.disconnect()
                elif hasattr(existing, 'terminate') and callable(getattr(existing, 'terminate')):
                    existing.terminate()
                logger.info(f"Session closed cleanly after stop (sid={sid})")
            except Exception as e:
                logger.warn(f"Error while closing session on stop (sid={sid}): {e}")
        else:
            logger.info(f"No active session to close on stop (sid={sid})")
        return

    # Normalize audio bytes
    try:
        if hasattr(audioblob, 'buffer'):
            audio_bytes = bytes(audioblob)
        elif isinstance(audioblob, list):
            audio_bytes = bytes(audioblob)
        elif isinstance(audioblob, (bytes, bytearray, memoryview)):
            audio_bytes = bytes(audioblob)
        else:
            audio_bytes = audioblob
    except Exception:
        # Fallback: try best effort conversion
        audio_bytes = audioblob

    # Log normalized audio data
    normalized_length = len(audio_bytes) if hasattr(audio_bytes, '__len__') else 'unknown'
    logger.info(f"[AUDIO NORMALIZED] sid={sid}, normalized_length={normalized_length}")

    def on_open(session_opened: aai.RealtimeSessionOpened):
        logger.info(f"Session opened: {session_opened.session_id} (sid={sid})")

    def on_data(transcript: aai.RealtimeTranscript):
        try:
            if not transcript.text:
                return
            # Preserve legacy behavior: emit bare string only on final
            if isinstance(transcript, aai.RealtimeFinalTranscript):
                logger.info(f"Final transcript (sid={sid}): {transcript.text}")
                logger.info(f"[SOCKET EMIT] Sending final transcript to sid={sid}: '{transcript.text}'")
                asyncio.run_coroutine_threadsafe(
                    sio.emit("audio transcribe", transcript.text, room=sid),
                    loop
                )
                logger.info(f"[SOCKET EMIT] Final transcript sent successfully to sid={sid}")
                
            else:
                # Interim log (lighter)
                logger.info(f"Interim transcript (sid={sid}): {transcript.text}")
        except Exception as emit_err:
            logger.error(f"Emit error: {emit_err}")

    def on_error(error: aai.RealtimeError):
        logger.error(f"An error occurred: {error}")

    def on_close():
        logger.info(f"Closing Session (sid={sid})")
        transcribers.pop(sid, None)

        asyncio.run_coroutine_threadsafe(
            sio.emit("transcription_complete", {
                "status": "completed",
                "message": "Audio transcription finished"
            }, room=sid), loop
        )
        logger.info(f"[SOCKET EMIT] transcription_complete sent successfully to sid={sid}")

    # Create a session-scoped transcriber if missing
    if sid not in transcribers or transcribers.get(sid) is None:
        logger.info(f"Creating new transcriber for sid={sid}")
        transcribers[sid] = aai.RealtimeTranscriber(
            sample_rate=16000,
            on_data=on_data,
            on_error=on_error,
            on_open=on_open,
            on_close=on_close
        )
        transcribers[sid].connect()
        logger.info(f"Transcriber connected for sid={sid}")

    # Stream audio chunk for this sid
    try:
        logger.info(f"[AUDIO STREAM] Streaming audio to transcriber for sid={sid}, length={normalized_length}")
        transcribers[sid].stream(audio_bytes)
        logger.info(f"[AUDIO STREAM] Audio streamed successfully for sid={sid}")
    except Exception as e:
        logger.error(f"Error in audio streaming for sid={sid}: {str(e)}")

# executor = ThreadPoolExecutor(max_workers=105)  

async def synthesize_text(text):
    print("Received text for synthesis:", text)
    try:
        response = client.audio.speech.create(
            model="tts-1",
            voice="nova",
            input=text
        )

        audio_data = response.read()

        if len(audio_data) == 0 or len(audio_data) < 500:  
            return {"error": "Received insufficient audio data."}

        return audio_data  

    except Exception as e:
        return {"error": str(e)}

# method to save audio chat to database
# TODO: integrate with audio chat function
@sio.on("audio chat sentence")
async def audio_end_point(sid, data):
    session = await sio.get_session(sid)        
        
    run_stage = session.get('run_stage', None)  

    if run_stage is None:
        print(f"Run stage not found in session for sid: {sid}")
    else:
        print(f"Run stage retrieved: {run_stage}")
        
    logger.info("audio socket response", data["response"], data['user_session']['id'])
    try:
        chat_count = 1  
        sessionId = data['user_session']['id']
        realtime_evaluation = "null"
        accumulated_message = ""
        full_accumulated_message = ""
        template_id = data.get('template_id', "null")
        challenge_id = data.get('challenge_id', "null")
        total_questions = 0

         # Get session ID with error handling
        try:
            if isinstance(data.get('user_session'), dict) and 'id' in data['user_session']:
                sessionId = data['user_session']['id']
                logger.info(f"Processing interview chat for session ID: {sessionId}")
            else:
                error_msg = "Invalid user_session format: missing ID"
                logger.error(error_msg)
                logger.info(f"[SOCKET EMIT] Sending error to sid={sid}: {error_msg}")
                await sio.emit("error", {"error": error_msg}, room=sid)
                logger.info(f"[SOCKET EMIT] Error sent successfully to sid={sid}")
                return
        except Exception as session_id_error:
            logger.error(f"Error extracting session ID: {str(session_id_error)}")
            logger.info(f"[SOCKET EMIT] Sending error to sid={sid}: Failed to identify session")
            await sio.emit("error", {"error": "Failed to identify session"}, room=sid)
            logger.info(f"[SOCKET EMIT] Error sent successfully to sid={sid}")
            return
        
        #-----------------------------------------------------------------------------------#
        try:
            logger.info("=====================================-------------------------------------=============")
            logger.info(data)
            logger.info(data.get('template'))
            logger.info("=====================================-------------------------------------=============")

            if data.get('template'):
                    try:
                        template_id = data.get('template_id')
                        if not template_id:
                            logger.warn("Template flag set but no template_id provided")
                            return {"error": "Template ID is required"}
                            
                        ipersona_template = IpersonaTinderTemplateSchema()
                        saved_template = ipersona_template.get_tinder_template_id(
                            templateId=template_id, 
                            return_object=True, 
                            nopp=True, 
                            dataframe=False
                        )
                        
                        if not saved_template:
                            logger.warn(f"No template found for template ID: {template_id}")
                            return {"error": f"Template not found: {template_id}"}
                            
                        data['user_session'] = saved_template
                        collection = data['user_session']['attributes']['attributes']['template_questions']
                        question_counts = {section['sectionType']: len(section['questions']) for section in collection}
                        total_questions = sum(question_counts.values())
                    
                    except Exception as template_error:
                        logger.error(f"Error retrieving template: {str(template_error)}")
                        return {"error": f"Template retrieval failed: {str(template_error)}"}
                    
            else: 
                ipersona_user = IpersonaSessionSchema(run_stage=run_stage)
                session_fetched = ipersona_user.get_session_by_id(
                    sessionId=sessionId, 
                    nopp=True, 
                    dataframe=False
                )
              
                data['user_session'] = session_fetched
                all_questions = data['user_session']['attributes']['attributes']
                collection = all_questions.get('generated_questions') or all_questions.get('challenge_questions')
           
                question_counts = {section['sectionType']: len(section['questions']) for section in collection}
                total_questions = sum(question_counts.values())
                
                if not session_fetched:
                    logger.warn(f"No session found for session ID: {sessionId}")
                    return f"No session found for session ID: {sessionId}"
                
        except Exception as data_prep_error:
            logger.error(f"Error in data preparation in Audio Socket: {str(data_prep_error)}")
            return {"error": f"Data preparation failed: {str(data_prep_error)}"}
        #------------------------------------------------------------------------------------#

        
        # Fetch session chat history
        try:
            ipersona_message = IpersonaSessionMessageSchema(run_stage=run_stage)
            session_chathistory = ipersona_message.filter_by_session_id(
                sessionId=sessionId, 
                nopp=True, 
                dataframe=False
            )

            if not session_chathistory:
                logger.warn(f"Failed to retrieve chat history for session {sessionId}")
                chat = 0
            else:
                chat = session_chathistory.get('count', 0)

            if chat != 0:  
                try:
                    chat_total = session_chathistory.get('total', [])
                    assistant_count = sum(1 for entry in chat_total if entry.get("user_type") == "assistant")
                    chat_count += assistant_count
                except Exception as count_error:
                    logger.error(f"Error counting assistant messages: {str(count_error)}")
                    # Continue with default chat_count if count fails
            else:
                logger.info(f"No chat history found for session ID: {sessionId}")
        except Exception as history_error:
            logger.error(f"Error retrieving chat history: {str(history_error)}")


        # Insert the user's response if provided
        try:
            if data.get('response') and data.get('resume') is False:
                try:
                    strapi.step1_insert_message(
                        run_stage, 
                        data, 
                        sessionId)
                except Exception as insert_error:
                    logger.error(f"Failed to insert user message: {str(insert_error)}")
                    # Continue despite insertion failure
            else:
                logger.info("No user response to insert")
        except Exception as response_error:
            logger.error(f"Error processing user response: {str(response_error)}")

                 
        try:
            response = await util.generate_interview_question(
                run_stage, 
                data, 
                total_questions, 
                template_id, 
                challenge_id, 
                sessionId)
            
            if not response:
                logger.error("Failed to generate interview question: empty response")
                logger.info(f"[SOCKET EMIT] Sending error to sid={sid}: Failed to generate next question")
                await sio.emit("error", {"error": "Failed to generate next question"}, room=sid)
                logger.info(f"[SOCKET EMIT] Error sent successfully to sid={sid}")
                return
            
        except Exception as generate_error:
            logger.error(f"Error generating interview question: {str(generate_error)}")
            logger.info(f"[SOCKET EMIT] Sending error to sid={sid}: Question generation failed")
            await sio.emit("error", {"error": f"Question generation failed: {str(generate_error)}"}, room=sid)
            logger.info(f"[SOCKET EMIT] Error sent successfully to sid={sid}")
            return
             
        if response.get("interview") is not None:

            assistant_next_question = "" if response.get("interview") is None else response["interview"]       
            message = [
                        {
                            "user_type": "assistant",
                            "content_type": "question",
                            "content": {
                                "time_taken": "null",  
                                "time_limit": "null",
                                "chunk_response": accumulated_message,
                                "full_response": "",
                                "final": "false",
                                "realtime_evaluation": "null"
                            }
                        }
                    ]
            
            logger.info(f"[SOCKET EMIT] Sending initial audio chat sentence to sid={sid}: {message}")
            await sio.emit("audio chat sentence", message, room=sid)  
            logger.info(f"[SOCKET EMIT] Initial audio chat sentence sent successfully to sid={sid}")
            
            tasks = []
            for chunk in assistant_next_question:
                accumulated_message += chunk 
                full_accumulated_message += chunk            
                while True:
                    last_period = accumulated_message.rfind('.')
                    last_question = accumulated_message.rfind('?')

                    last_end_pos = max(last_period, last_question)
                    
                    if last_end_pos != -1:
                        complete_sentence = accumulated_message[:last_end_pos + 1]
                        message = [{
                            "content": {
                                "chunk_response": complete_sentence
                            }
                        }]  
                                
                        logger.info(f"[SOCKET EMIT] Sending chunk response to sid={sid}: '{complete_sentence}'")
                        await sio.emit("audio chat sentence", message, room=sid)
                        logger.info(f"[SOCKET EMIT] Chunk response sent successfully to sid={sid}")
                        tasks.append(synthesize_text(complete_sentence))
                    
                        accumulated_message = accumulated_message[last_end_pos + 1:].strip()                        
                    else:
                        break   
                    
            timelimit = strapi.calculate_time_limit(response)
            message = [{
                        "content": {
                            "time_limit": timelimit.get("time_limit", "null"),
                        }
                    }]                    
            logger.info(f"[SOCKET EMIT] Sending time limit to sid={sid}: {timelimit.get('time_limit', 'null')}")
            await sio.emit("audio_time_limit", message, room=sid)      
            logger.info(f"[SOCKET EMIT] Time limit sent successfully to sid={sid}")
               
            audio_chunks = await asyncio.gather(*tasks)
            
            for i, audio_data in enumerate(audio_chunks):
                if isinstance(audio_data, dict) and 'error' in audio_data:
                    print(f"Error: {audio_data['error']}")
                    continue
                
                # Log blob length instead of full content
                blob_length = len(audio_data) if audio_data else 0
                logger.info(f"[SOCKET EMIT] Sending audio_base64_chunks to sid={sid}: chunk_{i+1}, blob_length={blob_length} bytes")
                
                message = [{
                        "content": {
                            "audio_data": audio_data,
                        }
                    }]                    
                await sio.emit("audio_base64_chunks", message, room=sid) 
                logger.info(f"[SOCKET EMIT] audio_base64_chunks sent successfully to sid={sid}: chunk_{i+1}")
                
                logger.info(f"[SOCKET EMIT] Sending audio-single-chunk to sid={sid}: chunk_{i+1}, blob_length={blob_length} bytes")
                await sio.emit("audio-single-chunk", audio_data, room=sid)
                logger.info(f"[SOCKET EMIT] audio-single-chunk sent successfully to sid={sid}: chunk_{i+1}")
                
            logger.info(f"[SOCKET EMIT] Sending audio-single-text-chunk-done to sid={sid}")
            await sio.emit("audio-single-text-chunk-done", room=sid)
            logger.info(f"[SOCKET EMIT] audio-single-text-chunk-done sent successfully to sid={sid}")

            # Perform real-time response evaluation if applicable
            if data['response'] is not [None, ""]:
                type = 'job_interview_config'
                realtime_evaluation_response_json = util.realtime_response_evaluation(
                                run_stage, 
                                data, 
                                sessionId, 
                                type)
                realtime_evaluation = "null" if realtime_evaluation_response_json is None else realtime_evaluation_response_json.get("realtime_evaluation")
                logger.success(f"Realtime evaluation is: {realtime_evaluation}")
            
                message = [{
                    "content": {
                        "realtime_evaluation": realtime_evaluation,
                        "full_response": accumulated_message
                    }
                }]
                status = "start"
                await sio.emit("realtime_status", status, room=sid)  
                logger.info(f"[SOCKET EMIT] Sending audio_realtime to sid={sid}: {realtime_evaluation}")
                await sio.emit("audio_realtime", message, room=sid)  
                logger.info(f"[SOCKET EMIT] audio_realtime sent successfully to sid={sid}")
                status = "end"
                await sio.emit("realtime_status", status, room=sid)  
             
       
        # Insert the message or conclude the interview if the chat count exceeds the limit
        if chat_count < total_questions + 1:
            print("Full MESSAGE -=====")
            print(full_accumulated_message)
            print("Full MESSAGE -=====")
            final = 'false'
            strapi.step2_insert_message(
                run_stage, 
                data, 
                timelimit, 
                full_accumulated_message, 
                realtime_evaluation, 
                final,
                sessionId)
        else:
            message = 'interview over'
            logger.info(f"[SOCKET EMIT] Sending interview done to sid={sid}: {message}")
            await sio.emit("interview done", message, room=sid)
            logger.info(f"[SOCKET EMIT] interview done sent successfully to sid={sid}")

            final = 'true'
            if response.get("status") is not None:
                try:
                    message = [{
                            "user_type": "assistant",
                            "content_type": "question",
                            "content": {
                                "time_taken": "null",
                                "time_limit": "null",                        
                                "chunk_response": '',
                                "full_response": accumulated_message,
                                "final": "true",
                                "realtime_evaluation": response.get("realtime", "null")
                            }
                        }]
                    logger.info(f"[SOCKET EMIT] Sending last_audio_realtime_evaluation to sid={sid}")
                    await sio.emit("last_audio_realtime_evaluation", message, room=sid)   
                    logger.info(f"[SOCKET EMIT] last_audio_realtime_evaluation sent successfully to sid={sid}")

                except Exception as final_emit_error:
                            logger.error(f"Failed to emit final evaluation: {str(final_emit_error)}")
            # strapi.step3_insert_message(data, realtime_evaluation, final)
   
    except Exception as e:
        logger.error(f'Error: {str(e)}')  
        

# handle for text to text chat
@sio.on("interview chat")
async def interview_endpoint(sid, data):
    """
    Handle interview socket.io endpoint with comprehensive error handling.
    
    Args:
        sid (str): Socket.io session ID
        data (dict): Interview data containing user session and response
        
    Returns:
        None: Responses are sent via socket.io events
    """
    logger.info(f"Received interview request with template_id-=-: {data.get('template_id')}, job: {data.get('job_profile_id', None)}")
    try:
        logger.info(f"Received interview request with template_id-=-: {data.get('challenge_id')}, job: {data.get('job_profile_id', None)}")
        
        # Validate input data
        if not isinstance(data, dict):
            error_msg = "Invalid data format: expected a dictionary"
            logger.error(error_msg)
            await sio.emit("error", {"error": error_msg}, room=sid)
            return
            
        if 'user_session' not in data:
            error_msg = "Missing required field: user_session"
            logger.error(error_msg)
            await sio.emit("error", {"error": error_msg}, room=sid)
            return
        
        # Initialize variables
        # try:
        #     session = await sio.get_session(sid)
        # except Exception as session_error:
        #     logger.error(f"Failed to get socket session: {str(session_error)}")
        #     return {"error": f"Retrieval failed for session:, {sid}"}
        
        chat_count = 1  
        sessionId = None
        realtime_evaluation = "null"
        accumulated_message = ""     
        template_id = data.get('template_id', "null")
        challenge_id = data.get('challenge_id', "null")
        timelimit = {"time_limit": "null"}
        total_questions = 0
        
        # Get run stage from session
        try:
            session = await sio.get_session(sid)        
            run_stage = session.get('run_stage', None)  
            if run_stage is None:
                logger.warn(f"Run stage not found in session for sid: {sid}, using default")
                run_stage = 'democms'  # Default to production if not specified
            else:
                logger.info(f"Run stage retrieved: {run_stage}")
        except Exception as stage_error:
            logger.error(f"Error retrieving run stage: {str(stage_error)}")
            run_stage = 'democms'  # Default to production if error occurs
        
        # Get session ID with error handling
        try:
            if isinstance(data.get('user_session'), dict) and 'id' in data['user_session']:
                sessionId = data['user_session']['id']
                logger.info(f"Processing interview chat for session ID: {sessionId}")
            else:
                error_msg = "Invalid user_session format: missing ID"
                logger.error(error_msg)
                return {"error": error_msg}
        except Exception as session_id_error:
            logger.error(f"Error extracting session ID: {str(session_id_error)}")
            return {"error": f"Failed to identify session: {sid}" }
        
        #-----------------------------------------------------------------------------------#
        # Handle template-based or session-based interviews

        try:
            if data.get('template'):
                print("Template flag is set, processing template-based interview")
                try:
                    template_id = data.get('template_id')
                    if not template_id:
                        logger.warn("Template flag set but no template_id provided")
                        return {"error": "Template ID is required"}
                        
                    ipersona_template = IpersonaTinderTemplateSchema()
                    saved_template = ipersona_template.get_tinder_template_id(
                        templateId=template_id, 
                        return_object=True, 
                        nopp=True, 
                        dataframe=False
                    )
                    
                    if not saved_template:
                        logger.warn(f"No template found for template ID: {template_id}")
                        return {"error": f"Template not found: {template_id}"}
                        
                    data['user_session'] = saved_template
                    collection = data['user_session']['attributes']['attributes']['template_questions']
                    question_counts = {section['sectionType']: len(section['questions']) for section in collection}
                    total_questions = sum(question_counts.values())
                except Exception as template_error:
                    logger.error(f"Error retrieving template: {str(template_error)}")
                    return {"error": f"Template retrieval failed: {str(template_error)}"}
 
            else:    
                try:
                    # Fetch session by ID if user_session is already a dict
                    ipersona_user = IpersonaSessionSchema(run_stage=run_stage)
                    session_fetched = ipersona_user.get_session_by_id(
                        sessionId=sessionId, 
                        nopp=True, 
                        dataframe=False
                    )
                    
                    if not session_fetched:
                        logger.warn(f"No session found for session ID: {sessionId}")
                        return {"error": f"Session not found: {sessionId}"}
                        
                    data['user_session'] = session_fetched
                    all_questions = data['user_session']['attributes']['attributes']
                    collection = all_questions.get('generated_questions') or all_questions.get('challenge_questions')
                    collection = json.loads(collection) if isinstance(collection, str) else collection

                    question_counts = {section['sectionType']: len(section['questions']) for section in collection}
                    total_questions = sum(question_counts.values())

                except Exception as session_fetch_error:
                    logger.error(f"Error generated session: {str(session_fetch_error)}")
                    return {"error": f"Session retrieval failed: {str(session_fetch_error)}"}
                
        except Exception as data_prep_error:
            logger.error(f"Error in data preparation: {str(data_prep_error)}")
            return {"error": f"Data preparation failed: {str(data_prep_error)}"}
        #------------------------------------------------------------------------------------#
       
        # Fetch session chat history
        try:
            ipersona_message = IpersonaSessionMessageSchema(run_stage=run_stage)
            session_chathistory = ipersona_message.filter_by_session_id(
                sessionId=sessionId, 
                nopp=True, 
                dataframe=False
            )

            if not session_chathistory:
                logger.warn(f"Failed to retrieve chat history for session {sessionId}")
                chat = 0
            else:
                chat = session_chathistory.get('count', 0)

            if chat != 0:  
                try:
                    chat_total = session_chathistory.get('total', [])
                    assistant_count = sum(1 for entry in chat_total if entry.get("user_type") == "assistant")
                    chat_count += assistant_count
                except Exception as count_error:
                    logger.error(f"Error counting assistant messages: {str(count_error)}")
            else:
                logger.info(f"No chat history found for session ID: {sessionId}")

        except Exception as history_error:
            logger.error(f"Error retrieving chat history: {str(history_error)}")
            # Continue without chat history

        # Insert the user's response if provided
        try:
            if data.get('response') and data.get('resume') is False:
                try:
                    strapi.step1_insert_message(
                        run_stage, 
                        data, 
                        sessionId)
                except Exception as insert_error:
                    logger.error(f"Failed to insert user message: {str(insert_error)}")
                    # Continue despite insertion failure
            else:
                logger.info("No user response to insert")
        except Exception as response_error:
            logger.error(f"Error processing user response: {str(response_error)}")
            # Continue despite error
            
        # Generate the next interview question
        try:
            response = await util.generate_interview_question(
                run_stage, 
                data, 
                total_questions, 
                template_id, 
                challenge_id, 
                sessionId)
            if not response:
                logger.error("Failed to generate interview question: empty response")
                return {"error": "Failed to generate next question"}
        except Exception as generate_error:
            logger.error(f"Error generating interview question: {str(generate_error)}")
            return {"error": f"Question generation failed: {str(generate_error)}"}
       
        # Process and emit the assistant's response
        try:
            if response.get("interview") is not None:
                assistant_next_question = response.get("interview", "")
                
                # Prepare initial message
                try:
                    message = [
                        {
                            "user_type": "assistant",
                            "content_type": "question",
                            "content": {
                                "time_taken": "null",  
                                "time_limit": "null",
                                "chunk_response": accumulated_message,
                                "full_response": "",
                                "final": "false",
                                "realtime_evaluation": "null"
                            }
                        }
                    ]
                    logger.info(f"[SOCKET EMIT] Sending initial interview chat to sid={sid}: {message}")
                    await sio.emit("interview chat", message, room=sid)
                    logger.info(f"[SOCKET EMIT] Initial interview chat sent successfully to sid={sid}")

                except Exception as initial_emit_error:
                    logger.error(f"Failed to emit initial message: {str(initial_emit_error)}")
                    # Continue despite emission failure

                # Calculate and emit time limit
                try:
                    timelimit = strapi.calculate_time_limit(response)
                    message = [{
                                "content": {
                                    "time_limit": timelimit.get("time_limit", "null"),
                                }
                            }]
                    logger.info(f"[SOCKET EMIT] Sending time limit to sid={sid}: {timelimit.get('time_limit', 'null')}")
                    await sio.emit("time_limit", message, room=sid)
                    logger.info(f"[SOCKET EMIT] Time limit sent successfully to sid={sid}")

                except Exception as timelimit_error:
                    logger.error(f"Failed to calculate or emit time limit: {str(timelimit_error)}")
                    timelimit = {"time_limit": "null"}
                    # Continue despite time limit failure

                # Process and emit the assistant's message in chunks
                
                is_generator = hasattr(assistant_next_question, '__iter__') and hasattr(assistant_next_question, '__next__')
               
                try:
                    if not is_generator:
                        logger.warn("Expected list for assistant_next_question, converting to list")
                        if isinstance(assistant_next_question, str):
                            assistant_next_question = [assistant_next_question]
                        else:
                            assistant_next_question = [str(assistant_next_question)]
                            
                    for i, chunk in enumerate(assistant_next_question):
                        try:
                            accumulated_message += chunk
                            message = [{
                                "content": {
                                    "chunk_response": chunk
                                }
                            }]
                            logger.info(f"[SOCKET EMIT] Sending interview chat chunk to sid={sid}: chunk_{i+1}, content='{chunk}'")
                            await sio.emit("interview chat", message, room=sid)
                            logger.info(f"[SOCKET EMIT] Interview chat chunk sent successfully to sid={sid}: chunk_{i+1}")
                            
                        except Exception as chunk_error:
                            logger.error(f"Error processing chunk: {str(chunk_error)}")
                            # Continue with next chunk despite error
                    logger.success("All chunks processed successfully", accumulated_message)
                except Exception as chunks_error:
                    logger.error(f"Error processing message chunks: {str(chunks_error)}")
                    # Continue despite chunks processing failure
            
                # Perform real-time response evaluation if applicable
                try:
                    if data.get('response') not in [None, "", []]:
                        try:
                            type = 'job_interview_config'
                            realtime_evaluation_response_json = util.realtime_response_evaluation(
                                run_stage, 
                                data, 
                                sessionId, 
                                type)
                            realtime_evaluation = "null" if realtime_evaluation_response_json is None else realtime_evaluation_response_json.get("realtime_evaluation")
                        except Exception as eval_compute_error:
                            logger.error(f"Failed to compute realtime evaluation: {str(eval_compute_error)}")
                            realtime_evaluation = "null"
                        
                        try:
                            message = [{
                                "content": {
                                    "realtime_evaluation": realtime_evaluation,
                                    "full_response": accumulated_message
                                }
                            }]

                            status = "started"
                            await sio.emit("realtime_status", status, room=sid)  
                            logger.info(f"[SOCKET EMIT] Sending realtime evaluation to sid={sid}: {realtime_evaluation}")
                            await sio.emit("realtime", message, room=sid)
                            logger.info(f"[SOCKET EMIT] Realtime evaluation sent successfully to sid={sid}")
                            status = "finished"
                            await sio.emit("realtime_status", status, room=sid)  

                        except Exception as eval_emit_error:
                            logger.error(f"Failed to emit realtime evaluation: {str(eval_emit_error)}")

                except Exception as realtime_error:
                    logger.error(f"Error in realtime evaluation: {str(realtime_error)}")

            else:
                logger.warn("No interview question generated in the response")
        except Exception as response_process_error:
            logger.error(f"Error processing response: {str(response_process_error)}")
            return {"error": f"Error processing response: {str(response_process_error)}"}
                
        # Insert the message or conclude the interview
        try:
            if chat_count < total_questions + 1:
                final = 'false'
                try:
                    strapi.step2_insert_message(
                        run_stage, 
                        data, 
                        timelimit, 
                        accumulated_message, 
                        realtime_evaluation, 
                        final,
                        sessionId)
                except Exception as insert_message_error:
                    logger.error(f"Failed to insert assistant message: {str(insert_message_error)}")

            else:
                # Handle interview conclusion
                try:
                    message = 'interview over'
                    logger.info(f"[SOCKET EMIT] Sending interview done to sid={sid}: {message}")
                    await sio.emit("interview done", message, room=sid)
                    logger.info(f"[SOCKET EMIT] Interview done sent successfully to sid={sid}")
                    final = 'true'
                    temp_id = data.get('template_id') if data.get('template_id') is not None else "null"
                    challenge_id = data.get('challenge_id') if data.get('challenge_id') is not None else "null"

                    if response.get("status") is not None:
                        try:
                            message = [{
                                "user_type": "assistant",
                                "content_type": "question",
                                "content": {
                                    "time_taken": "null",
                                    "time_limit": "null",                        
                                    "chunk_response": '',
                                    "full_response": accumulated_message,
                                    "final": "true",
                                    "realtime_evaluation": response.get("realtime", "null")
                                }
                            }]
                            logger.info(f"[SOCKET EMIT] Sending last_realtime_evaluation to sid={sid}")
                            await sio.emit("last_realtime_evaluation", message, room=sid)
                            logger.info(f"[SOCKET EMIT] last_realtime_evaluation sent successfully to sid={sid}")
                        
                        except Exception as final_emit_error:
                            logger.error(f"Failed to emit final evaluation: {str(final_emit_error)}")

                except Exception as conclusion_error:
                    logger.error(f"Error concluding interview: {str(conclusion_error)}")
                    return f"Error concluding interview: {str(conclusion_error)}"
                
        except Exception as final_step_error:
            logger.error(f"Error in final processing step: {str(final_step_error)}")
            return  {"error": "Error in final processing step"}

    except Exception as e:
        error_message = f"Error processing interview chat: {str(e)}"
        logger.error(error_message, exc_info=True)
        return error_message

def get_socketio_app(fast_app):
    app = socketio.ASGIApp(
        socketio_server=sio,
        other_asgi_app=fast_app,
        socketio_path='/socket.io/'
        # transports=["websocket"]
    )
    return app

