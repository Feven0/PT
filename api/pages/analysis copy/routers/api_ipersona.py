
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
import utils.utils as util
import time
from fastapi import FastAPI
from models.Analysis import FileReceivedPayload
import time
from fastapi import UploadFile, Form
import boto3
from typing import List
import api.utils.ipersona_schema as db
import api.utils.ipersona_db as database
from config.env_manager import get_env_manager
from scripts.agents import agents
from dotenv import load_dotenv
import assemblyai as aai
import api.pages.analysis.models.model_persona as PM
from api.pages.analysis.models import model_cv_analysis as camodel
import ast
hr_agent = agents()

env_manager = get_env_manager()
# from api.logs.loggers.logger import logger_config

# logger = logger_config(__name__)

s3_client = boto3.client('s3')

routes = FastAPI(openapi_prefix="/api")
uploaded_files = []
hr_persona = []

load_dotenv(".env")
ASSEMBLYAI_API_KEY= os.getenv("ASSEMBLYAI_API_KEY")
aai.settings.api_key = ASSEMBLYAI_API_KEY
transcriber = aai.Transcriber()


router = APIRouter()



@routes.post("/upload")
async def upload_files(
    file: UploadFile = File(...),
    userId: str = Form(...),
    email: str = Form(...)):
    try:
        file_path = os.path.join("./cv_files", file.filename)
        with open(file_path, "wb") as f:
            contents = await file.read()
            f.write(contents)

        output_file = os.path.splitext(file.filename)[0] + ".txt"
        output_file_path = os.path.join("./txt_files", output_file)
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
        return {"filenames": f"uploaded successfully: {res}"}
    
    except Exception as e:
        print(f"Error processing files: {e}")
        return JSONResponse(status_code=500, content={"error": "Error processing files"})


@routes.post("/audio_upload")
async def speech_to_text(file: UploadFile = File(...)):
    try:
        start_time_1 = time.time() 
        print("######## Audio Processing #######")
        file_path = os.path.join("./audio", file.filename)
        with open(file_path, "wb") as f:
            contents = await file.read()
            f.write(contents)
        
        audio_path = "./audio/" + file.filename 
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


@routes.post("/analyse_cv")
async def analyse_cv_job(recieved: PM.AnalyseJobRequestRecieved): 
    start_time = time.time()    
    try: 
        global hr_agent
        jbPath = recieved.jbPath
        jbPath = "./txt_files/job.txt"   
        global persona        

        created_persona = util.create_persona(jbPath)
        prompt_text = util.file_reader('./prompts/persona.txt')
        generated_persona = prompt_text.replace("{hr_persona}", created_persona)                         
             
        job_session_id = await database.save_to_db(recieved, jbPath)
        response = await util.analysing_vitae(generated_persona, recieved,  jbPath)
            
        data = {
            "id": job_session_id,
            "persona": generated_persona,
            "analysis": response,
        }    
         
        res = await db.update_ipersona_data_new(data, fields_to_update=['persona', 'analysis'])
        return response
    
    except Exception as e:
        print(f"Error processing files: {e}")
        return JSONResponse(status_code=500, content={"error": "Error processing files"})

    finally:
        end_time = time.time() 
        elapsed_time = end_time - start_time 
        print(f"Time taken for Analysis processing: {elapsed_time:.2f} seconds")
