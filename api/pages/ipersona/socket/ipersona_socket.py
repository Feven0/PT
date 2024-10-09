import socketio, ast, time
import api.modules.ipersona_parrot as util
sio = socketio.AsyncServer(cors_allowed_origins="*", async_mode="asgi")


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

        message = [
                {   
                    "candidate": {
                        "response": data['response'],
                        "time_taken": data['time_taken'],
                    }
                },
                {
                    "assistant": {
                        "response": "null" if response.get("interview") is None else response["interview"].get("interview_question"),
                        "realtime_evaluation": "null" if response.get("realtime") is None else response["realtime"].get("realtime_evaluation"),
                        "overall_evaluation": "null" if response.get("overall") is None else response["overall"].get("overall_evaluation"),
                        "metrics": "null" if response.get("metrics") is None else response["metrics"].get("evaluation_metrics"),
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

def get_socketio_app(fast_app):
    app = socketio.ASGIApp(
        socketio_server=sio,
        other_asgi_app=fast_app,
        socketio_path='/socket.io/'
    )
    return app