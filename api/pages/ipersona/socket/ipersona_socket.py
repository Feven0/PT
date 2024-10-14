import socketio, ast, time
import api.modules.ipersona_parrot as util
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
    print("interview_data", data["previous_question"], data['user_session']['jobId'])
    try:
        start_time = time.time()
        response = await util.generate_interview_question(data)

        # message = [
        #         {   
        #             "candidate": {
        #                 "response": data['response'],
        #                 "time_taken": data['time_taken'],
        #             }
        #         },
        #         {
        #             "assistant": {
        #                 "response": "null" if response.get("interview") is None else response["interview"].get("interview_question"),
        #                 "realtime_evaluation": "null" if response.get("realtime") is None else response["realtime"].get("realtime_evaluation"),
        #                 "overall_evaluation": "null" if response.get("overall") is None else response["overall"].get("overall_evaluation"),
        #                 "metrics": "null" if response.get("metrics") is None else response["metrics"].get("evaluation_metrics"),
        #             }
        #         }
        #     ]
        
        assistant_next_question = None if response.get("interview") is None else response["interview"].get("interview_question")
        realtime_evaluation = None if response.get("realtime") is None else response["realtime"].get("realtime_evaluation")
        interview_evaluation = None if response.get("overall") is None else response["overall"].get("overall_evaluation")
        interview_evaluation_metrics = None if response.get("metrics") is None else response["metrics"].get("evaluation_metrics")

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
                    "time_taken": None,
                    "response": assistant_next_question,
                    "realtime_evaluation": realtime_evaluation,
                    "interview_evaluation": interview_evaluation,
                    "interview_evaluation_metrics": interview_evaluation_metrics,
                }
            }
        ]
        
        await sio.emit("interview chat", message, room=sid) 

     
    except Exception as e:
        return f'Error: {str(e)}'
    
        
    finally:
        end_time = time.time() 
        elapsed_time = end_time - start_time  
        print(f"Time taken for interview processing: {elapsed_time:.2f} seconds")


