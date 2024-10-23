import socketio, ast, time
import api.modules.ipersona_parrot as util
import api.llm.ipersona.ipersona_schema as db
import api.llm.ipersona.ipersona_prisma as prisma

sio = socketio.AsyncServer(cors_allowed_origins="*", async_mode="asgi")
socket_app = socketio.ASGIApp(sio)


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
    print("interview_session-data", type(data['user_session']), data['user_session']['id'])
    try:
        start_time = time.time()
        global chat_count
        chat_count = 1  
        sessionId =  data['user_session']['id']   
        chat = await prisma.fetch_chat_history(data['user_session']['id'])
        if len(chat) != 0:  
            chat = chat[0].chathistory
            assistant_count = sum(1 for entry in chat if entry["user_type"] == "assistant")
            chat_count += assistant_count 
            print("Number of assistant entries:", chat_count)
        else:
            pass        

        if(data['response']):
            chathistory = [{
                "user_type": "candidate",
                "content_type": "answer",
                "complete": False,
                "content": {
                    "response": data['response'],
                    "time_taken": data['time_taken'],
                    "realtime_evaluation": "null"
                }
            }]
            # await db.Add_Interview_History(sessionId, chathistory)
            await prisma.create_chat(sessionId, chathistory)

        response = await util.generate_interview_question(data)

 
        assistant_next_question = "null" if response.get("interview") is None else response["interview"].get("interview_question")
        realtime_evaluation = "null" if response.get("realtime") is None else response["realtime"].get("realtime_evaluation")
        interview_evaluation = "null" if response.get("overall") is None else response["overall"].get("overall_evaluation")
        interview_evaluation_metrics = "null" if response.get("metrics") is None else response["metrics"].get("evaluation_metrics")

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
                    "response": assistant_next_question,
                    "realtime_evaluation": realtime_evaluation,
                    # "interview_evaluation": interview_evaluation,
                    # "interview_evaluation_metrics": interview_evaluation_metrics
                }
            }
        ]
        
        if chat_count < 9:
            # await db.Add_Interview_History(sessionId, message)
            await prisma.create_chat(sessionId, message)
        else:            
            # await db.Add_Interview_History(sessionId, message)
            await prisma.create_chat(sessionId, message)
            # await db.Add_Interview_Observer(sessionId, interview_evaluation, interview_evaluation_metrics)
            await prisma.create_observer(sessionId, interview_evaluation, interview_evaluation_metrics)

        await sio.emit("interview chat", message, room=sid) 

     
    except Exception as e:
        return f'Error: {str(e)}'
    
        
    finally:
        end_time = time.time() 
        elapsed_time = end_time - start_time  
        print(f"Time taken for interview processing: {elapsed_time:.2f} seconds")


@sio.on("audio chat")
async def audio_endpoint(sid, data):
    print("interview-audio-data", type(data['user_session']), data['user_session']['id'])
    try:
        start_time = time.time()
        # global chat_count
        # chat_count = 1  
        # sessionId =  data['user_session']['id']   
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
        #     await prisma.create_chat(sessionId, chathistory)

        response = await util.generate_interview_question(data)
        print("witches are the best")
        print(response)
 
        assistant_next_question = "null" if response.get("interview") is None else response["interview"].get("interview_question")
        realtime_evaluation = "null" if response.get("realtime") is None else response["realtime"].get("realtime_evaluation")
        interview_evaluation = "null" if response.get("overall") is None else response["overall"].get("overall_evaluation")
        interview_evaluation_metrics = "null" if response.get("metrics") is None else response["metrics"].get("evaluation_metrics")

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
                    "response": assistant_next_question,
                    "realtime_evaluation": realtime_evaluation,
                    "interview_evaluation": interview_evaluation,
                    "interview_evaluation_metrics": interview_evaluation_metrics
                }
            }
        ]
        print("vampires burn in the sun")
        print(message)
        # if chat_count < 9:
        #     await prisma.create_chat(sessionId, message)
        # else:            
        #     await prisma.create_chat(sessionId, message)
        #     await prisma.create_observer(sessionId, interview_evaluation, interview_evaluation_metrics)

        await sio.emit("audio chat", message, room=sid) 

     
    except Exception as e:
        return f'Error: {str(e)}'
    
        
    finally:
        end_time = time.time() 
        elapsed_time = end_time - start_time  
        print(f"Time taken for interview processing: {elapsed_time:.2f} seconds")

