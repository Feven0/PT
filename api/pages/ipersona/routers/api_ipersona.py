
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
import api.pages.ipersona.models.model_persona as pemodel
import assemblyai as aai
import ast

hr_agent = agents()

uploaded_files = []
hr_persona = []

# load_dotenv("../.env")
# ASSEMBLYAI_API_KEY= os.getenv("ASSEMBLYAI_API_KEY")
aai.settings.api_key = "49e5f82458584a70b847f477a035ce48"
transcriber = aai.Transcriber()


# router = APIRouter()
routes = FastAPI(openapi_prefix="/api")

module_dir= os.path.dirname(__file__)
module_di= os.path.dirname('/home/rehmet/dev/tenx_ipersona/api/modules/prompts')
data_path = lambda x: os.path.join(module_dir, "folders", x)
prompt_path = lambda x: os.path.join(module_di, "prompts", x)


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
        created_persona = util.create_persona(recieved.jbJson)
        prompt_text = util.file_reader(prompt_path('ipersona/prompt/persona.txt'))
        generated_persona = prompt_text\
                .replace("{hr_persona}", created_persona)\
                .replace("{job_description}", str(recieved.jbJson))\
                .replace("{profile}", str(recieved.cvJson))    
                
        
        message = util.file_reader(prompt_path('ipersona/prompt/generate_question.txt'))
        context = str(message)
        
        msg=context\
            .replace("{background_count}", str(2))\
            .replace("{technical_count}", str(2))\
            .replace("{behavioral_count}", str(2))\
            .replace("{ability_count}", str(2))
        
        hr_agent.assistant.update_system_message(generated_persona)
        response = await hr_agent.generate_question(msg)
        generated_question_json = util.extract_json(response, quite=False)
        
        # Initialize question number
        question_number = 1
        for category, questions in generated_question_json.items():
            for question in questions:
                question["question_number"] = str(question_number)  
                question_number += 1 
        combined_generated_question_json = json.dumps(generated_question_json, indent=4)
        
                
        data = {
            "userId": str(recieved.userId),
            "sessionId": str(uuid.uuid4()),
            "username": recieved.name,
            "user_profile": recieved.cvJson,
            "jobId": str(recieved.jobId),
            "job_desc": recieved.jbJson,
            "persona": generated_persona,
            "generated_questions": combined_generated_question_json 
        }
                
   
        res = await db.create_schema(data)
        return {"filenames": f"uploaded successfully: {res}"}
    
    except Exception as e:
        print(f"Error processing files: {e}")
        return JSONResponse(status_code=500, content={"error": "Error processing files"})
        
@routes.post("/clarify")
async def clarify_question(recieved: pemodel.ClarificationRequestRecieved): 
    question = recieved.question
    start_time = time.time()    
    try:                      
        result = await util.clarify_question(question)           
       
        return result
    
    except Exception as e:
        print(f"Error processing files: {e}")
        return JSONResponse(status_code=500, content={"error": "Error processing files"})

    finally:
        end_time = time.time() 
        elapsed_time = end_time - start_time 
        print(f"Time taken for question clarififcation processing: {elapsed_time:.2f} seconds")


@routes.post("/calculate_overall_progress")
async def calculate_overall_progress(recieved: pemodel.ChatHistoryRequestRecieved): 
    start_time = time.time()    
    try:  
        chathistory = await database.fecth_all_chathistory(recieved)                    
        result =  util.calculate_overall_progress(chathistory) 
        return result
    
    except Exception as e:
        print(f"Error processing files: {e}")
        return JSONResponse(status_code=500, content={"error": "Error processing files"})

    finally:
        end_time = time.time() 
        elapsed_time = end_time - start_time 
        print(f"Time taken for Analysis processing: {elapsed_time:.2f} seconds")
