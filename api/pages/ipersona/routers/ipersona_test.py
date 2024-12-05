import os, sys
curdir = os.path.dirname(os.path.realpath(__file__))
cpath = os.path.dirname(curdir)
if not cpath in sys.path:
    sys.path.append(cpath) 
from fastapi import FastAPI, File, UploadFile, Form, Request
from fastapi.responses import StreamingResponse, JSONResponse
import api.modules.ipersona_parrot_gpt as util
import api.pages.ipersona.routers.test2 as IpersonaSchema
import api.pages.ipersona.models.persona as pemodel
import assemblyai as aai
from openai import OpenAI
from api.services.secret import get_auth
from api.utils.logger import LLPackerLogger

logger = LLPackerLogger(os.path.basename(__file__))

OPENAI_API_KEY  = get_auth(ssmkey='OPENAI_PARROT_API_KEY')

uploaded_files = []

# ASSEMBLYAI_API_KEY= os.getenv("ASSEMBLYAI_API_KEY")
aai.settings.api_key = "49e5f82458584a70b847f477a035ce48"
transcriber = aai.Transcriber()

routes_test = FastAPI(openapi_prefix="/test")

module_dir= os.path.dirname(__file__)
module_di= os.path.dirname(__file__)
data_path = lambda x: os.path.join(module_dir, "folders", x)
prompt_path = lambda x: os.path.join(module_di, "data/prompts", x)

client = OpenAI(api_key=OPENAI_API_KEY)


import time, asyncio
from openai import OpenAI
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from api.services.strapi_ipersona import IpersonaManager
from api.pages.ipersona.routers.test import AllUserSchema
from api.pages.ipersona.routers.test2 import IpersonaSchema
from api.llm.ipersona.ipersona_strapi_schemas import IpersonaSessionSchema

from io import BytesIO
from api.services.secret import get_auth
import numpy as np
import pandas as pd
OPENAI_API_KEY  = get_auth(ssmkey='TENX_DEV_STRAPI_TOKEN')
app = FastAPI()

@routes_test.post("/leapbase_test")
async def leapstrapi_methods():
    try:      
        # schema = IpersonaSchema()
        schema = IpersonaSessionSchema()
        data = schema.get_all_sessions(nopp=True,dataframe=False)
        # data = schema.get_trainee(idval='136',nopp=True,dataframe=False)
        # data = schema.filter_by_2id(vid='64', tid=167, nopp=True,dataframe=False)
        return data
        
    
    except Exception as e:
        print(f"Error processing files: {e}")
    except Exception as e:
        print(f"Error processing files: {e}")
        return {"error": str(e)}
    
@routes_test.post("/strapi_db_test")
async def strapi_methods():
    try:
        ipersona_manager = IpersonaManager(sessionId=120, id=14, all_user_id=1920, user_profile_id=164, job_profile_id=128, run_stage="dev")
        # ipersona_manager = IpersonaManager(sessionId=42, alluser=16, job_profile_id=1045, run_stage="dev")

        # data = ipersona_manager.get_messages()
        # data = ipersona_manager.get_observers()
        # data = ipersona_manager.get_alluser_sessions()
        # data = ipersona_manager.get_match(tinder_user_profile_id = 190, tinder_job_profile_id = 46)
        # data = ipersona_manager.get_job_sessions_observers()
        # data = ipersona_manager.get_job_sessions()
        
        #data = ipersona_manager.get_all_sessions()
        data = ipersona_manager.get_user_reaction_id()
        # data = util.summarize_allusers_data(data)
        
        # data = ipersona_manager.get_alluserid_from_user_profile()
        # data = util.calculate_session_metrics(data)
        # data = ipersona_manager.get_session()
        # data = ipersona_manager.get_all_user_data()
        # data = ipersona_manager.session_overall_observer()
        # data = ipersona_manager.get_trainee_user_profile()
        # data = ipersona_manager.get_trainee_job_profile()
        # data = ipersona_manager.get_alluserId()

        # data = ipersona_manager.get_trainee_user_profile()  
        # data = extract_job_neccessary_values(data)
    
            
        # data = ipersona_manager.get_job_sessions()
        # data = ipersona_manager.update_session_status()
        # data = ipersona_manager.get_session()
        # message_data = {
        #     "attributes": {
        #         "overall_confidence": "confidence_overtime",
        #         "overall_clarity": "clarity_overtime",
        #         "overall_engagement": "engagement_overtime",
        #         "overall_time_management": "overall_time_managements",
        #         "overall_competency": "overall_competencies",
        #         "overall_performance": "overall_performance_scores"
        #     },
        #     "metadata": {
        #         "createdBy": "parrot"
        #     },
        #     "jobprofileId": 1080,   # This should be an integer
        #     "all_user_id": 187,      # 2241This should be an integer
        #     "sessionIds": [35, 36]  # This should be a list of integers
        # }

        # data = ipersona_manager.create_session_overall_observer(message_data)
        return data
       
    
    except Exception as e:
        print(f"Error processing files: {e}")
    except Exception as e:
        print(f"Error processing files: {e}")
        return {"error": str(e)}


@routes_test.post("/synthesize-audio/")
async def synthesize_audio(recieved: pemodel.audioRequestRecieved):
    print('Received text for synthesis:', recieved.text)
    
    response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=recieved.text
    )
    print("Error in audio synthesis:", response)
    if not response:
        print("Error in audio synthesis:", response)
        return {"error": "Failed to synthesize audio"}
    audio_data = response.read()  
    audio_stream = BytesIO(audio_data)
    audio_stream.seek(0)

    print("Audio stream created successfully")
    return StreamingResponse(audio_stream, media_type="audio/mpeg")


@routes_test.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    try:
        audio_path  = os.path.join(data_path('audio'), file.filename)
        with open(audio_path, "wb") as f:
            contents = await file.read()
            f.write(contents)
        
        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_path
        )
        return {"transcription": transcription.text}
    except Exception as e:
        print(f"Error processing files: {e}")

import io

@routes_test.post("/synthesize")
async def synthesize_text():
    print("Received text for synthesis:")
    try:
        response = client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input="text france best love"
        )

        audio_data = response.read()  
        
        print("Audio data size:", len(audio_data))  
        print("Audio data content:", audio_data)  

        if len(audio_data) == 0 or len(audio_data) < 500:  
            return {"error": "Received insufficient audio data."}

        audio_stream = io.BytesIO(audio_data)

        return StreamingResponse(audio_stream, media_type="audio/mpeg")

    except Exception as e:
        print(f"Error processing audio: {e}")
        return {"error": str(e)}

