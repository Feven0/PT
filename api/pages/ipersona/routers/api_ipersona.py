import os, time, json, sys
import uuid
curdir = os.path.dirname(os.path.realpath(__file__))
cpath = os.path.dirname(curdir)
if not cpath in sys.path:
    sys.path.append(cpath) 
from fastapi import APIRouter, BackgroundTasks
from fastapi import FastAPI, File, UploadFile, Form, Request
from fastapi.responses import JSONResponse
import api.modules.ipersona_parrot_gpt as util
from fastapi import FastAPI
from fastapi import UploadFile, Form
from fastapi.responses import StreamingResponse
import api.llm.ipersona.ipersona_schema as db
import api.llm.ipersona.ipersona_gpt as gpt
import api.llm.ipersona.ipersona_prisma as prisma
import api.llm.ipersona.ipersona_db as database
from api.llm.ipersona.ipersona_agent import agents
import api.pages.ipersona.models.persona as pemodel
import assemblyai as aai
import ast
from openai import OpenAI

hr_agent = agents()

uploaded_files = []
hr_persona = []

# load_dotenv("../.env")
# ASSEMBLYAI_API_KEY= os.getenv("ASSEMBLYAI_API_KEY")
aai.settings.api_key = config.assemblyai.api_key
transcriber = aai.Transcriber()


routes = FastAPI(openapi_prefix="/api")

module_dir= os.path.dirname(__file__)
module_di= os.path.dirname(__file__)
data_path = lambda x: os.path.join(module_dir, "folders", x)
prompt_path = lambda x: os.path.join(module_di, "data/prompts", x)


OPENAI_API_KEY = config.openai.api_key

client = OpenAI(api_key=OPENAI_API_KEY)


import time, asyncio
from openai import OpenAI
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from api.services.strapi_ipersona import IpersonaManager
from io import BytesIO

app = FastAPI()

@routes.post("/strapi_db_test")
async def strapi_methods():
    try:
        ipersona_manager = IpersonaManager(sessionId=32, alluser=16, jobId=1045, run_stage="dev")
        # data = ipersona_manager.get_messages()
        # data = ipersona_manager.get_observers()
        # data = ipersona_manager.get_alluser_sessions()
        data = ipersona_manager.get_job_sessions_observers()
        # data = ipersona_manager.get_job_sessions()
        # data = ipersona_manager.update_session_status()
        # data = ipersona_manager.get_session()

        # message_data = {
        #         "attributes": {
        #             "message": {
        #                 "user_type": "candidate",
        #                 "content_type": "answer",
        #                 "content": {
        #                     "response": "data['response']",
        #                     "time_taken": "data['time_taken']",
        #                     "realtime_evaluation": "null"
        #                 }
        #             },
        #         },
        #         "metadata": {
        #             "createdBy": "parrot"
        #         }
        #     }

        # data = ipersona_manager.insert_message(message_data)
        
        # Print or return the fetched data
        # print("###########")
        # print(data)
        
        # message_data = {
        #     "attributes": {
        #         "message": "Test message",
        #         "evaluation": "Good"
        #     },
        #     "metadata": {
        #         "createdBy": "User123"
        #     }
        # }

        # data = ipersona_manager.insert_message(message_data)
        # print(data)        
        
        return data
    
    except Exception as e:
        print(f"Error processing files: {e}")
    except Exception as e:
        print(f"Error processing files: {e}")
        return {"error": str(e)}

@routes.post("/synthesize-audio/")
async def synthesize_audio(recieved: pemodel.audioRequestRecieved):
    print('Received text for synthesis:', recieved.text)
    
    # Call the audio synthesis client
    response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=recieved.text
    )
    print("Error in audio synthesis:", response)


    # Check if the response is successful
    if not response:
        print("Error in audio synthesis:", response)
        return {"error": "Failed to synthesize audio"}

    # Read the audio data directly (no await)
    audio_data = response.read()  # Remove await if not async
    # print("audddddddddio data")
    # print(audio_data)
    # Create an audio stream
    audio_stream = BytesIO(audio_data)
    # print("audiiiiiiiii  stream")
    # print(audio_stream)
    # Ensure stream is reset to the start
    audio_stream.seek(0)
    print("lassstttttt")
    print(audio_stream.seek(0))

    print("Audio stream created successfully")
    return StreamingResponse(audio_stream, media_type="audio/mpeg")


@routes.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    try:
        audio_path  = os.path.join(data_path('audio'), file.filename)
        with open(audio_path, "wb") as f:
            contents = await file.read()
            f.write(contents)
            
            
        print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
        # audio_file = await file.read()
        
        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_path
        )
        return {"transcription": transcription.text}
    except Exception as e:
        print(f"Error processing files: {e}")

import io

@routes.post("/synthesize")
async def synthesize_text(text: str):
    print("Received text for synthesis:", text)
    try:
        response = client.audio.speech.with_streaming_response.create(
            model="tts-1",
            voice="alloy",
            input=text
        )

        # If response is a single audio byte stream
        audio_data = response  # Adjust based on if response is async
        
        audio_stream = io.BytesIO(audio_data)

        return StreamingResponse(audio_stream, media_type="audio/mpeg")
    except Exception as e:
        print(f"Error processing files: {e}")
        return {"error": str(e)}

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
        print("##########persona.txt############")
        generated_persona = prompt_text\
                .replace("{hr_persona}", created_persona)\
                .replace("{job_description}", str(recieved.jbJson))\
                .replace("{profile}", str(recieved.cvJson))    
                
        
        message = util.file_reader(prompt_path('generate_question.txt'))
        print("##########generate.txt############")
        context = str(message)
        
        msg=context\
            .replace("{background_count}", str(2))\
            .replace("{technical_count}", str(2))\
            .replace("{behavioral_count}", str(2))\
            .replace("{ability_count}", str(2))
        
        # hr_agent.assistant.update_system_message(generated_persona)
        # response = await hr_agent.generate_question(msg)
        
        content = generated_persona + msg
        response = gpt.openai_gpt_assistant_without_streaming(content)
        generated_question_json = util.extract_json(response, quite=False)
        
        question_number = 1
        for category, questions in generated_question_json.items():
            for question in questions:
                question["question_number"] = str(question_number)  
                question_number += 1 
        combined_generated_question_json = json.dumps(generated_question_json, indent=4)
       

        #------------- Save to DB ---------------        
        # data = {
        #     "alluser": str(recieved.userId),
        #     "userId": str(recieved.userId),
        #     "jobId": str(recieved.jobId),
        #     "username": recieved.name,
        #     "persona": generated_persona ,
        #     "generated_questions": str(combined_generated_question_json)
        # }     
        
        
        message_data = {
            "slug": str(uuid.uuid4()),
            "attributes": {
                "alluser": recieved.userId,
                "jobId": recieved.jobId,
                "username": recieved.name,
                "persona": generated_persona,
                "generated_questions": generated_question_json
            },
            "metadata": {
                "createdBy": "parrot"
            }
        }

        ipersona_manager = IpersonaManager(run_stage="dev")

        response = ipersona_manager.create_session(message_data)           
   
        # response = await db.create_sechema(data)
        # response = await prisma.create_session(data)
        #------------- ---------------------- 

        return response
    
    except Exception as e:
        print(f"Error processing files: {e}")
        return JSONResponse(status_code=500, content={"error": "Error processing files"})
        
        
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


@routes.post("/calculate_session_overall_progress")
async def calculate_overall_progress(recieved: pemodel.UserSessionRequestRecieved) -> dict:
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
        ipersona_manager = IpersonaManager(sessionId=recieved.alluser, jobId=recieved.jobId, run_stage="dev")
        session_chatobserver = ipersona_manager.get_job_sessions_observers()
                            
        result =  util.calculate_overall_progress(session_chatobserver) 
        return result
    
    except Exception as e:
        print(f"Error processing files: {e}")
        return JSONResponse(status_code=500, content={"error": "Error processing files"})

    finally:
        end_time = time.time() 
        elapsed_time = end_time - start_time 
        print(f"Time taken for Analysis processing: {elapsed_time:.2f} seconds")


@routes.post("/calculate_allstat_progress")
async def calculate_allstat_progress(recieved: pemodel.AllUserSessionRequestRecieved) -> dict:
    """
    Calculates overall users progress metrics for all job types.

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
        ipersona_manager = IpersonaManager(sessionId=recieved.alluser, run_stage="dev")
        session_chatobserver = ipersona_manager.get_alluser_sessions()                  
        result =  util.all_session_jobs_average_metrics(session_chatobserver) 
        return result
    
    except Exception as e:
        print(f"Error processing files: {e}")
        return JSONResponse(status_code=500, content={"error": "Error processing files"})

    finally:
        end_time = time.time() 
        elapsed_time = end_time - start_time 
        print(f"Time taken for Analysis processing: {elapsed_time:.2f} seconds")
