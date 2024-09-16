import socketio, ast
# import utils.db as database
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
        print("socket_analysis", data['message'])        
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
    print("interview_data", data['response'], data['user']['jbPath'], data['cvPath'])
    try:

        response = await util.interview_chat_response(data)
           
        message = [
                {
                "role": "candidate",
                "response": data['response']
                },
                {
                "role": "assistant",
                "response": response
                }
                ]
        
               
        # await database.interview_chat_to_db(data, message)
            
        # print(f"Interview response: {message}")
        await sio.emit("interview chat", message, room=sid)

    except Exception as e:
        return f'Error: {str(e)}'


