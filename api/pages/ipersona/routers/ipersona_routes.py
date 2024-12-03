import api.llm.ipersona.ipersona_schema as db
import api.llm.ipersona.ipersona_db as database
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi import FastAPI, File, UploadFile, Form, Request
from fastapi.responses import StreamingResponse, JSONResponse
import api.modules.ipersona_parrot_gpt as util
import api.llm.ipersona.ipersona_gpt as gpt
import api.pages.ipersona.models.persona as pemodel
import time, os
from api.services.secret import get_auth
import assemblyai as aai
from api.services.strapi_ipersona import IpersonaManager
from api.utils.logger import LLPackerLogger

logger = LLPackerLogger(os.path.basename(__file__))
module_dir= os.path.dirname(__file__)
module_di= os.path.dirname(__file__)
data_path = lambda x: os.path.join(module_dir, "folders", x)
prompt_path = lambda x: os.path.join(module_di, "data/prompts", x)

aai.settings.api_key = "49e5f82458584a70b847f477a035ce48"
transcriber = aai.Transcriber()

routes = FastAPI(root_path="/api")

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
async def user_session_files(recieved: pemodel.UserSessionRequestRecieved):
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
        ipersona_manager = IpersonaManager(alluserId=recieved.alluserId, run_stage="dev")
        trainee_profile_data = ipersona_manager.get_trainee_user_profile()
        if not trainee_profile_data:
                logger.warn("No trainee user profiles found.")
                return []
        tinder_user_profile_id = trainee_profile_data[0]['id']
        tinder_user_profile_data = util.extract_trainee_neccessary_values(trainee_profile_data)
        
        tinder_job_data = ipersona_manager.get_trainee_job_profile()
        if not tinder_job_data:
                logger.warn("No Job data found.")
                return []
        tinder_job_data = util.extract_job_neccessary_values(tinder_job_data)
 
        
        created_persona = util.create_persona(str(tinder_job_data))
        prompt_text = util.file_reader(prompt_path('persona.txt'))
        generated_persona = prompt_text\
                .replace("{hr_persona}", created_persona)\
                .replace("{job_description}", str(tinder_job_data))\
                .replace("{profile}", str(tinder_user_profile_data))    
                
        
        message = util.file_reader(prompt_path('generate_question.txt'))
        context = str(message)
        
        msg=context\
            .replace("{background_count}", str(2))\
            .replace("{technical_count}", str(2))\
            .replace("{behavioral_count}", str(2))\
            .replace("{ability_count}", str(2))
                
        content = generated_persona + msg
        response = gpt.openai_gpt_assistant_without_streaming(content)
        generated_question_json = util.extract_json(response, quite=False)
        
        question_number = 1
        for category, questions in generated_question_json.items():
            for question in questions:
                question["question_number"] = str(question_number)  
                question_number += 1 
        

        message_data = {
            "slug": str(f"all_user_id: {recieved.alluserId}"), 
            "attributes": {
                "persona": generated_persona,  
                "generated_questions": generated_question_json
            },
            "metadata": {
                "createdBy": "parrot"
            },
            "alluserId": tinder_user_profile_id,
            "jobId": recieved.jobId
        }


        ipersona_manager = IpersonaManager(run_stage="dev")

        response = ipersona_manager.create_session(message_data)           

        return response
    
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


@routes.post("/calculate_session_overall_progress")
async def calculate_overall_progress(recieved: pemodel.UserSessionRequestRecieved):
    """
    Fetch overall progress metrics for a job.
    Returns:
    -------
    dict
        A dictionary containing the overall progress metrics or an 
        error message if an exception occurs during processing.
    """
    start_time = time.time()    
    try:  
        ipersona_manager = IpersonaManager(alluserId=recieved.alluserId, jobId=recieved.jobId, run_stage="dev")
        session_chatobserver = ipersona_manager.session_overall_observer_by_user_and_job()
                            
        return session_chatobserver["all_sessions"][0]
    
    except Exception as e:
        print(f"Error processing files: {e}")
        return JSONResponse(status_code=500, content={"error": "Error processing files"})

    finally:
        end_time = time.time() 
        elapsed_time = end_time - start_time 
        print(f"Time taken for Analysis processing: {elapsed_time:.2f} seconds")


@routes.post("/calculate_allstat_progress")
async def calculate_allstat_progress(recieved: pemodel.AllUserSessionRequestRecieved):
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
        ipersona_manager = IpersonaManager(alluserId=recieved.alluserId, run_stage="dev")
        session_chatobserver = ipersona_manager.session_overall_observer_by_user()
               
        result =  util.all_session_jobs_average_metrics(session_chatobserver) 
        return result
    
    except Exception as e:
        print(f"Error processing files: {e}")
        return JSONResponse(status_code=500, content={"error": "Error processing files"})

    finally:
        end_time = time.time() 
        elapsed_time = end_time - start_time 
        print(f"Time taken for Analysis processing: {elapsed_time:.2f} seconds")


@routes.post("/engagement_jobs_status")
async def calculate_engagement_jobs_status(recieved: pemodel.AllUserSessionRequestRecieved):
    """
    """
    start_time = time.time()    
    try:                 
        result =  util.summarize_interviews(recieved.alluserId) 
        return result
    
    except Exception as e:
        logger.error(f"Error processing files: {e}")
        return JSONResponse(status_code=500, content={"error": "Error processing files"})

    finally:
        end_time = time.time() 
        elapsed_time = end_time - start_time 
        logger.info(f"Time taken for Analysis processing: {elapsed_time:.2f} seconds")

@routes.post("/admin_overview_status")
async def calculate_admin_data_status():
    """
    """
    start_time = time.time()    
    try:      
        ipersona_manager = IpersonaManager(run_stage="dev")

        data = ipersona_manager.get_all_sessions()
        result = util.calculate_session_metrics(data)           
        return result
    
    except Exception as e:
        logger.error(f"Error processing files: {e}")
        return JSONResponse(status_code=500, content={"error": "Error processing files"})

    finally:
        end_time = time.time() 
        elapsed_time = end_time - start_time 
        logger.info(f"Time taken for Analysis processing: {elapsed_time:.2f} seconds")

@routes.post("/admin_user_data")
async def calculate_admin_user_data():
    """
    """
    start_time = time.time()    
    try:      
        ipersona_manager = IpersonaManager(run_stage="dev")

        data = ipersona_manager.get_all_sessions()
        result = util.summarize_allusers_data(data)        
        return result
    
    except Exception as e:
        logger.error(f"Error processing files: {e}")
        return JSONResponse(status_code=500, content={"error": "Error processing files"})

    finally:
        end_time = time.time() 
        elapsed_time = end_time - start_time 
        logger.info(f"Time taken for Analysis processing: {elapsed_time:.2f} seconds")


@routes.post("/fetch_user_session")
async def fetch_session(recieved: pemodel.UserSessionRequestRecieved):
    """
    Fetches user session data from the database.

    This asynchronous function retrieves the session data for a given user ID 
    and processes the latest data, particularly handling generated questions.

    Parameters:
    ----------
    recieved : pemodel.SessionRequestRecieved
        An object containing the user ID for which the session data is to be fetched.

    Returns:
    -------
    dict
        A dictionary containing all user data and the latest user data, or an 
        error response if an exception occurs during processing.
    """
    try:
        ipersona_manager = IpersonaManager(alluserId=recieved.alluserId, jobId=recieved.jobId, run_stage="dev")
        user_data = ipersona_manager.get_job_sessions()

        return user_data
    
    except Exception as e:
        print(f"Error processing files: {e}")
        return JSONResponse(status_code=500, content={"error": "Error processing files"})
   
   
@routes.post("/fetch_chat_history")
async def fetch_chat_history(recieved: pemodel.ChatHistoryRequestRecieved):  
    """
    Fetches the chat history from the database.

    This asynchronous function retrieves all chat history associated with the 
    specified session.

    Parameters:
    ----------
    recieved : pemodel.ChatHistoryRequestRecieved
        An object containing the necessary information to fetch the chat history.

    Returns:
    -------
    list
        A list containing the chat history for the session, or None if an 
        exception occurs during processing.
    """
    try:
        ipersona_manager = IpersonaManager(sessionId=recieved.sessionId, run_stage="dev")
        session_chathistory = ipersona_manager.get_messages()
  
        return session_chathistory

    except Exception as e:
        print(f"Error fetching chat history: {e}")
        return None  
    
    except Exception as e:
        print(f"Error processing files: {e}")
        return JSONResponse(status_code=500, content={"error": "Error processing files"})
    

@routes.post("/fetch_user_session_observers")
async def fetch_user_session_observer(recieved: pemodel.UserSessionRequestRecieved):  
    try:
        ipersona_manager = IpersonaManager(sessionId=recieved.alluser, jobId=recieved.jobId, run_stage="dev")
        session_chatobserver = ipersona_manager.get_job_sessions()
         
        return session_chatobserver

    except Exception as e:
        print(f"Error fetching chat observer: {e}")
        return None  
    
    except Exception as e:
        print(f"Error processing files: {e}")
        return JSONResponse(status_code=500, content={"error": "Error processing files"})
    
@routes.post("/fetch_user_all_observer")
async def fetch_user_all_observer(recieved: pemodel.ChatHistoryRequestRecieved):  
    try:
        ipersona_manager = IpersonaManager(sessionId=recieved.sessionId, run_stage="dev")
        session_chatobserver = ipersona_manager.get_observers()
         
        return session_chatobserver

    except Exception as e:
        print(f"Error fetching chat observer: {e}")
        return None  
    
    except Exception as e:
        print(f"Error processing files: {e}")
        return JSONResponse(status_code=500, content={"error": "Error processing files"})
    
@routes.post("/fetch_single_session")
async def fetch_single_session(recieved: pemodel.ChatHistoryRequestRecieved):  
    try:
        ipersona_manager = IpersonaManager(sessionId=recieved.sessionId, run_stage="dev")
        session_fetched = ipersona_manager.get_session()
         
        return session_fetched

    except Exception as e:
        print(f"Error fetching chat observer: {e}")
        return None  
    
    except Exception as e:
        print(f"Error processing files: {e}")
        return JSONResponse(status_code=500, content={"error": "Error processing files"})