import api.llm.ipersona.ipersona_schema as db
import api.llm.ipersona.ipersona_db as database
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi import FastAPI, File, UploadFile, Form, Request
from fastapi.responses import StreamingResponse, JSONResponse
from api.llm.ipersona.ipersona_strapi_schemas import IpersonaSessionSchema, IpersonaTraineeSchema, IpersonaJobSchema, IpersonaSessionOverallObserverSchema, IpersonaSessionMessageSchema, IpersonaSessionObserverSchema
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
        ipersona_user = IpersonaTraineeSchema()
        trainee_profile_data = ipersona_user.filter_by_alluser_id(all_user_id=recieved.all_user_id, nopp=True, dataframe=False)
        if not trainee_profile_data:
                logger.warn("No trainee user profiles found.")
                return []
        tinder_user_profile_id = trainee_profile_data[0]['id']
        tinder_user_profile_data = util.extract_trainee_neccessary_values(trainee_profile_data)
        
        ipersona_job = IpersonaJobSchema()
        tinder_job_data = ipersona_job.filter_by_job_id(job_profile_id=recieved.job_profile_id, nopp=True, dataframe=False)
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
        

        session_data = {
            "slug": str(f"all_user_id: {recieved.all_user_id}"), 
            "status": "Incomplete",
            "attributes": {
                "persona": generated_persona,  
                "generated_questions": generated_question_json
            },
            "user_profile_id": tinder_user_profile_id,
            "job_profile_id": recieved.job_profile_id
        }

          
        ipersona_session = IpersonaSessionSchema()
        saved_session = ipersona_session.save_session(params=session_data, return_object=True, nopp=True, dataframe=False)
        if saved_session:
            logger.success("Session saved and created successfully!")
            
        return saved_session
    
    except Exception as e:
        logger.error(f"Error processing files: {e}")
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
        logger.error(f"Error processing files: {e}")
        return JSONResponse(status_code=500, content={"error": "Error processing files"})

    finally:
        end_time = time.time() 
        elapsed_time = end_time - start_time 
        logger.info(f"Time taken for question clarififcation processing: {elapsed_time:.2f} seconds")


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
        ipersona_overall = IpersonaSessionOverallObserverSchema()
        ipersona_user = IpersonaTraineeSchema()

        trainee_profile_data = ipersona_user.filter_by_alluser_id(all_user_id=recieved.all_user_id, nopp=True, dataframe=False)
        if not trainee_profile_data:
                logger.warn("No trainee user profiles found.")
                return []
        tinder_user_profile_id = trainee_profile_data[0]['id']        
        session_chatobserver = ipersona_overall.filter_by_with_user_and_job_id(user_profile_id=tinder_user_profile_id, job_profile_id=recieved.job_profile_id, nopp=True, dataframe=False)
                            
        return session_chatobserver["all_sessions"][0]
    
    except Exception as e:
        logger.error(f"Error processing files: {e}")
        return JSONResponse(status_code=500, content={"error": "Error processing files"})

    finally:
        end_time = time.time() 
        elapsed_time = end_time - start_time 
        logger.info(f"Time taken for Analysis processing: {elapsed_time:.2f} seconds")


@routes.post("/calculate_allstat_progress")
async def calculate_allstat_progress(recieved: pemodel.AllUserSessionRequestRecieved):
    """
    Calculates overall users progress metrics for all job types.

    This asynchronous function retrieves chat history data from the database and 
    calculates overall progress metrics using a utility function. It returns the 
    calculated results or an error message if the process fails.

    Parameters:
    ----------
    recieved : pemodel.SessionIdRequestRecieved
        An object containing the necessary information to fetch chat history.

    Returns:
    -------
    dict
        A dictionary containing the calculated overall progress metrics or an 
        error message if an exception occurs during processing.
    """
    start_time = time.time()    
    try:  
        ipersona_overall = IpersonaSessionOverallObserverSchema()
        ipersona_user = IpersonaTraineeSchema()

        trainee_profile_data = ipersona_user.filter_by_alluser_id(all_user_id=recieved.all_user_id, nopp=True, dataframe=False)
        if not trainee_profile_data:
                logger.warn("No trainee user profiles found.")
                return []
        tinder_user_profile_id = trainee_profile_data[0]['id'] 
        
        session_chatobserver = ipersona_overall.filter_by_tinder_user_profile_id(user_profile_id=tinder_user_profile_id, nopp=True, dataframe=False)
        result =  util.all_session_jobs_average_metrics(session_chatobserver) 
        return result
    
    except Exception as e:
        logger.error(f"Error processing files: {e}")
        return JSONResponse(status_code=500, content={"error": "Error processing files"})

    finally:
        end_time = time.time() 
        elapsed_time = end_time - start_time 
        logger.info(f"Time taken for Analysis processing: {elapsed_time:.2f} seconds")


@routes.post("/engagement_jobs_status")
async def calculate_engagement_jobs_status(recieved: pemodel.AllUserSessionRequestRecieved):
    """
    """
    start_time = time.time()    
    try:  
        ipersona_user = IpersonaTraineeSchema()

        trainee_profile_data = ipersona_user.filter_by_alluser_id(all_user_id=recieved.all_user_id, nopp=True, dataframe=False)
        if not trainee_profile_data:
                logger.warn("No trainee user profiles found.")
                return []
        tinder_user_profile_id = trainee_profile_data[0]['id'] 
                
        result = util.summarize_interviews(tinder_user_profile_id) 
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
        ipersona_session = IpersonaSessionSchema()
        data = ipersona_session.get_all_sessions(nopp=True, dataframe=False)
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
        ipersona_session = IpersonaSessionSchema()
        data = ipersona_session.get_all_sessions(nopp=True, dataframe=False)
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
        ipersona_user = IpersonaTraineeSchema()

        trainee_profile_data = ipersona_user.filter_by_alluser_id(all_user_id=recieved.all_user_id, nopp=True, dataframe=False)
        if not trainee_profile_data:
                logger.warn("No trainee user profiles found.")
                return []
        tinder_user_profile_id = trainee_profile_data[0]['id'] 
                                              
        ipersona_session = IpersonaSessionSchema()
        user_data = ipersona_session.filter_by_with_user_job_id(user_profile_id=tinder_user_profile_id, job_profile_id=recieved.job_profile_id, nopp=True, dataframe=False)

        return user_data
    
    except Exception as e:
        logger.error(f"Error processing files: {e}")
        return JSONResponse(status_code=500, content={"error": "Error processing files"})
   
   
@routes.post("/fetch_chat_history")
async def fetch_chat_history(recieved: pemodel.SessionIdRequestRecieved):  
    """
    Fetches the chat history from the database.

    This asynchronous function retrieves all chat history associated with the 
    specified session.

    Parameters:
    ----------
    recieved : pemodel.SessionIdRequestRecieved
        An object containing the necessary information to fetch the chat history.

    Returns:
    -------
    list
        A list containing the chat history for the session, or None if an 
        exception occurs during processing.
    """
    try:
        ipersona_message = IpersonaSessionMessageSchema()
        session_chathistory = ipersona_message.filter_by_session_id(sessionId=recieved.sessionId, nopp=True, dataframe=False, sort='asc')
  
        return session_chathistory

    except Exception as e:
        logger.error(f"Error fetching chat history: {e}")
        return None  
    
    except Exception as e:
        print(f"Error processing files: {e}")
        return JSONResponse(status_code=500, content={"error": "Error processing files"})
    
@routes.post("/fetch_user_all_observer")
async def fetch_user_all_observer(recieved: pemodel.SessionIdRequestRecieved):  
    try:
        ipersona_observer = IpersonaSessionObserverSchema()
        session_chatobserver = ipersona_observer.filter_by_observer_session_id(sessionId=recieved.sessionId, nopp=True, dataframe=False)
        return session_chatobserver

    except Exception as e:
        logger.error(f"Error fetching chat observer: {e}")
        return None  
    
    except Exception as e:
        logger.error(f"Error processing files: {e}")
        return JSONResponse(status_code=500, content={"error": "Error processing files"})
    
@routes.post("/fetch_single_session")
async def fetch_single_session(recieved: pemodel.SessionIdRequestRecieved):  
    try:        
        ipersona_user = IpersonaSessionSchema()
        session_fetched = ipersona_user.get_session_by_id(sessionId=recieved.sessionId, nopp=True, dataframe=False)
        return session_fetched

    except Exception as e:
        logger.error(f"Error fetching single session: {e}")
        return None  
    
    except Exception as e:
        logger.error(f"Error processing files: {e}")
        return JSONResponse(status_code=500, content={"error": "Error processing files"})