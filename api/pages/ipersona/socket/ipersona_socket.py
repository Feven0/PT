import socketio, ast, time
import api.modules.ipersona_parrot_gpt as util
import api.llm.ipersona.ipersona_schema as db
import api.llm.ipersona.ipersona_prisma as prisma
import api.llm.ipersona.ipersona_gpt as gpt
from openai import OpenAI
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed


sio = socketio.AsyncServer(cors_allowed_origins="*", async_mode="asgi")
socket_app = socketio.ASGIApp(sio)

OPENAI_API_KEY = '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'

client = OpenAI(api_key=OPENAI_API_KEY)

@sio.on("initial connect")
async def connect(sid, data):
    print("####### Socket Connected #######")
    await sio.emit(
        "initial connect",
        {"message": "socket connection started"}, 
        room=sid)


@sio.on("disconnect")
async def disconnect(sid):
    print("Client Disconnected: " + " " + str(sid))
    
            
@sio.on("interview chat")
async def interview_endpoint(sid, data):
    print("interview_session-data", type(data['user_session']))
    try:
        start_time = time.time()
        global chat_count
        chat_count = 1  
        # chat = await prisma.fetch_chat_history(data['user_session']['id'])
        # if len(chat) != 0:  
        #     chat = chat[0].chathistory
        #     assistant_count = sum(1 for entry in chat if entry["user_type"] == "assistant")
        #     chat_count += assistant_count 
        #     print("Number of assistant entries:", chat_count)
        # else:
        #     pass        

        # if(data['response']):
        #     chathistory = [{
        #         "user_type": "candidate",
        #         "content_type": "answer",
        #         "complete": False,
        #         "content": {
        #             "response": data['response'],
        #             "time_taken": data['time_taken'],
        #             "realtime_evaluation": "null"
        #         }
        #     }]
        #     # await db.Add_Interview_History(sessionId, chathistory)
        #     status = False
        #     # await prisma.create_chat(sessionId, chathistory, status)

        response = await util.generate_interview_question(data)               
 
        assistant_next_question = "" if response.get("interview") is None else response["interview"]
        # assistant_next_question = "null" if response.get("interview") is None else response["interview"].get("interview_question")
        # realtime_evaluation = "" if response.get("realtime") is None else response["realtime"].get("realtime_evaluation")
        # interview_evaluation = "" if response.get("overall") is None else response["overall"].get("overall_evaluation")
        # interview_evaluation_metrics = "" if response.get("metrics") is None else response["metrics"].get("evaluation_metrics")
        
        # print("interview+evaluation")
        # print(interview_evaluation)
        # print("^^^^^^^^^^^^^^^^^^^^^^^^^^")
        # print("interview+eval+metrics")
        # print(interview_evaluation_metrics)
        
        accumulated_message = ""  
        
        # if realtime_evaluation is not None:
        #     content_type = "question_feedback"
        #     complete = False
        # elif chat_count == 8:
        #     content_type = "question_feedback"
        #     complete = True
        # elif interview_evaluation is not None:
        #     content_type = "overall_feedback"
        #     complete = True
        # else:
        #     content_type = "question"
        #     complete = False

        message = [
            {
                "user_type": "assistant",
                "content_type": "question",
                "complete": False,
                "content": {
                    "time_taken": "null",
                    "time_limit":  "null",
                    "chunk_response": accumulated_message,
                    "full_response": '',
                    "realtime_evaluation": "",
                    # "interview_evaluation": interview_evaluation,
                    # "interview_evaluation_metrics": interview_evaluation_metrics
                }
            }
        ]
        
        await sio.emit("interview chat", message, room=sid) 
        
        
        for chunk in assistant_next_question:
            accumulated_message += chunk
            message = [{
                "user_type": "assistant",
                "content_type": "question",
                "complete": False,
                "content": {
                    "time_taken": "null",
                    "time_limit":  "null",
                    "chunk_response": chunk,  
                    "full_response": '',
                    "realtime_evaluation": ""
                }
            }]
            
            print("Chunk Message")
            print(chunk)  
            end_time = time.time() 
            elapsed_time = end_time - start_time  
            print(f"Chunk Time taken: {elapsed_time:.2f} seconds")

            await sio.emit("interview chat", message, room=sid) 
        
        start_time01 = time.time()
        timelimit =  util.interview_question_time_limit(accumulated_message)
        end_time01 = time.time() 
        elapsed_time01 = end_time01 - start_time01  
        print(f"Timelimit future exec Time taken: {elapsed_time01:.2f} seconds")  
                  
        message = [{
            "content": {
                "time_limit": timelimit.get("time_limit"),
                "full_response": accumulated_message,
            }
        }]
        
        await sio.emit("time_limit", message, room=sid)
        
        # if(data['response']):
        #     start_time02 = time.time()  
        #     realtime_evaluation_response_json = util.realtime_response_evaluation(data)
        #     realtime_evaluation = "" if realtime_evaluation_response_json is None else realtime_evaluation_response_json.get("realtime_evaluation")
        #     end_time02 = time.time() 
        #     elapsed_time02 = end_time02 - start_time02
        #     print(f"Realtime future exec Time taken: {elapsed_time02:.2f} seconds")
        #     message = [{
        #         "content": {
        #             "realtime_evaluation": realtime_evaluation
        #         }
        #     }]
            
        #     await sio.emit("realtime", message, room=sid)

        
        # if data['question_counter'] < 9:
        #     status = False
        #     # await db.Add_Interview_History(sessionId, message)
        #     await prisma.create_chat(sessionId, message, status)
        # else: 
        #     status = True           
        #     # await db.Add_Interview_History(sessionId, message)
        #     await prisma.create_chat(sessionId, message, status)
        #     # await db.Add_Interview_Observer(sessionId, interview_evaluation, interview_evaluation_metrics)
        #     await prisma.create_observer(sessionId, interview_evaluation, interview_evaluation_metrics)

        # await sio.emit("interview chat", message, room=sid) 

     
    except Exception as e:
        return f'Error: {str(e)}'
    
        
    finally:
        end_time = time.time() 
        elapsed_time = end_time - start_time  
        print(f"Time taken for interview processing: {elapsed_time:.2f} seconds")


@sio.on("audio chat")
async def audio_endpoint(sid, data):
    print("That is not what I am saying")
    try:
        start_time = time.time()        
        response = await util.generate_interview_question(data)               
 
        assistant_next_question = "" if response.get("interview") is None else response["interview"]   
        accumulated_message = "" 
         
        for chunk in assistant_next_question:
            accumulated_message += chunk
            print("Chunk Message")
            print(chunk)  
            end_time = time.time() 
            elapsed_time = end_time - start_time  
            print(f"Chunk Time taken: {elapsed_time:.2f} seconds")    
             
            while True:
                last_period = accumulated_message.rfind('.')
                last_question = accumulated_message.rfind('?')

                last_end_pos = max(last_period, last_question)
                
                if last_end_pos != -1:
                    complete_sentence = accumulated_message[:last_end_pos + 1]
                    
                    await sio.emit("audio chat", complete_sentence, room=sid)
                    
                    accumulated_message = accumulated_message[last_end_pos + 1:].strip()
                else:
                    break
            
            

   
    except Exception as e:
        print(f'Error: {str(e)}')  
        
    finally:
        end_time = time.time() 
        elapsed_time = end_time - start_time  
        print(f"Time taken for audio interview processing: {elapsed_time:.2f} seconds")



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
#                 "complete": complete,
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

