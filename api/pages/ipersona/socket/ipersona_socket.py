import socketio, time
# import api.pages.ipersona.socket.ipersona_parrot_gpt as util
# import api.pages.ipersona.socket.ipersona_parrot_audio as audio
# import api.pages.ipersona.socket.ipersona_parrot_audio_copy as copy
import api.modules.ipersona_parrot_gpt as util
import api.modules.ipersona_parrot_audio as audio
import api.modules.ipersona_parrot_audio_copy as copy
import api.llm.ipersona.ipersona_strapi as strapi
from api.services.strapi_ipersona import IpersonaManager
from openai import OpenAI
from fastapi.responses import StreamingResponse, JSONResponse
import assemblyai as aai
from api import config
import asyncio
import io
aai.settings.api_key = "436bc16c4e474f47ae116cbe17041966"

sio = socketio.AsyncServer(cors_allowed_origins="*", async_mode="asgi")
socket_app = socketio.ASGIApp(sio)

OPENAI_API_KEY = config.openai.api_key

sio = socketio.AsyncServer(cors_allowed_origins="*", async_mode="asgi")
socket_app = socketio.ASGIApp(sio)

OPENAI_API_KEY = config.openai.api_key

client = OpenAI(api_key=OPENAI_API_KEY)


transcriber = None

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

import asyncio
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=105)  

async def synthesize_text(text):
    print("Received text for synthesis:")
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
        response = await copy.generate_interview_question(data)
        assistant_next_question = response.get("interview", "")

        #tasks = [synthesize_text(chunk) for chunk in assistant_next_question]

        tasks = []
        for chunk in assistant_next_question:
            await sio.emit("audio-single-text-chunk", chunk, room=sid)
            tasks.append(synthesize_text(chunk))
        
        await sio.emit("audio-single-text-chunk-done", room=sid)

        audio_chunks = await asyncio.gather(*tasks)

        for audio_data in audio_chunks:
            if isinstance(audio_data, dict) and 'error' in audio_data:
                print(f"Error: {audio_data['error']}")
                continue

            await sio.emit("audio-single-chunk", audio_data, room=sid)
       
        ## Optional
        # valid_audio_chunks = [chunk for chunk in audio_chunks if not isinstance(chunk, dict) or 'error' not in chunk]

        # # Concatenate all audio chunks then pass it
        # final_audio_data = b''.join(valid_audio_chunks)
        # await sio.emit("audio-single-chunk", audio_chunks, room=sid)

    except Exception as e:
        print(f"Error processing audio: {e}")

    finally:
        message = 'over'
        await sio.emit("interview done", message, room=sid)
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Time taken for audio interview processing: {elapsed_time:.2f} seconds")


@sio.on("audio double chunk")
async def audio_endpoint(sid, data):
    try:
        start_time = time.time()        
        response = await copy.generate_interview_question(data)
        assistant_next_question = "" if response.get("interview") is None else response["interview"]
         
        accumulated_message = ""  
        accumulated_tokens = []  
        token_chunk_size = 20 

        for chunk in assistant_next_question:  
            accumulated_message += chunk
            # Emit the 1-token chunk through the socket
            await sio.emit("audio-double-single-chunk", chunk, room=sid)

            tokens = chunk.split()  
            accumulated_tokens.extend(tokens)

            while len(accumulated_tokens) >= token_chunk_size:
                chunk_to_emit = " ".join(accumulated_tokens[:token_chunk_size])
                print(f"Token Chunk: {chunk_to_emit}")
                # Emit the 20-token chunk through the socket
                await sio.emit("audio-double-ten-chunks", chunk_to_emit, room=sid)

                accumulated_tokens = accumulated_tokens[token_chunk_size:]       

        if accumulated_tokens:
            chunk_to_emit = " ".join(accumulated_tokens)
            print(f"Remaining Tokens Chunk: {chunk_to_emit}")
            await sio.emit("audio-double-ten-chunks", chunk_to_emit, room=sid)

        await sio.emit("audio double chunk", accumulated_message, room=sid)
        
    except Exception as e:
        print(f'Error: {str(e)}')


@sio.on("audio chat sentence")
async def audio_end_point(sid, data):
    print("audio socket response", data["response"])
    try:
        start_time = time.time()   
        global chat_count
        chat_count = 1  
        sessionId =  data['user_session']['id'] 
        realtime_evaluation = "null"
   
        ipersona_manager = IpersonaManager(sessionId=sessionId, run_stage="dev")
        session_chathistory = ipersona_manager.get_messages()

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

                        accumulated_message = accumulated_message[last_end_pos + 1:].strip()
                    else:
                        break   
            
            if(data['response']):
                start_time02 = time.time()  
                realtime_evaluation_response_json = audio.realtime_response_evaluation(data)
                realtime_evaluation = "null" if realtime_evaluation_response_json is None else realtime_evaluation_response_json.get("realtime_evaluation")
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
    print("interview_session-data", type(data['user_session']), data['user_session']['id'] )
    try:
        start_time = time.time()
        global chat_count
        chat_count = 1  
        sessionId =  data['user_session']['id'] 
        realtime_evaluation = "null"
   
        ipersona_manager = IpersonaManager(sessionId=sessionId, run_stage="dev")
        session_chathistory = ipersona_manager.get_messages()

        chat = session_chathistory['count']       
            
        if chat != 0:  
            chat_total = session_chathistory['total']
            assistant_count = sum(1 for entry in chat_total if entry["user_type"] == "assistant")
            chat_count += assistant_count 
        else:
            pass        

        if(data['response']):
            strapi.step1_insert_message(data)

        response = await util.generate_interview_question(data)  
        
        print("generate_question_response")
        print(response)         

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
            
            await sio.emit("interview chat", message, room=sid)   
        
            timelimit = strapi.calculate_time_limit(response)
            message = [{
                        "content": {
                            "time_limit": timelimit.get("time_limit", "null"),
                        }
                    }]
                    
            await sio.emit("time_limit", message, room=sid)      
            
            for chunk in assistant_next_question:
                accumulated_message += chunk     
                message = [{
                    "content": {
                        "chunk_response": chunk
                    }
                }]     
                end_time = time.time() 
                elapsed_time = end_time - start_time  
                print(f"Chunk Time taken: {elapsed_time:.2f} seconds")

                await sio.emit("interview chat", message, room=sid) 
                
            print('marchel', accumulated_message, type(accumulated_message), accumulated_message != "", accumulated_message != 'None')
            
            if(data['response']):
                start_time02 = time.time()  
                realtime_evaluation_response_json = util.realtime_response_evaluation(data)
                realtime_evaluation = "null" if realtime_evaluation_response_json is None else realtime_evaluation_response_json.get("realtime_evaluation")
                end_time02 = time.time() 
                elapsed_time02 = end_time02 - start_time02
                print(f"Realtime future exec Time taken: {elapsed_time02:.2f} seconds")
                message = [{
                    "content": {
                        "realtime_evaluation": realtime_evaluation,
                        "full_response": accumulated_message

                    }
                }]            
                await sio.emit("realtime", message, room=sid)

        
        if chat_count < 9:
            strapi.step2_insert_message(data, timelimit, accumulated_message, realtime_evaluation)
            
        else:
            message = 'interview over'
            await sio.emit("interview done", message, room=sid)
            strapi.step3_insert_message(data, realtime_evaluation)

     
    except Exception as e:
        return f'Error: {str(e)}'
        
    finally:
        end_time = time.time() 
        elapsed_time = end_time - start_time  
        print(f"Time taken for interview processing: {elapsed_time:.2f} seconds")


def get_socketio_app(fast_app):
    app = socketio.ASGIApp(
        socketio_server=sio,
        other_asgi_app=fast_app,
        socketio_path='/socket.io/'
    )
    return app

