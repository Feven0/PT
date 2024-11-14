import socketio, ast, time
import api.pages.ipersona.socket.ipersona_parrot_gpt as util
import api.modules.ipersona_parrot_audio as audio
import api.llm.ipersona.ipersona_strapi as strapi
import api.llm.ipersona.ipersona_prisma as prisma
import api.llm.ipersona.ipersona_gpt as gpt
from openai import OpenAI
import assemblyai as aai
from api import config
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
from api.services.strapi_ipersona import IpersonaManager


aai.settings.api_key = "436bc16c4e474f47ae116cbe17041966"

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
    global transcriber
    global transcription
    transcription = None
    
    if transcriber:
        # Close the transcriber when the client disconnects
        transcriber.close()
        transcriber = None
        print(f"Socket Session closed for SID: {sid}")
        
def enzo(txt, data):
    list_transcription = []
    list_transcription.append(txt)
    # response = await util.fetch_interview_question(transcription, list_transcription)
    response = audio.generate_interview_question(txt, list_transcription, data)  
    assistant_next_question = "" if response.get("interview") is None else response["interview"]
    accumulated_message = ""
    for chunk in assistant_next_question:
        accumulated_message += chunk        
        print("Chunk Message")
        print(chunk)  
    # await sio.emit("audio transcribe",  response)
    print("talk about these")
    print(accumulated_message)
        
        
# Socket.IO event for handling incoming audio data
@sio.on("audio transcribe")
async def audio_endpoint(sid, data):
    global transcriber
    # user_data = data['all']
    audioblob = data['audioblob']
    
    if transcriber is None:
        # Define callbacks for AssemblyAI
        def on_open(session_opened: aai.RealtimeSessionOpened):
            print("Session ID:", session_opened.session_id)

        def on_data(transcript: aai.RealtimeTranscript):
            if not transcript.text:
                return

            if isinstance(transcript, aai.RealtimeFinalTranscript):
                print(transcript.text)
                enzo(transcript.text, data)
    
            else:
                print(transcript.text)

        def on_error(error: aai.RealtimeError):
            print("AssemblyAI Error:", error)

        def on_close():
            print("AssemblyAI Session Closed")

        try:
            transcriber = aai.RealtimeTranscriber(
                sample_rate=16000,
                on_data=on_data,
                on_error=on_error,
                on_open=on_open,
                on_close=on_close
            )
            transcriber.connect()

        except Exception as e:
            print(f"Error while starting transcriber: {str(e)}")
            return

    try:
        transcriber.stream(audioblob)
        # await sio.emit("audio transcribe",  transcription)
       

    except Exception as e:
        print(f"Error in audio streaming: {str(e)}")
        return
            
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
                
            if(accumulated_message != ""):
                timelimit =  util.interview_question_time_limit(accumulated_message)            
            
                message = [{
                    "content": {
                        "time_limit": timelimit.get("time_limit", "null"),
                        "full_response": accumulated_message,
                    }
                }]
                
                await sio.emit("time_limit", message, room=sid)
            
            if(data['response']):
                start_time02 = time.time()  
                realtime_evaluation_response_json = util.realtime_response_evaluation(data)
                realtime_evaluation = "null" if realtime_evaluation_response_json is None else realtime_evaluation_response_json.get("realtime_evaluation")
                end_time02 = time.time() 
                elapsed_time02 = end_time02 - start_time02
                print(f"Realtime future exec Time taken: {elapsed_time02:.2f} seconds")
                message = [{
                    "content": {
                        "realtime_evaluation": realtime_evaluation
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
        
        
@sio.on("audio chat")
async def audio_endpoint(sid, data):
    try:
        start_time = time.time()
        response = await util.generate_interview_question(data)
 
        assistant_next_question = "null" if response.get("interview") is None else response["interview"].get("interview_question")
        realtime_evaluation = "null" if response.get("realtime") is None else response["realtime"].get("realtime_evaluation")
        interview_evaluation = "null" if response.get("overall") is None else response["overall"].get("overall_evaluation")
        interview_evaluation_metrics = "null" if response.get("metrics") is None else response["metrics"].get("evaluation_metrics")

        if realtime_evaluation is not None:
            content_type = "question_feedback"
            complete = False
        elif interview_evaluation is not None:
            content_type = "overall_feedback"
            complete = True
        else:
            content_type = "question"
            complete = False

        message = [
            {
                "user_type": "assistant",
                "content_type": content_type,
                "complete": complete,
                "content": {
                    "time_taken": "null",
                    "response": assistant_next_question,
                    "realtime_evaluation": realtime_evaluation,
                    "interview_evaluation": interview_evaluation,
                    "interview_evaluation_metrics": interview_evaluation_metrics
                }
            }
        ]
 
        await sio.emit("audio chat", message, room=sid) 

     
    except Exception as e:
        return f'Error: {str(e)}'
    
        
    finally:
        end_time = time.time() 
        elapsed_time = end_time - start_time  
        print(f"Time taken for interview processing: {elapsed_time:.2f} seconds")


# @sio.on("audio chat")
# async def audio_endpoint(sid, data):
#     print("That is not what I am saying")
#     try:
#         start_time = time.time()        
#         response = await util.generate_interview_question(data)               
 
#         assistant_next_question = "" if response.get("interview") is None else response["interview"]   
#         accumulated_message = "" 
         
#         for chunk in assistant_next_question:
#             accumulated_message += chunk
#             print("Chunk Message")
#             print(chunk)  
#             end_time = time.time() 
#             elapsed_time = end_time - start_time  
#             print(f"Chunk Time taken: {elapsed_time:.2f} seconds")    
             
#             while True:
#                 last_period = accumulated_message.rfind('.')
#                 last_question = accumulated_message.rfind('?')

#                 last_end_pos = max(last_period, last_question)
                
#                 if last_end_pos != -1:
#                     complete_sentence = accumulated_message[:last_end_pos + 1]
                    
#                     await sio.emit("audio chat", complete_sentence, room=sid)
                    
#                     accumulated_message = accumulated_message[last_end_pos + 1:].strip()
#                 else:
#                     break
            
   
#     except Exception as e:
#         print(f'Error: {str(e)}')  
        
#     finally:
#         end_time = time.time() 
#         elapsed_time = end_time - start_time  
#         print(f"Time taken for audio interview processing: {elapsed_time:.2f} seconds")



# @sio.on("audio chat")
# async def audio_endpoint(sid, data):
#     print("-audiointerview-data", type(data['user_session']), data['user_session']['id'])
#     try:
#         start_time = time.time()
        
#         response = await util.generate_interview_question(data)

#         for chunk in response:
#             print(chunk)  
 
#         assistant_next_question = "null" if response.get("interview") is None else response["interview"].get("interview_question")
#         realtime_evaluation = "null" if response.get("realtime") is None else response["realtime"].get("realtime_evaluation")
#         interview_evaluation = "null" if response.get("overall") is None else response["overall"].get("overall_evaluation")
#         interview_evaluation_metrics = "null" if response.get("metrics") is None else response["metrics"].get("evaluation_metrics")

#         if realtime_evaluation is not None:
#             content_type = "question_feedback"
#             complete = False
#         elif chat_count == 8:
#             content_type = "question_feedback"
#             complete = True
#         elif interview_evaluation is not None:
#             content_type = "overall_feedback"
#             complete = True
#         else:
#             content_type = "question"
#             complete = False

#         message = [
#             {
#                 "user_type": "assistant",
#                 "content_type": content_type,
#                 "content": {
#                     "time_taken": "null",
#                     "response": assistant_next_question,
#                     "realtime_evaluation": realtime_evaluation,
#                     "interview_evaluation": interview_evaluation,
#                     "interview_evaluation_metrics": interview_evaluation_metrics
#                 }
#             }
#         ]
                           

#         await sio.emit("audio chat", message, room=sid) 

#     except Exception as e:
#         return f'Error: {str(e)}'
    
        
#     finally:
#         end_time = time.time() 
#         elapsed_time = end_time - start_time  
#         print(f"Time taken for interview processing: {elapsed_time:.2f} seconds")


def get_socketio_app(fast_app):
    app = socketio.ASGIApp(
        socketio_server=sio,
        other_asgi_app=fast_app,
        socketio_path='/socket.io/'
    )
    return app

