import asyncio, os
import socketio, time
from openai import OpenAI
import assemblyai as aai

from concurrent.futures import ThreadPoolExecutor
from api import config
import api.modules.ipersona_parrot_gpt as util
import api.modules.ipersona_parrot_audio as audio
import api.llm.ipersona.ipersona_strapi as strapi
from api.llm.ipersona.ipersona_strapi_schemas import IpersonaSessionMessageSchema
import api.modules.ipersona_parrot_audio as audio


from api.utils.logger import LLPackerLogger

logger = LLPackerLogger(os.path.basename(__file__))
aai.settings.api_key = config.assemblyai.api_key


OPENAI_API_KEY = config.openai.api_key
client = OpenAI(api_key=OPENAI_API_KEY)

transcriber = None

sio = socketio.AsyncServer(cors_allowed_origins="*", async_mode="asgi")
socket_app = socketio.ASGIApp(sio)



@sio.on("initial connect")
async def connect(sid):
    print("####### Socket Connected #######")
    await sio.emit(
        "initial connect",
        {"message": "socket connection started"}, 
        room=sid)

@sio.on("disconnect")
async def disconnect(sid):
    print(f"Transcribe Client Disconnected: {sid}")
   
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


executor = ThreadPoolExecutor(max_workers=105)  

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

@sio.on("audio chat")
async def audio_endpoint(sid, data):
    try:
        start_time = time.time()        
        response = await audio.generate_interview_question(data)
        assistant_next_question = response.get("interview", "")

        #tasks = [synthesize_text(chunk) for chunk in assistant_next_question]
        accumulated_message = ""             

        tasks = []
        for chunk in assistant_next_question:
            accumulated_message += chunk
            
            while True:
                last_period = accumulated_message.rfind('.')
                last_question = accumulated_message.rfind('?')

                last_end_pos = max(last_period, last_question)
                
                if last_end_pos != -1:
                    complete_sentence = accumulated_message[:last_end_pos + 1]
                    await sio.emit("audio-single-text-chunk", complete_sentence, room=sid)
                    tasks.append(synthesize_text(complete_sentence))
                    
                    accumulated_message = accumulated_message[last_end_pos + 1:].strip()                        
                else:
                    break   
        
        
        await sio.emit("audio-single-text-chunk-done", room=sid)

        audio_chunks = await asyncio.gather(*tasks)

        for audio_data in audio_chunks:
            if isinstance(audio_data, dict) and 'error' in audio_data:
                print(f"Error: {audio_data['error']}")
                continue

            await sio.emit("audio-single-chunk", audio_data, room=sid)
       
    except Exception as e:
        print(f"Error processing audio: {e}")

    finally:
        message = 'over'
        await sio.emit("interview done", message, room=sid)
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Time taken for audio interview processing: {elapsed_time:.2f} seconds")


@sio.on("audio chat sentence")
async def audio_end_point(sid, data):
    print("audio socket response", data["response"])
    try:
        start_time = time.time()   
        global chat_count
        chat_count = 1  
        sessionId =  data['user_session']['id'] 
        realtime_evaluation = "null"
   
        ipersona_message = IpersonaSessionMessageSchema()
        session_chathistory = ipersona_message.filter_by_session_id(sessionId=sessionId, 
                                                                    nopp=True, 
                                                                    dataframe=False)

        chat = session_chathistory['count']       
            
        if chat != 0:  
            chat_total = session_chathistory['total']
            assistant_count = sum(1 for entry in chat_total if entry["user_type"] == "assistant")
            chat_count += assistant_count 
        else:
            pass        

        if(data['response']):
            strapi.step1_insert_message(data)
                 
        response = await audio.generate_interview_question(data) 
      
        
        if(response != 'None'):
            assistant_next_question = "" if response.get("interview") is None else response["interview"]       
            accumulated_message = ""              
            message = [
                {
                    "user_type": "assistant",
                    "content_type": "question",
                    "content": {
                        "time_taken": "null",
                        "time_limit":  "null",
                        "chunk_response": accumulated_message,
                        "full_response": "",
                        "realtime_evaluation": "null"
                    }
                }
            ]
            
            await sio.emit("audio chat sentence", message, room=sid)   
        
            timelimit = strapi.calculate_time_limit(response)
            message = [{
                        "content": {
                            "time_limit": timelimit.get("time_limit", "null"),
                        }
                    }]                    
            await sio.emit("audio_time_limit", message, room=sid)      
            
            for chunk in assistant_next_question:
                accumulated_message += chunk
                print("Chunk Message")
                print(chunk)  
                
                await sio.emit("audio-one-chunk", chunk, room=sid)

                end_time = time.time() 
                elapsed_time = end_time - start_time  
                print(f"Chunk Time taken: {elapsed_time:.2f} seconds")    
                
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
                                
                        await sio.emit("audio-single-chunk-sentence", complete_sentence, room=sid)
                        await sio.emit("audio chat sentence", message, room=sid)
                        
                            #-----------------------------------------------------------------#
                        # tasks = []
                        # for chunk in assistant_next_question:
                        #     await sio.emit("audio-single-chunk-sentence", complete_sentence, room=sid)
                        #     await sio.emit("audio chat sentence", message, room=sid)
                        #     tasks.append(synthesize_text(complete_sentence))
                        
                        # await sio.emit("audio-single-text-chunk-done", room=sid)

                        # audio_chunks = await asyncio.gather(*tasks)

                        # for audio_data in audio_chunks:
                        #     if isinstance(audio_data, dict) and 'error' in audio_data:
                        #         print(f"Error: {audio_data['error']}")
                        #         continue

                        #     await sio.emit("audio-single-chunk", audio_data, room=sid)
                            #-----------------------------------------------------------------#

                        accumulated_message = accumulated_message[last_end_pos + 1:].strip()
                        
                    else:
                        break   
            
            if(data['response']):
                start_time02 = time.time()  
                realtime_evaluation_response_json = audio.realtime_response_evaluation(data)
                realtime_evaluation = "null" if realtime_evaluation_response_json is None else realtime_evaluation_response_json.get("realtime_evaluation")
                logger.info(f"Realtime done {realtime_evaluation}")

                end_time02 = time.time() 
                elapsed_time02 = end_time02 - start_time02
                print(f"Realtime future exec Time taken: {elapsed_time02:.2f} seconds")
                message = [{
                    "content": {
                        "realtime_evaluation": realtime_evaluation,
                        "full_response": accumulated_message

                    }
                }]            
                await sio.emit("audio_realtime", message, room=sid)

        
        if chat_count < 9:
            strapi.step2_insert_message(data, timelimit, accumulated_message, realtime_evaluation)
            
        else:
            message = 'interview over'
            await sio.emit("interview done", message, room=sid)
            strapi.step3_insert_message(data, realtime_evaluation)
          
   
    except Exception as e:
        print(f'Error: {str(e)}')  
        
    finally:
        end_time = time.time() 
        elapsed_time = end_time - start_time  
        print(f"Time taken for audio interview processing: {elapsed_time:.2f} seconds")
    

@sio.on("interview chat")
async def interview_endpoint(sid, data):
    try:
        logger.info(f"Processing interview chat for session: {data['user_session']['id']}")
        
        start_time = time.time()
        global chat_count
        chat_count = 1  
        sessionId = data['user_session']['id']
        realtime_evaluation = "null"

        # Fetch session chat history
        ipersona_message = IpersonaSessionMessageSchema()
        session_chathistory = ipersona_message.filter_by_session_id(
            sessionId=sessionId, 
            nopp=True, 
            dataframe=False
        )

        chat = session_chathistory['count']

        if chat != 0:  
            chat_total = session_chathistory['total']
            assistant_count = sum(1 for entry in chat_total if entry["user_type"] == "assistant")
            chat_count += assistant_count
        else:
            logger.info(f"No chat history found for session ID: {sessionId}")

        # Insert the user's response if provided
        if data['response']:
            strapi.step1_insert_message(data)

        # Generate the next interview question
        response = await util.generate_interview_question(data)

        if response:
            assistant_next_question = response.get("interview", "")
            accumulated_message = ""

            # Emit the assistant's next question
            message = [
                {
                    "user_type": "assistant",
                    "content_type": "question",
                    "content": {
                        "time_taken": "null",
                        "time_limit": "null",
                        "chunk_response": accumulated_message,
                        "full_response": "",
                        "realtime_evaluation": "null"
                    }
                }
            ]
            await sio.emit("interview chat", message, room=sid)

            # Calculate and emit the time limit for the next question
            timelimit = strapi.calculate_time_limit(response)
            message = [{
                        "content": {
                            "time_limit": timelimit.get("time_limit", "null"),
                        }
                    }]
            await sio.emit("time_limit", message, room=sid)

            # Process and emit the assistant's next question in chunks
            for chunk in assistant_next_question:
                accumulated_message += chunk
                message = [{
                    "content": {
                        "chunk_response": chunk
                    }
                }]
                end_time = time.time()
                elapsed_time = end_time - start_time
                logger.info(f"Chunk emitted, time taken: {elapsed_time:.2f} seconds")

                await sio.emit("interview chat", message, room=sid)

            # Perform real-time response evaluation if applicable
            if data['response']:
                start_time02 = time.time()
                realtime_evaluation_response_json = util.realtime_response_evaluation(data)
                realtime_evaluation = "null" if realtime_evaluation_response_json is None else realtime_evaluation_response_json.get("realtime_evaluation")

                end_time02 = time.time()
                elapsed_time02 = end_time02 - start_time02
                logger.info(f"Realtime evaluation processed, time taken: {elapsed_time02:.2f} seconds")

                message = [{
                    "content": {
                        "realtime_evaluation": realtime_evaluation,
                        "full_response": accumulated_message
                    }
                }]
                await sio.emit("realtime", message, room=sid)

        # Insert the message or conclude the interview if the chat count exceeds the limit
        if chat_count < 9:
            strapi.step2_insert_message(data, timelimit, accumulated_message, realtime_evaluation)
        else:
            message = 'interview over'
            await sio.emit("interview done", message, room=sid)
            strapi.step3_insert_message(data, realtime_evaluation)

    except Exception as e:
        logger.error(f"Error processing interview chat for session {data['user_session']['id']}: {str(e)}", exc_info=True)
        await sio.emit("error", {"error": f"Error: {str(e)}"}, room=sid)

    finally:
        end_time = time.time()
        elapsed_time = end_time - start_time
        logger.info(f"Time taken for interview processing: {elapsed_time:.2f} seconds")


def get_socketio_app(fast_app):
    app = socketio.ASGIApp(
        socketio_server=sio,
        other_asgi_app=fast_app,
        socketio_path='/socket.io/'
    )
    return app

