
import os, sys
import json
import time
from typing import List, Dict
import asyncio

#
curdir = os.path.dirname(os.path.realpath(__file__))
cpath = os.path.dirname(curdir)
if not cpath in sys.path:
    sys.path.append(cpath) 
    
#
from fastapi import APIRouter, BackgroundTasks
from fastapi import FastAPI, File, UploadFile, Form, Request
from fastapi.responses import JSONResponse
import os, openai, uuid, time
import api.modules.ipersona_utils as util
import time
from fastapi import FastAPI
import time
from fastapi import UploadFile, Form
from typing import List
import api.llm.ipersona.ipersona_schema as db
import api.llm.ipersona.ipersona_db as database
from api.llm.ipersona.ipersona_agent import agents
from dotenv import load_dotenv
import api.pages.ipersona.models.model_persona as pemodel
import assemblyai as aai
import ast

hr_agent = agents()

# env_manager = get_env_manager()
# from api.logs.loggers.logger import logger_config

# logger = logger_config(__name__)


uploaded_files = []
hr_persona = []

# load_dotenv("../.env")
# ASSEMBLYAI_API_KEY= os.getenv("ASSEMBLYAI_API_KEY")
aai.settings.api_key = "49e5f82458584a70b847f477a035ce48"
transcriber = aai.Transcriber()


# router = APIRouter()
routes = FastAPI(openapi_prefix="/api")

module_dir= os.path.dirname(__file__)
data_path = lambda x: os.path.join(module_dir, "folders", x)


@routes.post("/upload")
async def upload_files(
    file: UploadFile = File(...),
    userId: str = Form(...),
    email: str = Form(...)):
    try:
        file_path = os.path.join(data_path('cv_files'), file.filename)
        with open(file_path, "wb") as f:
            contents = await file.read()
            f.write(contents)

        output_file = os.path.splitext(file.filename)[0] + ".txt"
        output_file_path = os.path.join(data_path('txt_files'), output_file)
        util.pdf_to_txt(file_path, output_file_path)
        
        #################### Save to DB #####################   
        data = {
            "email": email,
            "userId": userId,
            "sessionId": str(uuid.uuid4()),
            "fileName": file.filename,
            "cvPath": output_file_path
        }
                
         
        res = await db.create_schema(data)
        return {"filenames": f"uploaded successfully: {data}"}
    
    except Exception as e:
        print(f"Error processing files: {e}")
        return JSONResponse(status_code=500, content={"error": "Error processing files"})

@routes.post("/audio_upload")
async def speech_to_text(file: UploadFile = File(...)):
    try:
        start_time_1 = time.time() 
        print("######## Audio Processing #######")
        audio_path  = os.path.join(data_path('audio'), file.filename)
        with open(audio_path, "wb") as f:
            contents = await file.read()
            f.write(contents)
        
        transcriber = aai.Transcriber()
        transcript = transcriber.transcribe(audio_path)

        if transcript.status == aai.TranscriptStatus.error:
            print(transcript.error)
            return {"error": transcript.error}
        else:
            print(transcript.text)
            return {"transcription": transcript.text}
    except Exception as e:
        # logger.exception(f"Query failed {str(e)}")
        print("audio transcriptin failed", e)
        return JSONResponse(
            content={
                "system": f"Something went wrong! {str(e)}",
                "transcript": "Failed"
            }
        )
    finally:
        end_time = time.time() 
        elapsed_time = end_time - start_time_1  
        print(f"Time taken for audio upload processing: {elapsed_time:.2f} seconds")

@routes.post("/create_user_session")
async def user_session_files(recieved: pemodel.userSessionRequestRecieved):
    try:
        #################### Save to DB #####################   
        data = {
            "email": recieved.email,
            "userId": recieved.userId,
            "sessionId": str(uuid.uuid4()),
            "fileName": recieved.name,
            "cvPath": recieved.cvJson
        }
                
   
        res = await db.create_schema(data)
        return {"filenames": f"uploaded successfully: {res}"}
    
    except Exception as e:
        print(f"Error processing files: {e}")
        return JSONResponse(status_code=500, content={"error": "Error processing files"})


@routes.post("/analyse_cv")
async def analyse_cv_job(recieved: pemodel.AnalyseJobRequestRecieved): 
    # 
    start_time = time.time()    
    try: 
        global hr_agent
        # jbPath = data_path('txt_files/job.txt')
        global persona        
                     
             
        job_session_id = await database.save_to_db(recieved)
        result = await util.analysing_vitae(recieved)
            
        data = {
            "id": job_session_id,
            "persona": result['generated_persona'],
            "analysis": result['response']
        }    
         
        res = await db.update_ipersona_data_new(data, fields_to_update=['persona', 'analysis'])
        return result['response']
    
    except Exception as e:
        print(f"Error processing files: {e}")
        return JSONResponse(status_code=500, content={"error": "Error processing files"})

    finally:
        end_time = time.time() 
        elapsed_time = end_time - start_time 
        print(f"Time taken for Analysis processing: {elapsed_time:.2f} seconds")
        
        
@routes.post("/all_metrics")
async def analyse_all_metrics(): 
    # 
    start_time = time.time()    
    try:                      
        result = await util.analysing_all_metrics()            
       
        return result
    
    except Exception as e:
        print(f"Error processing files: {e}")
        return JSONResponse(status_code=500, content={"error": "Error processing files"})

    finally:
        end_time = time.time() 
        elapsed_time = end_time - start_time 
        print(f"Time taken for Analysis processing: {elapsed_time:.2f} seconds")
