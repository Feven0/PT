import socketio, ast
import api.modules.ipersona_utils as util

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
   
   
@sio.on("analyse")
async def analysis_endpoint(sid, data):
    try:
        print("socket_analysis", data['cvPath'])        
        response = await util.analysis_chat_response(data)

        message = [
                {
                "role": "user",
                "response": data['message']
                },
                {
                "role": "assistant",
                "response": response
                }
                ]
        
        # await database.analyse_chat_to_db(data, message)       
            
        # print(f"Analysis response: {message}")
        await sio.emit("analyse", message, room=sid)
    except Exception as e:
        return f'Error: {str(e)}'


@sio.on("interview chat")
async def interview_endpoint(sid, data):
    print("interview_data", data['time_taken'], "counter:", data['question_counter'])
    try:

        response = await util.interview_chat_response(data)
        print("response coming", response)
        message = [
                {
                "role": "candidate",
                "response": data['response'],
                "time_taken": data['time_taken'],
                },
                {
                "role": "assistant",
                "response": response
                }
                ]
        print("response message coming", message)
        print("########check counter########")
        data['history'].extend(message)
        
        if data['question_counter'] == 5:
            response_metrics = await util.interview_chat_response_metrics(data)
            # print(f"Interview response: {response_metrics}")
            await sio.emit("interview chat", {
                "message": message,
                "response_metrics": response_metrics
            }, room=sid)
        else:    
            # await database.interview_chat_to_db(data, message)
            await sio.emit("interview chat", {
            "message": message,
            "response_metrics": ""
            }, room=sid)   

    except Exception as e:
        return f'Error: {str(e)}'


