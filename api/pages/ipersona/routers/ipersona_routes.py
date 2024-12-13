
import time, os
import assemblyai as aai
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi import FastAPI, File, UploadFile, Form, Request
from fastapi.responses import JSONResponse

#
from api import config
from api.llm.ipersona.ipersona_strapi_schemas import (
    IpersonaSessionSchema, 
    IpersonaTraineeSchema, 
    IpersonaJobSchema, 
    IpersonaSessionOverallObserverSchema, 
    IpersonaSessionMessageSchema, 
    IpersonaSessionObserverSchema
)
import api.modules.ipersona_parrot_gpt as util
import api.llm.ipersona.ipersona_gpt as gpt
import api.pages.ipersona.models.persona as pemodel
from api.utils.logger import LLPackerLogger

logger = LLPackerLogger(os.path.basename(__file__))
module_dir= os.path.dirname(__file__)
data_path = lambda x: os.path.join(module_dir, "folders", x)
prompt_path = lambda x: os.path.join(module_dir, "data/prompts", x)

aai.settings.api_key = config.assemblyai.api_key
transcriber = aai.Transcriber()

routes = FastAPI(root_path="/api")

@routes.post("/audio_upload")
async def speech_to_text(file: UploadFile = File(...)) -> dict:
    """
    Converts audio file to text using a speech-to-text assembly transcriber.

    This asynchronous function processes an uploaded audio file, saves it to a 
    specified location, and uses an assembly transcriber to convert the audio to text. 
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
    start_time = time.time()  # Track processing time
    try:
        logger.info("Starting audio processing...")
        
        audio_path = os.path.join(data_path('audio'), file.filename)
        logger.debug(f"Saving audio file to: {audio_path}")
        
        with open(audio_path, "wb") as f:
            contents = await file.read()
            f.write(contents)
        logger.info("Audio file saved successfully.")
        
        transcriber = aai.Transcriber()
        transcript = transcriber.transcribe(audio_path)

        if transcript.status == aai.TranscriptStatus.error:
            logger.error(f"Transcription error: {transcript.error}")
            return {"error": transcript.error}
        else:
            logger.info("Transcription completed successfully.")
            logger.debug(f"Transcription text: {transcript.text}")
            return {"transcription": transcript.text}
    
    except Exception as e:
        logger.error(f"An error occurred during transcription: {str(e)}", exc_info=True)
        return JSONResponse(
            content={
                "system": f"Something went wrong! {str(e)}",
                "transcript": "Failed"
            }
        )
    
    finally:
        end_time = time.time()
        elapsed_time = end_time - start_time
        logger.info(f"Time taken for audio upload and processing: {elapsed_time:.2f} seconds")

@routes.post("/create_user_session")
async def user_session_files(recieved: pemodel.UserSessionRequestRecieved):
    """
    Processes user session files and generates interview questions.

    This asynchronous function saves user profile data, creates a persona 
    from job descriptions, and generates questions using an HR agent. It 
    stores the session data in a database and returns a success message.

    Parameters:
    ----------
    recieved : pemodel.UserSessionRequestRecieved
        An object containing user session information including job description, 
        user profile, and user ID.

    Returns:
    -------
    dict
        A dictionary containing a success message with the uploaded filenames 
        or an error response if an exception occurs during processing.
    """
    try:
        logger.info("Starting user session file processing...")

        # Step 1: Fetch trainee profile data
        ipersona_user = IpersonaTraineeSchema()
        trainee_profile_data = ipersona_user.filter_by_alluser_id(
            all_user_id=recieved.all_user_id, nopp=True, dataframe=False
        )

        if not trainee_profile_data:
            logger.warn(f"No trainee user profiles found for all_user_id: {recieved.all_user_id}.")
            return JSONResponse(status_code=404, content={"error": "No trainee user profiles found"})

        tinder_user_profile_id = trainee_profile_data['id']
        tinder_user_profile_data = util.extract_trainee_neccessary_values(trainee_profile_data)
        logger.info(f"Tinder user profile data extracted for user ID: {tinder_user_profile_id}")

        # Step 2: Fetch job profile data
        ipersona_job = IpersonaJobSchema()
        tinder_job_data = ipersona_job.filter_by_job_id(
            job_profile_id=recieved.job_profile_id, nopp=True, dataframe=False
        )

        if not tinder_job_data:
            logger.warn(f"No job data found for job_profile_id: {recieved.job_profile_id}.")
            return JSONResponse(status_code=404, content={"error": "No job data found"})

        tinder_job_data = util.extract_job_neccessary_values(tinder_job_data)
        logger.info(f"Tinder job data extracted for job_profile_id: {recieved.job_profile_id}")

        # Step 3: Create persona and generate questions
        created_persona = util.create_persona(str(tinder_job_data))
        prompt_text = util.file_reader(prompt_path('persona.txt'))
        generated_persona = prompt_text \
            .replace("{hr_persona}", created_persona) \
            .replace("{job_description}", str(tinder_job_data)) \
            .replace("{profile}", str(tinder_user_profile_data))

        message = util.file_reader(prompt_path('generate_question.txt'))
        context = str(message)
        msg = context \
            .replace("{background_count}", str(2)) \
            .replace("{technical_count}", str(2)) \
            .replace("{behavioral_count}", str(2)) \
            .replace("{ability_count}", str(2))

        content = generated_persona + msg
        response = gpt.openai_gpt_assistant_without_streaming(content)
        generated_question_json = util.extract_json(response, quite=False)
        logger.info("Persona and questions generated successfully.")

        # Step 4: Add question numbers
        question_number = 1
        for category, questions in generated_question_json.items():
            for question in questions:
                question["question_number"] = str(question_number)
                question_number += 1

        # Step 5: Save session data
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
        saved_session = ipersona_session.save_session(
            params=session_data, return_object=True, nopp=True, dataframe=False
        )

        if saved_session:
            logger.info("Session saved and created successfully!")
            return saved_session
        else:
            logger.error("Failed to save session.")
            return JSONResponse(status_code=500, content={"error": "Failed to save session"})

    except Exception as e:
        logger.error(f"Error processing user session files: {e}", exc_info=True)
        return JSONResponse(status_code=500, content={"error": f"Error processing files: {str(e)}"})

        
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

    if not question or not isinstance(question, str):
        logger.error("Invalid or missing question in request.")
        return JSONResponse(status_code=400, content={"error": "Invalid or missing question."})

    try:
        result = await util.clarify_question(question)

        if not result or not isinstance(result, dict):
            logger.warn(f"Clarification result is invalid or empty for question: {question}")
            return JSONResponse(status_code=500, content={"error": "Clarification result is invalid."})

        logger.info(f"Clarification successful for question: {question}")
        return result

    except KeyError as e:
        logger.error(f"Key error during clarification: {str(e)} for question: {question}")
        return JSONResponse(status_code=500, content={"error": f"Key error: {str(e)}"})

    except TypeError as e:
        logger.error(f"Type error during clarification: {str(e)} for question: {question}")
        return JSONResponse(status_code=500, content={"error": f"Type error: {str(e)}"})

    except Exception as e:
        logger.error(f"Unexpected error during question clarification: {str(e)} for question: {question}")
        return JSONResponse(status_code=500, content={"error": f"An unexpected error occurred: {str(e)}"})

    finally:
        end_time = time.time()
        elapsed_time = end_time - start_time
        logger.info(f"Time taken for question clarification processing: {elapsed_time:.2f} seconds")


@routes.post("/calculate_session_overall_progress")
async def calculate_overall_progress(received: pemodel.UserSessionRequestRecieved):
    """
    Fetch overall progress metrics for a job.

    Parameters:
    ----------
    received : pemodel.UserSessionRequestRecieved
        The request object containing user and job profile data.

    Returns:
    -------
    JSONResponse or dict
        A dictionary containing the overall progress metrics, or an error message if an exception occurs.
    """
    start_time = time.time()
    try:
        ipersona_overall = IpersonaSessionOverallObserverSchema()
        ipersona_user = IpersonaTraineeSchema()

        trainee_profile_data = ipersona_user.filter_by_alluser_id(all_user_id=received.all_user_id, nopp=True, dataframe=False)
        if not trainee_profile_data:
            logger.warn(f"No trainee profiles found for user_id: {received.all_user_id}")
            return JSONResponse(status_code=404, content={"error": "No trainee profiles found."})

        tinder_user_profile_id = trainee_profile_data.get('id', None)
        if not tinder_user_profile_id:
            logger.error(f"Trainee profile missing 'id' for user_id: {received.all_user_id}")
            return JSONResponse(status_code=500, content={"error": "Trainee profile is invalid."})

        session_chatobserver = ipersona_overall.filter_by_with_user_and_job_id(
            user_profile_id=tinder_user_profile_id,
            job_profile_id=received.job_profile_id,
            nopp=True,
            dataframe=False
        )

        if "all_sessions" not in session_chatobserver or not session_chatobserver["all_sessions"]:
            logger.warn(f"No session data found for user_profile_id: {tinder_user_profile_id}, job_profile_id: {received.job_profile_id}")
            return JSONResponse(status_code=404, content={"error": "No session overall observer data found."})

        logger.info(f"Successfully fetched overall session data for user_profile_id: {tinder_user_profile_id}, job_profile_id: {received.job_profile_id}")
        return session_chatobserver["all_sessions"][0]

    except KeyError as e:
        logger.error(f"Key error during session progress calculation: {str(e)}")
        return JSONResponse(status_code=500, content={"error": f"Key error: {str(e)}"})

    except TypeError as e:
        logger.error(f"Type error during session progress calculation: {str(e)}")
        return JSONResponse(status_code=500, content={"error": f"Type error: {str(e)}"})

    except Exception as e:
        logger.error(f"Unexpected error during session progress calculation: {str(e)}")
        return JSONResponse(status_code=500, content={"error": f"Unexpected error: {str(e)}"})

    finally:
        end_time = time.time()
        elapsed_time = end_time - start_time
        logger.info(f"Time taken for analysis processing: {elapsed_time:.2f} seconds")

@routes.post("/calculate_allstat_progress")
async def calculate_allstat_progress(recieved: pemodel.AllUserSessionRequestRecieved):
    """
    Calculates overall users' progress metrics for all job types.

    This asynchronous function retrieves chat history data from the database and 
    calculates overall progress metrics using a utility function. It returns the 
    calculated results or an error message if the process fails.

    Parameters:
    ----------
    recieved : pemodel.AllUserSessionRequestRecieved
        An object containing the necessary information to fetch chat history.

    Returns:
    -------
    dict
        A dictionary containing the calculated overall progress metrics or an 
        error message if an exception occurs during processing.
    """
    start_time = time.time()

    if not recieved or not isinstance(recieved, pemodel.AllUserSessionRequestRecieved):
        logger.error("Invalid request format.")
        return JSONResponse(status_code=400, content={"error": "Invalid request format."})

    try:
        ipersona_overall = IpersonaSessionOverallObserverSchema()
        ipersona_user = IpersonaTraineeSchema()

        trainee_profile_data = ipersona_user.filter_by_alluser_id(all_user_id=recieved.all_user_id, 
                                                                  nopp=True, dataframe=False)

        if not trainee_profile_data or not isinstance(trainee_profile_data, dict) or len(trainee_profile_data) == 0:
            logger.warn(f"No trainee user profiles found for all_user_id: {recieved.all_user_id}")
            return JSONResponse(status_code=404, content={"error": "No trainee user profiles found."})

        tinder_user_profile_id = trainee_profile_data.get('id')
        if not tinder_user_profile_id:
            logger.error("Missing tinder_user_profile_id in trainee profile data.")
            return JSONResponse(status_code=500, content={"error": "Error fetching user profile."})

        session_chatobserver = ipersona_overall.filter_by_tinder_user_profile_id(user_profile_id=tinder_user_profile_id, nopp=True, dataframe=False)
        if not session_chatobserver or not isinstance(session_chatobserver, list) or len(session_chatobserver) == 0:
            logger.warn(f"No session data found for user_profile_id: {tinder_user_profile_id}")
            return JSONResponse(status_code=404, content={"error": "No session data found."})

        result = util.all_session_jobs_average_metrics(session_chatobserver)
        if not result or not isinstance(result, dict):
            logger.warn(f"Failed to calculate metrics for user_profile_id: {tinder_user_profile_id}")
            return JSONResponse(status_code=500, content={"error": "Error calculating progress metrics."})

        logger.info(f"Progress metrics successfully calculated for user_profile_id: {tinder_user_profile_id}")
        return result

    except KeyError as e:
        logger.error(f"KeyError while processing request: {str(e)} for all_user_id: {recieved.all_user_id}")
        return JSONResponse(status_code=500, content={"error": f"KeyError: {str(e)}"})

    except TypeError as e:
        logger.error(f"TypeError while processing request: {str(e)} for all_user_id: {recieved.all_user_id}")
        return JSONResponse(status_code=500, content={"error": f"TypeError: {str(e)}"})

    except Exception as e:
        logger.error(f"Unexpected error during processing: {str(e)} for all_user_id: {recieved.all_user_id}")
        return JSONResponse(status_code=500, content={"error": f"Unexpected error occurred: {str(e)}"})

    finally:
        end_time = time.time()
        elapsed_time = end_time - start_time
        logger.info(f"Time taken for overall progress calculation: {elapsed_time:.2f} seconds")

@routes.post("/engagement_jobs_status")
def calculate_engagement_jobs_status(recieved: pemodel.AllUserSessionRequestRecieved):
    """
    Calculate engagement jobs status based on the user profile data.

    This synchronous function fetches trainee profile data using the user ID, summarizes 
    interview engagement status, and returns the result. The function logs detailed information 
    and handles any errors that occur during processing.

    Parameters:
    ----------
    recieved : pemodel.AllUserSessionRequestRecieved
        An object containing user session information including the user ID.

    Returns:
    -------
    dict
        A dictionary containing the summarized interview engagement status or an error response 
        if an exception occurs during processing.
    """
    start_time = time.time()
    
    try:
        logger.info(f"Starting engagement jobs status calculation for all_user_id: {recieved.all_user_id}")

        # Step 1: Fetch trainee profile data
        ipersona_user = IpersonaTraineeSchema()
        trainee_profile_data = ipersona_user.filter_by_alluser_id(
            all_user_id=recieved.all_user_id, nopp=True, dataframe=False
        )

        if not trainee_profile_data:
            logger.warn(f"No trainee user profiles found for all_user_id: {recieved.all_user_id}")
            return JSONResponse(status_code=404, content={"error": "No trainee user profiles found"})
        
        tinder_user_profile_id = trainee_profile_data['id']
        logger.info(f"Tinder user profile data extracted for user ID: {tinder_user_profile_id}")

        # Step 2: Summarize interview engagement status
        result = util.summarize_interviews(tinder_user_profile_id)
        logger.info(f"Interview engagement summary completed for user ID: {tinder_user_profile_id}")

        return result

    except Exception as e:
        logger.error(f"Error processing files for all_user_id: {recieved.all_user_id}: {str(e)}", exc_info=True)
        return JSONResponse(status_code=500, content={"error": f"Error processing files: {str(e)}"})

    finally:
        # Step 3: Log elapsed time
        end_time = time.time()
        elapsed_time = end_time - start_time
        logger.info(f"Time taken for engagement jobs status processing: {elapsed_time:.2f} seconds")

@routes.post("/admin_overview_status")
async def calculate_admin_data_status():
    """
    Calculates admin data status by fetching session data and processing metrics.
    
    This asynchronous function retrieves all session data, calculates the session metrics, 
    and returns the results. If any exception occurs, it logs the error and returns an 
    error response.
    
    Returns:
    -------
    dict
        A dictionary containing the calculated session metrics or an error response if an 
        exception occurs during processing.
    """
    start_time = time.time()

    try:
        logger.info("Starting admin data status calculation...")

        # Step 1: Fetch all session data
        ipersona_session = IpersonaSessionSchema()
        data = ipersona_session.get_all_sessions(nopp=True, dataframe=False)

        if not data:
            logger.warn("No session data found.")
            return JSONResponse(status_code=404, content={"error": "No session data found"})

        logger.info(f"Session data retrieved successfully. Processing {len(data)} sessions.")

        # Step 2: Calculate session metrics
        result = util.calculate_session_metrics(data)
        logger.info("Session metrics calculated successfully.")

        return result

    except Exception as e:
        logger.error(f"Error processing admin data: {str(e)}", exc_info=True)
        return JSONResponse(status_code=500, content={"error": f"Error processing files: {str(e)}"})

    finally:
        # Step 3: Log the elapsed time for the process
        end_time = time.time()
        elapsed_time = end_time - start_time
        logger.info(f"Time taken for admin data status processing: {elapsed_time:.2f} seconds")

@routes.post("/admin_user_data")
async def calculate_admin_data_status():
    """
    Calculate admin data status by processing all sessions and computing session metrics.

    This asynchronous function fetches all session data, calculates session metrics, 
    and returns the result. It logs detailed information throughout the process and handles 
    any errors that occur during the computation.

    Returns:
    -------
    dict
        A dictionary containing session metrics or an error response if an exception occurs.
    """
    start_time = time.time()

    try:
        logger.info("Starting admin data status calculation.")

        # Step 1: Fetch all session data
        ipersona_session = IpersonaSessionSchema()
        data = ipersona_session.get_all_sessions(nopp=True, dataframe=False)

        if not data:
            logger.warn("No session data found.")
            return JSONResponse(status_code=404, content={"error": "No session data found"})

        logger.info("Session data retrieved successfully.")

        # Step 2: Calculate session metrics
        result = util.calculate_session_metrics(data)
        logger.info("Session metrics calculated successfully.")

        return result

    except Exception as e:
        logger.error(f"Error processing admin data status: {str(e)}", exc_info=True)
        return JSONResponse(status_code=500, content={"error": f"Error processing files: {str(e)}"})

    finally:
        # Step 3: Log elapsed time
        end_time = time.time()
        elapsed_time = end_time - start_time
        logger.info(f"Time taken for admin data status processing: {elapsed_time:.2f} seconds")

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
    start_time = time.time()
    
    try:
        logger.info(f"Fetching session data for user ID: {recieved.all_user_id}")

        # Step 1: Retrieve trainee profile data
        ipersona_user = IpersonaTraineeSchema()
        trainee_profile_data = ipersona_user.filter_by_alluser_id(all_user_id=recieved.all_user_id, nopp=True, dataframe=False)

        if not trainee_profile_data:
            logger.warn(f"No trainee user profiles found for user ID: {recieved.all_user_id}")
            return JSONResponse(status_code=404, content={"error": "No trainee user profiles found"})
        
        logger.info(f"Trainee profile data retrieved for user ID: {recieved.all_user_id}")

        # Step 2: Extract user profile ID
        tinder_user_profile_id = trainee_profile_data['id']
         
        # Step 3: Fetch session data by user and job ID
        ipersona_session = IpersonaSessionSchema()
        user_data = ipersona_session.filter_by_with_user_job_id(
            user_profile_id=tinder_user_profile_id,
            job_profile_id=recieved.job_profile_id,
            nopp=True, 
            dataframe=False
        )

        if not user_data:
            logger.warn(f"No session data found for user ID: {recieved.all_user_id} and job ID: {recieved.job_profile_id}")
            return JSONResponse(status_code=404, content={"error": "No session data found"})

        logger.info(f"Session data successfully retrieved for user ID: {recieved.all_user_id} and job ID: {recieved.job_profile_id}")
        
        return user_data

    except Exception as e:
        logger.error(f"Error processing session data for user ID: {recieved.all_user_id} - {str(e)}", exc_info=True)
        return JSONResponse(status_code=500, content={"error": f"Error processing files: {str(e)}"})

    finally:
        # Step 4: Log elapsed time for processing
        end_time = time.time()
        elapsed_time = end_time - start_time
        logger.info(f"Time taken to fetch session data for user ID {recieved.all_user_id}: {elapsed_time:.2f} seconds")

   
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
        A list containing the chat history for the session, or an error response 
        if an exception occurs during processing.
    """
    start_time = time.time()

    try:
        logger.info(f"Fetching chat history for session ID: {recieved.sessionId}")

        # Step 1: Fetch chat history from the database
        ipersona_message = IpersonaSessionMessageSchema()
        session_chathistory = ipersona_message.filter_by_session_id(
            sessionId=recieved.sessionId, 
            nopp=True, 
            dataframe=False, 
            sort='asc'
        )

        if not session_chathistory:
            logger.warn(f"No chat history found for session ID: {recieved.sessionId}")
            return JSONResponse(status_code=404, content={"error": "No chat history found"})

        logger.info(f"Successfully fetched chat history for session ID: {recieved.sessionId}")
        return session_chathistory

    except Exception as e:
        logger.error(f"Error fetching chat history for session ID {recieved.sessionId}: {str(e)}", exc_info=True)
        return JSONResponse(status_code=500, content={"error": f"Error fetching chat history: {str(e)}"})

    finally:
        # Step 2: Log the elapsed time for the process
        end_time = time.time()
        elapsed_time = end_time - start_time
        logger.info(f"Time taken for fetching chat history: {elapsed_time:.2f} seconds")

@routes.post("/fetch_user_all_observer")
async def fetch_user_all_observer(recieved: pemodel.SessionIdRequestRecieved):  
    """
    Fetches all observers for a given session from the database.

    This asynchronous function retrieves all observer data associated with 
    the specified session.

    Parameters:
    ----------
    recieved : pemodel.SessionIdRequestRecieved
        An object containing the necessary information to fetch the observer data.

    Returns:
    -------
    list
        A list containing the observer data for the session, or an error response 
        if an exception occurs during processing.
    """
    start_time = time.time()

    try:
        logger.info(f"Fetching observers for session ID: {recieved.sessionId}")

        # Step 1: Fetch session observers from the database
        ipersona_observer = IpersonaSessionObserverSchema()
        session_chatobserver = ipersona_observer.filter_by_observer_session_id(
            sessionId=recieved.sessionId, 
            nopp=True, 
            dataframe=False
        )

        if not session_chatobserver:
            logger.warn(f"No observers found for session ID: {recieved.sessionId}")
            return JSONResponse(status_code=404, content={"error": "No observers found"})

        logger.info(f"Successfully fetched observers for session ID: {recieved.sessionId}")
        return session_chatobserver

    except Exception as e:
        logger.error(f"Error fetching observers for session ID {recieved.sessionId}: {str(e)}", exc_info=True)
        return JSONResponse(status_code=500, content={"error": f"Error fetching observers: {str(e)}"})

    finally:
        # Step 2: Log the elapsed time for the process
        end_time = time.time()
        elapsed_time = end_time - start_time
        logger.info(f"Time taken for fetching observers: {elapsed_time:.2f} seconds")

@routes.post("/fetch_single_session")
async def fetch_single_session(recieved: pemodel.SessionIdRequestRecieved):  
    """
    Fetches a single session from the database.

    This asynchronous function retrieves the session data associated with the
    specified session ID.

    Parameters:
    ----------
    recieved : pemodel.SessionIdRequestRecieved
        An object containing the necessary session ID information.

    Returns:
    -------
    dict
        A dictionary containing session data or an error response if an
        exception occurs during processing.
    """
    start_time = time.time()

    try:
        logger.info(f"Fetching session data for session ID: {recieved.sessionId}")

        # Step 1: Fetch session data by session ID from the database
        ipersona_user = IpersonaSessionSchema()
        session_fetched = ipersona_user.get_session_by_id(
            sessionId=recieved.sessionId, 
            nopp=True, 
            dataframe=False
        )

        if not session_fetched:
            logger.warn(f"No session found for session ID: {recieved.sessionId}")
            return JSONResponse(status_code=404, content={"error": "Session not found"})

        logger.info(f"Successfully fetched session data for session ID: {recieved.sessionId}")
        return session_fetched

    except Exception as e:
        logger.error(f"Error fetching session data for session ID {recieved.sessionId}: {str(e)}", exc_info=True)
        return JSONResponse(status_code=500, content={"error": f"Error fetching session: {str(e)}"})

    finally:
        # Step 2: Log the elapsed time for the process
        end_time = time.time()
        elapsed_time = end_time - start_time
        logger.info(f"Time taken for fetching session data: {elapsed_time:.2f} seconds")
