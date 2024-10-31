import socketio, ast, time
import api.modules.ipersona_parrot as util
import api.llm.ipersona.ipersona_schema as db
import api.llm.ipersona.ipersona_prisma as prisma
import api.llm.ipersona.ipersona_gpt as gpt
from openai import OpenAI
import textwrap
from IPython.display import display, clear_output, HTML

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


async def process_streamed_responses(response_stream):
    response_text = ""
    complete_texts = []
    
    for chunk in response_stream:
        chunk_message = chunk.choices[0].delta.content
        if chunk_message is not None:  
            response_text += chunk_message
        is_complete = chunk.choices[0].finish_reason is not None
        
        wrapped_text = textwrap.fill(response_text, width=80)  
        complete_texts.append(wrapped_text)
        
        print("damon love")
        print(wrapped_text)
        if is_complete:
            break
   
@sio.on("interview chat")
async def interview_endpoint(sid, data):
    print("interview_session-data", type(data['user_session']), data['user_session']['id'])
    try:
        start_time = time.time()
        global chat_count
        chat_count = 1  
        sessionId =  data['user_session']['id']   
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
        print("bonieeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee")
        print(response.get("interview"))
                    
 
        assistant_next_question = "" if response.get("interview") is None else response["interview"]
        # assistant_next_question = "null" if response.get("interview") is None else response["interview"].get("interview_question")
        realtime_evaluation = "" if response.get("realtime") is None else response["realtime"].get("realtime_evaluation")
        interview_evaluation = "" if response.get("overall") is None else response["overall"].get("overall_evaluation")
        interview_evaluation_metrics = "" if response.get("metrics") is None else response["metrics"].get("evaluation_metrics")
        
        print("interview+evaluation")
        print(interview_evaluation)
        print("^^^^^^^^^^^^^^^^^^^^^^^^^^")
        print("interview+eval+metrics")
        print(interview_evaluation_metrics)
        
        accumulated_message = ""  
        
        if realtime_evaluation is not None:
            content_type = "question_feedback"
            complete = False
        elif chat_count == 8:
            content_type = "question_feedback"
            complete = True
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
                    "time_limit":  "null",
                    "chunk_response": accumulated_message,
                    "full_response": '',
                    "realtime_evaluation": realtime_evaluation,
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
                "content_type": content_type,
                "complete": complete,
                "content": {
                    "time_taken": "null",
                    "time_limit":  "null",
                    "chunk_response": chunk,  
                    "full_response": '',
                    "realtime_evaluation": realtime_evaluation
                }
            }]
            
            print("Chunk Message")
            print(chunk)  
            end_time = time.time() 
            elapsed_time = end_time - start_time  
            print(f"Chunk Time taken: {elapsed_time:.2f} seconds")


            await sio.emit("interview chat", message, room=sid) 
          
            
        timelimit =  await util.interview_question_time_limit(accumulated_message)
        final_message = [{
            "user_type": "assistant",
            "content_type": content_type,
            "complete": complete,
            "content": {
                "time_taken": "null",
                "time_limit": timelimit.get("time_limit"),
                "chunk_response": '',
                "full_response": accumulated_message,
                "realtime_evaluation": realtime_evaluation
            }
        }]
        
        await sio.emit("interview fullchat", final_message, room=sid)
        
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
                
        def fetch_chunks(client, model, messages, temperature=0):
            response = client.chat.completions.create(  
                model=model,
                messages=messages,
                temperature=temperature,
                stream=True 
            )

            for chunk in response:
                chunk_message = chunk.choices[0].delta.content 
                if chunk_message: 
                    yield chunk_message

        model = 'gpt-4o-mini'
        messages = [{'role': 'user', 'content': "What is your name?"}]

        
        accumulated_message = ""  

        for chunk in fetch_chunks(client, model, messages):
            accumulated_message += chunk 
            await sio.emit("audio chat", chunk, room=sid) 
            
        # for chunk in fetch_chunks(client, model, messages):
        #     print(chunk)  
        #     await sio.emit("audio chat", chunk, room=sid) 

                    
        # model = 'gpt-4o-mini'
        # messages = [{'role': 'user', 'content': "Tell me about ethiopia in 100 characters?"}]
        
        # for wrapped_text in generate_response(client, model, messages):
        #     await sio.emit("audio chat", wrapped_text, room=sid) 

    except Exception as e:
        print(f'Error: {str(e)}')  
        
    finally:
        end_time = time.time() 
        elapsed_time = end_time - start_time  
        print(f"Time taken for interview processing: {elapsed_time:.2f} seconds")



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

