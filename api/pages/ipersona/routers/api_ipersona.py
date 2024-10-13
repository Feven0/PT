
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
import api.modules.ipersona_parrot as util
import time
from fastapi import FastAPI
import time
from fastapi import UploadFile, Form
from typing import List
import api.llm.ipersona.ipersona_schema as db
import api.llm.ipersona.ipersona_db as database
from api.llm.ipersona.ipersona_agent import agents
import api.pages.ipersona.models.persona as pemodel
import assemblyai as aai
import ast

hr_agent = agents()

uploaded_files = []
hr_persona = []

# load_dotenv("../.env")
# ASSEMBLYAI_API_KEY= os.getenv("ASSEMBLYAI_API_KEY")
aai.settings.api_key = "49e5f82458584a70b847f477a035ce48"
transcriber = aai.Transcriber()


routes = FastAPI(openapi_prefix="/api")

module_dir= os.path.dirname(__file__)
module_di= os.path.dirname(__file__)
data_path = lambda x: os.path.join(module_dir, "data", x)
prompt_path = lambda x: os.path.join(module_di, "data", x)


@routes.post("/audio_upload")
async def speech_to_text(file: UploadFile = File(...)) -> dict:
    """
    Converts audio file to text using a speech-to-text assembly transcriber.

    This asynchronous function processes an uploaded audio file, saves it to a 
    specified location, and uses assembly transcriber to convert the audio to text. 
    It returns the transcription result or an error message if the process fails.

    Parameters:
    ----------
    file : UploadFile
        The audio file uploaded by the user.

    Returns:
    -------
    dict
        A dictionary containing the transcription result or an error message 
        if an exception occurs during processing.
    """
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
    print("sissssssssssssssssssssssssssssters")
    try:
        """
        Processes user session files and generates interview questions.

        This asynchronous function saves user profile data, creates a persona 
        from job descriptions, and generates questions using an HR agent. It 
        stores the session data in a database and returns a success message.

        Parameters:
        ----------
        recieved : pemodel.userSessionRequestRecieved
            An object containing user session information including job description, 
            user profile, and user ID.

        Returns:
        -------
        dict
            A dictionary containing a success message with the uploaded filenames 
            or an error response if an exception occurs during processing.
        """
        
        created_persona = util.create_persona(recieved.jbJson)
        prompt_text = util.file_reader(prompt_path('persona.txt'))
        generated_persona = prompt_text\
                .replace("{hr_persona}", created_persona)\
                .replace("{job_description}", str(recieved.jbJson))\
                .replace("{profile}", str(recieved.cvJson))    
                
        
        message = util.file_reader(prompt_path('generate_question.txt'))
        context = str(message)
        
        msg=context\
            .replace("{background_count}", str(2))\
            .replace("{technical_count}", str(2))\
            .replace("{behavioral_count}", str(2))\
            .replace("{ability_count}", str(2))
        
        hr_agent.assistant.update_system_message(generated_persona)
        response = await hr_agent.generate_question(msg)
        generated_question_json = util.extract_json(response, quite=False)
        
        question_number = 1
        for category, questions in generated_question_json.items():
            for question in questions:
                question["question_number"] = str(question_number)  
                question_number += 1 
        combined_generated_question_json = json.dumps(generated_question_json, indent=4)
        
        
        #------------- Save to DB ---------------        
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
        #------------- ---------------------- 
        
        return {"filenames": f"uploaded successfully"}
    
    except Exception as e:
        print(f"Error processing files: {e}")
        return JSONResponse(status_code=500, content={"error occur": f"Error processing files: {e}"})
        
        
@routes.post("/clarify")
async def clarify_question(recieved: pemodel.ClarificationRequestRecieved) -> dict:
    """
    Clarifies a given question using a clarification utility.

    This asynchronous function processes a clarification request by calling 
    a utility function to clarify the specified question. It returns the 
    clarification result or an error message if the process fails.

    Parameters:
    ----------
    recieved : pemodel.ClarificationRequestRecieved
        An object containing the question that needs clarification.

    Returns:
    -------
    dict
        A dictionary containing the clarification result or an error message 
        if an exception occurs during processing.
    """

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
async def calculate_overall_progress(recieved: pemodel.ChatHistoryRequestRecieved) -> dict:
    """
    Calculates overall progress metrics from chat history.

    This asynchronous function retrieves chat history data from the database and 
    calculates overall progress metrics using a utility function. It returns the 
    calculated results or an error message if the process fails.

    Parameters:
    ----------
    recieved : pemodel.ChatHistoryRequestRecieved
        An object containing the necessary information to fetch chat history.

    Returns:
    -------
    dict
        A dictionary containing the calculated overall progress metrics or an 
        error message if an exception occurs during processing.
    """
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
