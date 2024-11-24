import socketio, time
import api.pages.ipersona.socket.ipersona_parrot_gpt as util
import api.pages.ipersona.socket.ipersona_parrot_audio as audio
import api.pages.ipersona.socket.ipersona_parrot_audio_copy as copy
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

# Create a ThreadPoolExecutor for handling TTS tasks in parallel
executor = ThreadPoolExecutor(max_workers=5)  

###################### this setup cause misorder becuase some chunks may be faster to finish on tts so they are passed first so misorderin happened###################
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

        tasks = [synthesize_text(chunk) for chunk in assistant_next_question]
        
        for task in asyncio.as_completed(tasks):
            audio_data = await task

            if isinstance(audio_data, dict) and 'error' in audio_data:
                print(f"Error: {audio_data['error']}")
                continue

            await sio.emit("audio-single-chunk", audio_data, room=sid)

    except Exception as e:
        print(f"Error processing audio: {e}")

    finally:
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Time taken for audio interview processing: {elapsed_time:.2f} seconds")



###############################Avoids misorder, start all chunk process at the same time wait for all execution to end and pass the audios############################
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
        response = await copy.generate_interview_question(data)
        assistant_next_question = response.get("interview", "")

        tasks = [synthesize_text(chunk) for chunk in assistant_next_question]
        
        audio_chunks = await asyncio.gather(*tasks)

        for audio_data in audio_chunks:
            if isinstance(audio_data, dict) and 'error' in audio_data:
                print(f"Error: {audio_data['error']}")
                continue

            await sio.emit("audio-single-chunk", audio_data, room=sid)

    except Exception as e:
        print(f"Error processing audio: {e}")
        
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

