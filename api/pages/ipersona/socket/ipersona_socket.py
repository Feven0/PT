import asyncio, os, json
import socketio, time
from openai import OpenAI
import assemblyai as aai

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

transcriber = None

sio = socketio.AsyncServer(cors_allowed_origins="*", 
                           async_mode="asgi",
                           logger=False,
                           engineio_logger=False)
socket_app = socketio.ASGIApp(sio)

@sio.event
async def connect(sid, environ):
    print(f"####### Socket Connected with SID: {sid} #######")
    
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
    
@sio.on("disconnect")
async def disconnect(sid):
    logger.info(f"Client disconnected with SID: {sid}")
    print("work testing")
 
# assembly streaming
@sio.on("audio transcribe")
async def audio_endpoint(sid, data):
    loop = asyncio.get_event_loop()
    audioblob = data['audioblob']
    global transcriber

    def on_open(session_opened: aai.RealtimeSessionOpened):
        print("Session ID:", session_opened.session_id)

    def on_data(transcript: aai.RealtimeTranscript):
        if transcript.text:
            if isinstance(transcript, aai.RealtimeFinalTranscript):
                print("Final Transcription:", transcript.text)
                asyncio.run_coroutine_threadsafe(
                    sio.emit("audio transcribe", transcript.text), loop
                )
                
            else:
                print("Interim Transcription:", transcript.text)

    def on_error(error: aai.RealtimeError):
        print("An error occurred:", error)

    def on_close():
        print("Closing Session")
        global transcriber
        transcriber = None

    if transcriber is None:
        transcriber = aai.RealtimeTranscriber(
            sample_rate=16000,
            on_data=on_data,  
            on_error=on_error,
            on_open=on_open,
            on_close=on_close
        )
        transcriber.connect()

    try:
        transcriber.stream(audioblob)
    except Exception as e:
        print(f"Error in audio streaming: {str(e)}")

# executor = ThreadPoolExecutor(max_workers=105)  

async def synthesize_text(text):
    print("Received text for synthesis:", text)
    try:
        response = client.audio.speech.create(
            model="tts-1",
            voice="alloy",
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
                await sio.emit("error", {"error": error_msg}, room=sid)
                return
        except Exception as session_id_error:
            logger.error(f"Error extracting session ID: {str(session_id_error)}")
            await sio.emit("error", {"error": "Failed to identify session"}, room=sid)
            return
        
        #-----------------------------------------------------------------------------------#
        try:
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
                        all_questions = len(data['user_session']['attributes']['attributes']['template_questions'])
                    
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


        # # Insert the user's response if provided
        # if data['response']:
        #     strapi.step1_insert_message(run_stage, data)

        # Insert the user's response if provided
        try:
            if data.get('response'):
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
                await sio.emit("error", {"error": "Failed to generate next question"}, room=sid)
                return
            
        except Exception as generate_error:
            logger.error(f"Error generating interview question: {str(generate_error)}")
            await sio.emit("error", {"error": f"Question generation failed: {str(generate_error)}"}, room=sid)
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
            
            await sio.emit("audio chat sentence", message, room=sid)  
            
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
                                
                        await sio.emit("audio chat sentence", message, room=sid)
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
            await sio.emit("audio_time_limit", message, room=sid)      
               
            audio_chunks = await asyncio.gather(*tasks)
            
            for audio_data in audio_chunks:
                if isinstance(audio_data, dict) and 'error' in audio_data:
                    print(f"Error: {audio_data['error']}")
                    continue
                
                message = [{
                        "content": {
                            "audio_data": audio_data,
                        }
                    }]                    
                await sio.emit("audio_base64_chunks", message, room=sid) 
                
                await sio.emit("audio-single-chunk", audio_data, room=sid)
                
            await sio.emit("audio-single-text-chunk-done", room=sid)

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
                await sio.emit("audio_realtime", message, room=sid)  
             
       
        # Insert the message or conclude the interview if the chat count exceeds the limit
        if chat_count < total_questions:
            final = 'false'
            strapi.step2_insert_message(
                run_stage, 
                data, 
                timelimit, 
                accumulated_message, 
                realtime_evaluation, 
                final,
                sessionId)
        else:
            message = 'interview over'
            final = 'true'
            if response.get("status") is not None:
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
            await sio.emit("last_audio_realtime_evaluation", message, room=sid)          

            await sio.emit("interview done", message, room=sid)
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
    try:
        print('+++*****************************************000000000000******************************************+++')
        logger.info(f"Received interview request with template_id: {data.get('template_id')}")
        
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
        try:
            session = await sio.get_session(sid)
        except Exception as session_error:
            logger.error(f"Failed to get socket session: {str(session_error)}")
            return {"error": f"Retrieval failed for session:, {sid}"}
        
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
            run_stage = session.get('run_stage', None)  
            if run_stage is None:
                logger.warn(f"Run stage not found in session for sid: {sid}, using default")
                run_stage = 'dev'  # Default to production if not specified
            else:
                logger.info(f"Run stage retrieved: {run_stage}")
        except Exception as stage_error:
            logger.error(f"Error retrieving run stage: {str(stage_error)}")
            run_stage = 'dev'  # Default to production if error occurs
        
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
                    print('***************************************************===1****************************************************')
                    print(f"Total questions derived from template: {total_questions}")
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
                    logger.error(f"Error fetching session: {str(session_fetch_error)}")
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
            if data.get('response'):
                try:
                    print("ballls and filreee------===============================")
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
                    await sio.emit("interview chat", message, room=sid)

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
                    await sio.emit("time_limit", message, room=sid)

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
                            
                    for chunk in assistant_next_question:
                        try:
                            accumulated_message += chunk
                            message = [{
                                "content": {
                                    "chunk_response": chunk
                                }
                            }]
                            await sio.emit("interview chat", message, room=sid)
                            
                        except Exception as chunk_error:
                            logger.error(f"Error processing chunk: {str(chunk_error)}")
                            # Continue with next chunk despite error
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
                            await sio.emit("realtime", message, room=sid)

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
            print("((((((((((((((((((((((((((((((((((((((((()))))))))))))))))))))))))))))))))))))))))")
            if chat_count < total_questions + 1:
                final = 'false'
                try:
                    print("=================0::::0===================", sessionId)

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
                    await sio.emit("interview done", message, room=sid)
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
                            await sio.emit("last_realtime_evaluation", message, room=sid)
                        
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
    )
    return app

