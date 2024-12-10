import os, sys
import time
from io import BytesIO
import assemblyai as aai
from openai import OpenAI
#
from fastapi import FastAPI, File, UploadFile, Form, Request
from fastapi.responses import StreamingResponse, JSONResponse
#
from api import config
import api.modules.ipersona_parrot_gpt as util
import api.pages.ipersona.models.persona as pemodel
from api.services.strapi_ipersona import IpersonaManager
from api.llm.ipersona.ipersona_strapi_schemas import (
IpersonaAllUserSchema, IpersonaSessionSchema, IpersonaJobSchema, IpersonaSessionTinderUserJobMatchSchema, IpersonaSessionTinderUserReactionSchema, IpersonaSessionMessageSchema, IpersonaSessionObserverSchema, IpersonaSessionOverallObserverSchema, IpersonaProfileInformationSchema
)
from api.utils.logger import LLPackerLogger

logger = LLPackerLogger(os.path.basename(__file__))

#
OPENAI_API_KEY  = config.openai.api_key
client = OpenAI(api_key=OPENAI_API_KEY)

#
ASSEMBLYAI_API_KEY = config.assemblyai.api_key
aai.settings.api_key = ASSEMBLYAI_API_KEY 
transcriber = aai.Transcriber()

uploaded_files = []
module_dir= os.path.dirname(__file__)
data_path = lambda x: os.path.join(module_dir, "folders", x)
prompt_path = lambda x: os.path.join(module_dir, "data/prompts", x)




routes_test = FastAPI(openapi_prefix="/test")

@routes_test.post("/leapbase_test")
async def leapstrapi_methods():
    try:             
        #------------------------
        # ipersona_match = IpersonaSessionTinderUserReactionSchema()
        # job_match_data = ipersona_match.filter_by_with_user_and_job_id(user_profile_id=197, job_profile_id=1689, nopp=True, dataframe=False)
        # data = job_match_data
        #--------------------------      
        # ipersona_user = IpersonaTraineeSchema()
        # data = {
        #     "job_profile_id": 128,
        #     "all_user_id": 1959
        # }
        # trainee_profile_data = ipersona_user.filter_by_alluser_id(all_user_id=1959, nopp=True, dataframe=False)
        # if not trainee_profile_data:
        #         logger.warn("No trainee user profiles found.")
        #         return []
        # tinder_user_profile_id = trainee_profile_data[0]['id'] 
        # ipersona_session = IpersonaSessionSchema()    
        # session = ipersona_session.filter_by_with_user_job_id(user_profile_id=tinder_user_profile_id,job_profile_id=data['job_profile_id'], nopp=True, dataframe=False) 
        # session_chatobserver = util.extract_observers_metrics(session)
      
        # data = await util.calculate_overall_progress(data, session_chatobserver) 
        # --------------------------------------------------------------
        
        # schema = IpersonaTraineeSchema()
        # schema = IpersonaJobSchema()
        # data = schema.filter_by_job_id(job_profile_id=128, nopp=True, dataframe=False)
        # data = schema.get_all_sessions(nopp=True, dataframe=False)
        # data = schema.get_trainee_by_id(user_profile_id=197, nopp=True, dataframe=False)
        # data = data["attributes"]["all_users"]["data"][0]["id"]
            
        # data = schema.filter_by_observer_id(observer_id=70, nopp=True, dataframe=False)
        # data = schema.filter_by_with_more_ids(observer_id=70, trainee_user_id=164, nopp=True, dataframe=False)
        
        # ipersona_user = IpersonaTraineeSchema()
        # all_user_data = ipersona_user.get_trainee_by_id(user_profile_id=197, nopp=True, dataframe=False, return_object=True)
        # data = all_user_data.get('attributes', {}).get('all_users', {}).get('data', [{}])[0].get('id')
        #------------------------

        # {
        #     "slug": "new-session",
        #     "status": "active",
        #     "attributes": {"field1": "value1", "field2": "value2"},
        #     "tinder_user_profile": 164,
        #     "tinder_job_profile": 128
        # }
        
        #------------------------
        # session_data = {
        #     "slug": str(f"all_user_id: "), 
        #     "status": "Incomplete",
        #     "attributes": {
        #         "persona": "generated_persona",  
        #         "generated_questions": "generated_question_json"
        #     },
        #     "user_profile_id": 164,
        #     "job_profile_id": 128
        # }

        # saved_session = schema.save_session(params=session_data, return_object=True, nopp=True, dataframe=False)
        # data = saved_session
        #-------------------------

        
        # -------------------------
        # session_data = {
        #     "i_persona_session_id": 181, 
        #     "status": "Incomplete",
        # }

        # updated_session = schema.update_session(params=session_data, nopp=True, dataframe=False, return_object=True)
        # data = updated_session
        #------------------------
        
        
        #------------------------
        # deleted_session = schema.delete_session(ids=190, nopp=True, dataframe=False, return_object=True)
        # data = deleted_session
        #------------------------

        # schema = IpersonaAllUserSchema()
        # data = schema.get_alluser_by_id(all_user_id = 1959, nopp=True, dataframe=False, return_object=True)
        # schema = IpersonaProfileInformationSchema()
        # data = schema.filter_by_all_user_id(all_user_id = 1959, nopp=True, dataframe=False, return_object=True)
        return data
        
    
    except Exception as e:
        print(f"Error processing files: {e}")
    except Exception as e:
        print(f"Error processing files: {e}")
        return {"error": str(e)}
    
@routes_test.post("/strapi_db_test")
async def strapi_methods():
    try:
        ipersona_manager = IpersonaManager(sessionId=120, id=14, all_user_id=1959, user_profile_id=164, job_profile_id=128, run_stage="dev")
        # ipersona_manager = IpersonaManager(sessionId=42, alluser=16, job_profile_id=1045, run_stage="dev")

        # data = ipersona_manager.get_messages()
        # data = ipersona_manager.get_observers()
        # data = ipersona_manager.get_alluser_sessions()
        # data = ipersona_manager.get_match(tinder_user_profile_id = 190, tinder_job_profile_id = 46)
        # data = ipersona_manager.get_job_sessions_observers()
        # data = ipersona_manager.get_job_sessions()
        
        # data = ipersona_manager.get_all_sessions()
        # data = ipersona_manager.get_user_reaction_id()
        # data = util.summarize_allusers_data()
        
        # data = ipersona_manager.get_alluserid_from_user_profile()
        # data = util.calculate_session_metrics(data)
        # data = ipersona_manager.get_session()
        # data = ipersona_manager.get_all_user_data()
        # data = ipersona_manager.session_overall_observer()
        data = ipersona_manager.get_trainee_user_profile()
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


