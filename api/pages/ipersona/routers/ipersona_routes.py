import time, os
import assemblyai as aai
from fastapi import FastAPI, File, UploadFile, Form, Request, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Dict, List, Any, Union
import threading
import uuid

from api import config
from api.llm.ipersona.ipersona_strapi_schemas import (
    IpersonaSessionSchema, 
    IpersonaTraineeSchema, 
    IpersonaJobSchema, 
    IpersonaSessionOverallObserverSchema, 
    IpersonaSessionMessageSchema, 
    IpersonaSessionObserverSchema,
    IpersonaTinderTemplateSchema,
    IpersonaSessionTinderUserReactionSchema,
    IpersonaChallengeDocumentSchema,
    IpersonaSessionTinderUserJobMatchSchema
)
import api.modules.ipersona_parrot_gpt as util
import api.llm.ipersona.ipersona_gpt as gpt
import api.pages.ipersona.models.persona as pemodel
from api.utils.logger import LLPackerLogger
import api.llm.ipersona.ipersona_strapi as strapi
settings = config.settings


logger = LLPackerLogger(os.path.basename(__file__))
module_dir= os.path.dirname(__file__)
data_path = lambda x: os.path.join(module_dir, "folders", x)
prompt_path = lambda x: os.path.join(module_dir, "data/prompts", x)

aai.settings.api_key = config.assemblyai.api_key
transcriber = aai.Transcriber()

routes = FastAPI(
    root_path="/api",
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.PROJECT_VERSION,
    redoc=settings.REDOC_ENABLED,
    debug=False
    )

# In-memory status store (for demonstration; replace with persistent store for production)
audio_processing_status = {}

@routes.get("/health", tags=["Health Check"])
async def health_check():
    try:
        sessionId = 1879
        mode = 'Chat'
        run_stage = 'dev'
        updated_mode = util.updating_session_mode(sessionId, mode, run_stage)
        return updated_mode
    except Exception as e:
        logger.error(f"Error in health check: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Health check failed: {str(e)}"}
        )


@routes.post("/audio_upload", tags=["Audio Endpoints"])
async def speech_to_text(file: UploadFile = File(...)) -> dict:
    """
    Convert an audio file to text using a speech-to-text service.
    
    Processes an uploaded audio file, saves it to the specified location,
    and uses an Assembly AI transcriber to convert the audio to text.
    
    Parameters
    ----------
    file : UploadFile
        The audio file uploaded by the user.
        
    Returns
    -------
    Union[List, Dict]
        A dictionary containing:
        - 'transcription': The transcribed text or "Failed" on error
        - 'status': HTTP status code (200 for success, 400 for transcription error)
        - 'message': Empty string on success or error message
        
    Raises
    ------
    Exception
        If any error occurs during file handling or transcription
    """
    if not file or not file.filename:
        logger.error("Invalid file: No file or filename provided")
        return JSONResponse(
            status_code=400,
            content={
                "transcription": "Failed",
                "status": 400,
                "message": "No file provided or invalid file"
            }
        )
        
    try:
        logger.info(f"Starting audio processing for file: {file.filename}")
        
        # Create directory if it doesn't exist
        audio_dir = data_path('audio')
        os.makedirs(audio_dir, exist_ok=True)
        
        audio_path = os.path.join(audio_dir, file.filename)
        logger.debug(f"Saving audio file to: {audio_path}")
        
        # Save the uploaded file
        contents = await file.read()
        with open(audio_path, "wb") as f:
            f.write(contents)
        logger.info("Audio file saved successfully")
        
        # Initialize transcriber and process file
        transcriber = aai.Transcriber()
        transcript = transcriber.transcribe(audio_path)

        if transcript.status == aai.TranscriptStatus.error:
            error_msg = getattr(transcript, 'error', 'Unknown transcription error')
            logger.error(f"Transcription error: {error_msg}")
            return {
                "transcription": "Failed",
                "status": 400, 
                "message": error_msg
            }
            
        logger.info("Transcription completed successfully")
        logger.debug(f"Transcription text: {transcript.text}")
        return {
            "transcription": transcript.text,
            "status": 200, 
            "message": ""
        }
    
    except Exception as e:
        logger.error(f"Error during transcription: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "transcription": "Failed",
                "status": 500,
                "message": f"System error: {str(e)}"
            }
        )

@routes.post("/update_session_mode",  tags=["Session Endpoints"])
async def update_session_mode(request: pemodel.UpdateSessionModeRequestReceieved):
    try:
        sessionId = request.sessionId
        mode = request.mode
        run_stage = request.run_stage
        updated_mode = util.updating_session_mode(sessionId, mode, run_stage)
        return updated_mode
    
    except Exception as e:
        logger.error(f"Error in health check: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Health check failed: {str(e)}"}
        )
       
@routes.post("/create_user_session", tags=["Session Endpoints"])
async def user_session_files(request: pemodel.UserSessionRequestRecieved):
    """
    Process user session data and generate interview questions.

    Parameters
    ----------
    request : pemodel.UserSessionRequestRecieved
        Object containing:
        - all_user_id
        - job_profile_id
        - template, challenge, etc.

    Returns
    -------
    Dict[str, Any]
        Session data (ID, status, template_id, challenge_id)
    """
    run_stage = request.run_stage
    mode = request.mode
    template = request.template
    external = request.external
    challenge = request.challenge
    job_profile_id = request.job_profile_id
    all_user_id = request.all_user_id
    template_id = request.template_id
    challenge_id = request.challenge_id

    try:
        logger.info(f"Starting user session creation for user ID: {all_user_id}, job ID: {job_profile_id}")

        # Step 1: Fetch user profile data
        tinder_user_profile_data, tinder_user_profile_id = util.get_user_data(all_user_id, run_stage)
        # Step 2: Fetch job profile data
        tinder_job_data = util.get_job_data(job_profile_id, run_stage)
        
        session_incomplete = util.check_if_session_exists(
            run_stage, 
            tinder_user_profile_id, 
            job_profile_id,
            challenge_id,
            template_id)
        
        if session_incomplete:
            logger.info(f"Incomplete session already exists for user ID: {all_user_id}")
            return session_incomplete
        else:
            response = await util.create_session_logics(
                request,
                mode,
                run_stage, 
                template, 
                external, 
                challenge, 
                job_profile_id, 
                all_user_id, 
                template_id, 
                challenge_id,
                tinder_user_profile_id,
                tinder_job_data, 
                tinder_user_profile_data)
            
            return response
    except Exception as e:
        logger.error(f"Error creating user session: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": f"Error processing user session: {str(e)}"}
        )
       
@routes.post("/clarify", tags=["Session Endpoints"])
async def clarify_question(request: pemodel.ClarificationRequestRecieved) -> dict:
    """
    Clarifies a given question using a clarification utility.

    This asynchronous function processes a clarification request by calling 
    a utility function to clarify the specified question. It returns the 
    clarification result or an error message if the process fails.

    Parameters:
    ----------
    request : pemodel.ClarificationRequestRecieved
        An object containing the question that needs clarification.

    Returns:
    -------
    dict
        A dictionary containing the clarification result or an error message 
        if an exception occurs during processing.
    """
    question = request.question
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

    finally:
        end_time = time.time()
        elapsed_time = end_time - start_time
        logger.info(f"Time taken for question clarification processing: {elapsed_time:.2f} seconds")

@routes.post("/delete_session", tags=["Session Endpoints"])
async def delete_interview_session(request: pemodel.SessionIdRequestRecieved):
    """
    Mark an interview session as deleted.
    
    Updates the session status to 'Deleted' in the database without 
    physically removing the record.
    
    Parameters
    ----------
    request : pemodel.SessionIdRequestRecieved
        Object containing the session ID to be marked as deleted
        
    Returns
    -------
    JSONResponse
        Success message or error response
        
    Raises
    ------
    Exception
        If any error occurs during the update process
    """
    run_stage = request.run_stage

    if not request or not request.sessionId:
        logger.error("Missing session ID in request")
        return JSONResponse(
            status_code=400,
            content={"error": "Session ID is required"}
        )
        
    try:
        logger.info(f"Marking session as deleted, session ID: {request.sessionId}")
        
        ipersona_session = IpersonaSessionSchema(run_stage=run_stage)
        session_data = {
            "i_persona_session_id": request.sessionId, 
            "status": "Deleted",
        }
        
        updated_session = ipersona_session.update_session(
            params=session_data, 
            nopp=True, 
            dataframe=False, 
            return_object=True
        )
        
        if not updated_session:
            logger.warn(f"Session not found or could not be updated: {request.sessionId}")
            return JSONResponse(
                status_code=404, 
                content={"error": "Session not found or could not be updated"}
            )
            
        logger.info(f"Session status updated to 'Deleted' for session ID: {request.sessionId}")
        return JSONResponse(
            status_code=200, 
            content={"success": "Session deleted successfully"}
        )
  
    except Exception as e:
        logger.error(f"Error deleting session {request.sessionId}: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500, 
            content={"error": f"Error deleting session: {str(e)}"}
        )

@routes.post("/close_session", tags=["Session Endpoints"])
async def close_interview_session(request: pemodel.ClosedDataRequestRecieved):
    """
    Close an interview session and perform final evaluations.
    
    Processes session data, calculates final metrics, and updates session status to 'Closed'.
    
    Parameters
    ----------
    request : pemodel.ClosedDataRequestRecieved
        Object containing the session data needed for evaluation
        
    Returns
    -------
    JSONResponse
        Success message with evaluation results or error response
        
    Raises
    ------
    Exception
        If any error occurs during the evaluation process
    """
    run_stage = request.run_stage

    if not request or not request.data:
        logger.error("Missing session data in request")
        return JSONResponse(
            status_code=400, 
            content={"error": "Session data is required"}
        )
        
    try:
        logger.info("Processing session closure and final evaluation")
        
        response = await util.overall_interview_evaluations(run_stage, request.data, status="Closed")
        
        if not response:
            logger.warn("Session evaluation returned empty response")
            return JSONResponse(
                status_code=500,
                content={"error": "Failed to generate evaluation results"}
            )
            
        logger.info("Session closed and evaluated successfully")
        return JSONResponse(
            status_code=200, 
            content={"success": response}
        )
  
    except Exception as e:
        logger.error(f"Error closing session: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500, 
            content={"error": f"Error closing session: {str(e)}"}
        )

@routes.post("/calculate_session_overall_progress", tags=["Session Endpoints"])
async def calculate_overall_progress(request: pemodel.OverallRequestRecieved):
    """
    Fetch overall progress metrics for a job.

    Parameters:
    ----------
    request : pemodel.OverallRequestRecieved

    Returns:
    -------
    JSONResponse or dict
    """
    run_stage = request.run_stage
    job_profile_id = request.job_profile_id
    challenge_id = request.challenge_id
    all_user_id = request.all_user_id

    try:
        ipersona_overall = IpersonaSessionOverallObserverSchema(run_stage=run_stage)
        ipersona_user = IpersonaTraineeSchema(run_stage=run_stage)

        trainee_profile_data = ipersona_user.filter_by_alluser_id(
            all_user_id=all_user_id, 
            nopp=True,
            dataframe=False)

        if not trainee_profile_data:
            logger.warn(f"No trainee profiles found for user_id: {all_user_id}")
            return JSONResponse(status_code=200, content={"message": "No trainee profiles found by the given all_user_id"})

        tinder_user_profile_id = trainee_profile_data.get('id')
        if not tinder_user_profile_id:
            logger.error(f"Trainee profile missing 'id' for user_id: {all_user_id}")
            return JSONResponse(status_code=500, content={"error": "Trainee profile is invalid."})

        session_chatobserver = None

        if job_profile_id:
            session_chatobserver = ipersona_overall.filter_by_with_user_and_job_id(
                user_profile_id=tinder_user_profile_id,
                job_profile_id=job_profile_id,
                nopp=True,
                dataframe=False)
        elif challenge_id:
            session_chatobserver = ipersona_overall.filter_by_with_user_and_challenge_id(
                user_profile_id=tinder_user_profile_id,
                challenge_id=challenge_id,
                nopp=True,
                dataframe=False)

        if not session_chatobserver or "all_sessions" not in session_chatobserver or not session_chatobserver["all_sessions"]:
            logger.warn(f"No session data found for user_profile_id: {tinder_user_profile_id}")
            return JSONResponse(status_code=200, content={"message": "No session overall observer data found."})

        logger.info(f"Successfully fetched session data for user_profile_id: {tinder_user_profile_id}")
        return session_chatobserver["all_sessions"][0]

    except Exception as e:
        logger.error(f"Unexpected error during session progress calculation: {str(e)}")
        return JSONResponse(status_code=500, content={"error": f"Unexpected error: {str(e)}"})

@routes.post("/calculate_allstat_progress", tags=["Session Endpoints"])
async def calculate_allstat_progress(request: pemodel.AllUserIdRecieved):
    """
    Calculates overall users' progress metrics for all job types.

    This asynchronous function retrieves chat history data from the database and 
    calculates overall progress metrics using a utility function. It returns the 
    calculated results or an error message if the process fails.

    Parameters:
    ----------
    request : pemodel.AllUserIdRecieved
        An object containing the necessary information to fetch chat history.

    Returns:
    -------
    dict
        A dictionary containing the calculated overall progress metrics or an 
        error message if an exception occurs during processing.
    """
    run_stage = request.run_stage

    if not request or not isinstance(request, pemodel.AllUserIdRecieved):
        logger.error("Invalid request format.")
        return JSONResponse(status_code=400, content={"error": "Invalid request format."})

    try:
        ipersona_overall = IpersonaSessionOverallObserverSchema(run_stage=run_stage)
        ipersona_user = IpersonaTraineeSchema(run_stage=run_stage)

        trainee_profile_data = ipersona_user.filter_by_alluser_id(all_user_id=request.all_user_id, 
                                                                  nopp=True, dataframe=False)

        if not trainee_profile_data or not isinstance(trainee_profile_data, dict) or len(trainee_profile_data) == 0:
            logger.warn(f"No trainee user profiles found for all_user_id: {request.all_user_id}")
            return JSONResponse(status_code=200, content={"message": "No trainee user profiles found for the give all_user_id."})

        tinder_user_profile_id = trainee_profile_data.get('id')
        if not tinder_user_profile_id:
            logger.error("Missing tinder_user_profile_id in trainee profile data.")
            return JSONResponse(status_code=500, content={"error": "Error fetching user profile."})

        session_chatobserver = ipersona_overall.filter_by_tinder_user_profile_id(
            user_profile_id=tinder_user_profile_id, 
            nopp=True,
            dataframe=False
            )

        if not session_chatobserver or not isinstance(session_chatobserver, list) or len(session_chatobserver) == 0:
            logger.warn(f"No session data found for user_profile_id: {tinder_user_profile_id}")
            return JSONResponse(status_code=200, content={"message": "Session data empty"})

        result = util.all_session_jobs_average_metrics(session_chatobserver)

        if not result or not isinstance(result, dict):
            logger.warn(f"Failed to calculate metrics for user_profile_id: {tinder_user_profile_id}")
            return JSONResponse(status_code=500, content={"error": "Error calculating progress metrics."})

        logger.info(f"Progress metrics successfully calculated for user_profile_id: {tinder_user_profile_id}")
        return result

    except Exception as e:
        logger.error(f"Unexpected error during processing: {str(e)} for all_user_id: {request.all_user_id}")
        return JSONResponse(status_code=500, content={"error": f"Unexpected error occurred: {str(e)}"})

@routes.post("/engagement_jobs_status", tags=["Session Endpoints"])
def calculate_engagement_jobs_status(request: pemodel.AllUserSessionRequestRecieved):
    """
    Calculate interview engagement status for a user across all job types.
    
    Retrieves and summarizes a user's engagement with interview sessions for
    different job categories.
    
    Parameters
    ----------
    request : pemodel.AllUserSessionRequestRecieved
        Object containing:
        - all_user_id: User identifier
        - filter: Optional query filters
        - return_skip: Flag to include skipped items
        - information_level: Detail level for results
        - since: Starting point for pagination
        - limit: Maximum number of items to return
        - cursor: Pagination cursor
        
    Returns
    -------
    Dict[str, Any]
        Engagement summary data or error response
    """
    run_stage = request.run_stage

    if not request or not request.all_user_id:
        logger.error("Invalid request: Missing user ID")
        return {
            "all_user_id": [],
            "jobs": [],
            "cursor": [],
            "status": 400,
            "message": "User ID is required"
        }
        
    try:
        logger.info(f"Calculating engagement status for user ID: {request.all_user_id}")
        
        # Step 1: Fetch trainee profile data
        
        ipersona_user = IpersonaTraineeSchema(run_stage=run_stage)
        trainee_profile_data = ipersona_user.filter_by_alluser_id(
            all_user_id=request.all_user_id, 
            nopp=True, 
            dataframe=False
        )
        
        if not trainee_profile_data:
            logger.warn(f"No trainee profiles found for user ID: {request.all_user_id}")
            return {
                "all_user_id": request.all_user_id,
                "jobs": [],
                "cursor": [],
                "status": 404,
                "message": "No trainee profiles found for the given user ID"
            }
        
        tinder_user_profile_id = trainee_profile_data.get('id')

        if not tinder_user_profile_id:
            logger.error(f"Invalid trainee profile for user ID: {request.all_user_id}")
            return {
                "all_user_id": request.all_user_id,
                "jobs": [],
                "cursor": [],
                "status": 500,
                "message": "Invalid trainee profile data"
            }
            
        # Step 2: Process request parameters with defaults
        query_filter = request.filter or {}
        return_skip = request.return_skip
        information_level = request.information_level
        since = max(request.since, 1)  # Ensure minimum value of 1
        limit = max(request.limit, 1)  # Ensure minimum value of 1
        cursor = request.cursor

        # Step 3: Fetch and summarize interview data
        data, cursor = util.summarize_interviews(
            run_stage,                                                 
            tinder_user_profile_id, 
            filter=query_filter,
            cursor=cursor, 
            since=since, 
            limit=limit,
            information_level=information_level,
            return_skip=return_skip            
        )

        logger.info(f"Interview engagement summary completed for user ID: {request.all_user_id}")

        
        # Step 4: Prepare response
        # if data:
        return {
            "all_user_id": request.all_user_id,
            "jobs": data, 
            # "cursor": cursor,                  
            "status": 200, 
            "message": ""
        }
        # else: 
        #     return {
        #         "all_user_id": request.all_user_id, 
        #         "jobs": [],  
        #         "cursor": [],
        #         "status": 404, 
        #         "message": "No data found with the given parameters"
        #     }

    except Exception as e:
        logger.error(f"Error calculating engagement status: {str(e)}", exc_info=True)
        return {
            "all_user_id": request.all_user_id if hasattr(request, 'all_user_id') else [], 
            "jobs": [],  
            "cursor": [],
            "status": 500, 
            "message": str(e)
        }

@routes.post("/engagement_challenge_status", tags=["Session Endpoints"])
def calculate_engagement_challenge_status(request: pemodel.AllUserSessionRequestRecieved):
    """
    Calculate interview engagement status for a user across all challenges.
    
    Retrieves and summarizes a user's engagement with interview sessions for
    different job categories.
    
    Parameters
    ----------
    request : pemodel.AllUserSessionRequestRecieved
        Object containing:
        - all_user_id: User identifier
        - filter: Optional query filters
        - return_skip: Flag to include skipped items
        - information_level: Detail level for results
        - since: Starting point for pagination
        - limit: Maximum number of items to return
        - cursor: Pagination cursor
        
    Returns
    -------
    Dict[str, Any]
        Engagement summary data or error response
    """
    run_stage = request.run_stage

    if not request or not request.all_user_id:
        logger.error("Invalid request: Missing user ID")
        return {
            "all_user_id": [],
            "challenges": [],
            "status": 400,
            "message": "User ID is required"
        }
        
    try:
        logger.info(f"Calculating engagement status for user ID: {request.all_user_id}")
        
        # Step 1: Fetch trainee profile data
        ipersona_user = IpersonaTraineeSchema(run_stage=run_stage)
        trainee_profile_data = ipersona_user.filter_by_alluser_id(
            all_user_id=request.all_user_id, 
            nopp=True, 
            dataframe=False
        )
        
        if not trainee_profile_data:
            logger.warn(f"No trainee profiles found for user ID: {request.all_user_id}")
            return {
                "all_user_id": request.all_user_id,
                "challenges": [],
                "status": 404,
                "message": "No trainee profiles found for the given user ID"
            }
        
        tinder_user_profile_id = trainee_profile_data.get('id')

        if not tinder_user_profile_id:
            logger.error(f"Invalid trainee profile for user ID: {request.all_user_id}")
            return {
                "all_user_id": request.all_user_id,
                "challenges": [],
                "status": 500,
                "message": "Invalid trainee profile data"
            }
            
        # Step 2: Process request parameters with defaults
        query_filter = request.filter or {}
        return_skip = request.return_skip
        information_level = request.information_level
        since = max(request.since, 1)  # Ensure minimum value of 1
        limit = max(request.limit, 1)  # Ensure minimum value of 1
        cursor = request.cursor

        # Step 3: Fetch and summarize interview data
        data, cursor = util.summarize_challenge_interviews(
            run_stage,                                                 
            tinder_user_profile_id, 
            filter=query_filter,
            cursor=cursor, 
            since=since, 
            limit=limit,
            information_level=information_level,
            return_skip=return_skip            
        )

        logger.info(f"Interview engagement summary completed for user ID: {request.all_user_id}")

        
        # Step 4: Prepare response
        # if data:
        return {
            "all_user_id": request.all_user_id,
            "challenges": data, 
            "status": 200, 
            "message": ""
        }

    except Exception as e:
        logger.error(f"Error calculating engagement status: {str(e)}", exc_info=True)
        return {
            "all_user_id": request.all_user_id if hasattr(request, 'all_user_id') else [], 
            "challenges": [],  
            "status": 500, 
            "message": str(e)
        }

@routes.post("/engagement_status", tags=["Session Endpoints"])
def calculate_engagement_challenge_status(request: pemodel.AllUserSessionRequestRecieved):
    run_stage = request.run_stage

    if not request or not request.all_user_id:
        logger.error("Invalid request: Missing user ID")
        return {
            "all_user_id": [],
            "jobs": [],
            "cursor": [],
            "status": 400,
            "message": "User ID is required"
        }
        
    try:
        logger.info(f"Calculating engagement status for user ID: {request.all_user_id}")
        
        # Step 1: Fetch trainee profile data
        ipersona_user = IpersonaTraineeSchema(run_stage=run_stage)
        trainee_profile_data = ipersona_user.filter_by_alluser_id(
            all_user_id=request.all_user_id, 
            nopp=True, 
            dataframe=False
        )
        
        if not trainee_profile_data:
            logger.warn(f"No trainee profiles found for user ID: {request.all_user_id}")
            return {
                "all_user_id": request.all_user_id,
                "jobs": [],
                "cursor": [],
                "status": 404,
                "message": "No trainee profiles found for the given user ID"
            }
        
        tinder_user_profile_id = trainee_profile_data.get('id')

        if not tinder_user_profile_id:
            logger.error(f"Invalid trainee profile for user ID: {request.all_user_id}")
            return {
                "all_user_id": request.all_user_id,
                "jobs": [],
                "cursor": [],
                "status": 500,
                "message": "Invalid trainee profile data"
            }
            
        # Step 2: Process request parameters with defaults
        query_filter = request.filter or {}
        return_skip = request.return_skip
        information_level = request.information_level
        since = max(request.since, 1)  # Ensure minimum value of 1
        limit = max(request.limit, 1)  # Ensure minimum value of 1
        cursor = request.cursor

        # Step 3: Fetch and summarize interview data
        data, cursor = util.summarize(
            run_stage,                                                 
            tinder_user_profile_id, 
            filter=query_filter,
            cursor=cursor, 
            since=since, 
            limit=limit,
            information_level=information_level,
            return_skip=return_skip            
        )

        logger.info(f"Interview engagement summary completed for user ID: {request.all_user_id}")
        
        # Step 4: Prepare response
        return {
            "all_user_id": request.all_user_id,
            "jobs": data, 
            # "cursor": cursor,                  
            "status": 200, 
            "message": ""
        }

    except Exception as e:
        logger.error(f"Error calculating engagement status: {str(e)}", exc_info=True)
        return {
            "all_user_id": request.all_user_id if hasattr(request, 'all_user_id') else [], 
            "jobs": [],  
            "cursor": [],
            "status": 500, 
            "message": str(e)
        }

              
@routes.post("/admin_overview_status", tags=["Admin Endpoints"])
async def calculate_admin_overview_status(request: pemodel.AdminDataFiltering) -> Union[List, Dict]:
    """
    Calculate an overview of all interview sessions for administrative purposes.
    
    Retrieves and processes session data with optional filtering to produce
    administrative metrics and insights.
    
    Parameters
    ----------
    request : pemodel.AdminDataFiltering
        Object containing:
        - filter: Optional query filters
        - return_skip: Flag to include skipped items
        - information_level: Detail level for results
        - since: Starting point for pagination
        - limit: Maximum number of items to return
        - cursor: Pagination cursor
        
    Returns
    -------
    Union[List, Dict]
        Administrative overview metrics or error response with the format:
        {
            "data": list,
            "cursor": list,
            "status": int,
            "message": str
        }
    """
    try:
        run_stage = request.run_stage

        logger.info("Calculating admin overview status")
        
        # Process request parameters
        # query_filter = request.filter or {}
        # since = max(request.since or 1, 1)  # Ensure minimum value of 1
        # limit = max(request.limit or 1, 1)  # Ensure minimum value of 1
        # cursor = request.cursor
        
        # # Prepare query parameters
        # kwargs = query_filter.copy() if query_filter else {}
        
        # Fetch session data with pagination
        ipersona_session = IpersonaSessionSchema(run_stage=run_stage)
        # data, cursor = ipersona_session.get_all_sessions(
        #     cursor=cursor, 
        #     since=request.since, 
        #     limit=request.limit, 
        #     nopp=True, 
        #     dataframe=False,
        #     # **kwargs
        # )
        data = ipersona_session.get_alladmin_sessions(
            # cursor=cursor, 
            since=request.since, 
            limit=request.limit, 
            nopp=True, 
            dataframe=False,
            # **kwargs
        )
        
        if not data:
            logger.warn("No session data found for admin overview")
            return {
                "data": [],  
                "cursor": [],
                "status": 404, 
                "message": "No data found with the given parameters"
            }

        logger.info(f"Processing admin overview metrics for {len(data)} sessions")
        
        # Calculate and format metrics
        result = util.calculate_session_metrics(data)
        # result = util.add_columns(result, kind='admin_overview', **kwargs)
        
        logger.info("Admin overview status calculated successfully")
        return {
            "data": result, 
            # "cursor": cursor,                  
            "status": 200, 
            "message": ""
        }

    except Exception as e:
        logger.error(f"Error calculating admin overview status: {str(e)}", exc_info=True)
        return {
            "data": [],  
            "cursor": [],
            "status": 500, 
            "message": f"Error processing data: {str(e)}"
        }

@routes.post("/admin_allusers_data", tags=["Admin Endpoints"])
async def calculate_admin_allusers_data(request: pemodel.AdminDataFiltering) -> Union[List, Dict]:
    """
    Calculate administrative data for all users by processing session data.

    Fetches all session data based on provided filters, calculates metrics,
    and returns summarized results for all users.

    Parameters
    ----------
    request : pemodel.AdminDataFiltering
        Object containing:
        - filter: Optional query filters
        - return_skip: Flag to include skipped items
        - information_level: Detail level for results
        - since: Starting point for pagination
        - limit: Maximum number of items to return
        - cursor: Pagination cursor

    Returns
    -------
    Union[List, Dict]
        User data summary or error response with the format:
        {
            "data": list,
            "cursor": list,
            "status": int,
            "message": str
        }
    """
    run_stage = request.run_stage

    try:
        logger.info("Starting admin all users data calculation")
        
        # Process request parameters
        # query_filter = request.filter or {}
        # since = max(request.since or 1, 1)  # Ensure minimum value of 1
        # limit = max(request.limit or 1, 1)  # Ensure minimum value of 1
        # cursor = request.cursor
        
        # # Prepare query parameters
        # kwargs = query_filter.copy() if query_filter else {}
        
        # Step 1: Fetch all session data
        ipersona_session = IpersonaSessionSchema(run_stage=run_stage)
        # data, cursor = ipersona_session.get_all_sessions(
        #     cursor=cursor, 
        #     since=request.since, 
        #     limit=request.limit, 
        #     nopp=True, 
        #     dataframe=False,
        #     # **kwargs
        # )
        data = ipersona_session.get_alladmin_sessions(
            # cursor=cursor, 
            since=request.since, 
            limit=request.limit, 
            nopp=True, 
            dataframe=False,
            # **kwargs
        )
        
        if not data:
            logger.warn("No session data found for admin all users view")
            return {
                "data": [],  
                "cursor": [],
                "status": 404, 
                "message": "No data found with the given parameters"
            }

        logger.info(f"Processing all users metrics for {len(data)} sessions")
        
        # Step 2: Summarize all users data
        result = util.summarize_allusers_data(run_stage, data)
        # result = util.add_columns(result, kind='admin_alluser', **kwargs)
        
        logger.info("Admin all users data calculated successfully")
        return {
            "data": result, 
            # "cursor": cursor,                  
            "status": 200, 
            "message": ""
        }
   
    except Exception as e:
        logger.error(f"Error processing admin all users data: {str(e)}", exc_info=True)
        return {
            "data": [],  
            "cursor": [],
            "status": 500, 
            "message": f"Error processing data: {str(e)}"
        }

@routes.post("/admin_alljobs_data", tags=["Admin Endpoints"])
async def calculate_admin_alljobs_data(request: pemodel.AdminDataFiltering) -> Union[List, Dict]:
    """
    Calculate administrative data for all jobs by processing session data.

    Fetches all session data based on provided filters, calculates metrics,
    and returns summarized results for all jobs.

    Parameters
    ----------
    request : pemodel.AdminDataFiltering
        Object containing:
        - filter: Optional query filters
        - return_skip: Flag to include skipped items
        - information_level: Detail level for results
        - since: Starting point for pagination
        - limit: Maximum number of items to return
        - cursor: Pagination cursor

    Returns
    -------
    Union[List, Dict]
        Jobs data summary or error response with the format:
        {
            "data": list,
            "cursor": list,
            "status": int,
            "message": str
        }
    """
    run_stage = request.run_stage

    try:
        logger.info("Starting admin all jobs data calculation")
        
        # Process request parameters
        # query_filter = request.filter or {}
        # since = max(request.since or 1, 1)  # Ensure minimum value of 1
        # limit = max(request.limit or 1, 1)  # Ensure minimum value of 1
        # cursor = request.cursor
        
        # # Prepare query parameters
        # kwargs = query_filter.copy() if query_filter else {}
        
        # Step 1: Fetch all session data
        ipersona_session = IpersonaSessionSchema(run_stage=run_stage)
        # data, cursor = ipersona_session.get_all_sessions(
        #     cursor=cursor, 
        #     since=request.since, 
        #     limit=request.limit, 
        #     nopp=True, 
        #     dataframe=False,
        #     **kwargs
        # )
        data = ipersona_session.get_alladmin_sessions(
            # cursor=cursor, 
            since=request.since, 
            limit=request.limit, 
            nopp=True, 
            dataframe=False,
            # **kwargs
        )

        if not data:
            logger.warn("No session data found for admin all jobs view")
            return {
                "data": [],  
                "cursor": [],
                "status": 404, 
                "message": "No data found with the given parameters"
            }

        logger.info(f"Processing all jobs metrics for {len(data)} sessions")
        
        # Step 2: Summarize all jobs data
        result = util.summarize_alljobs_data(run_stage, data)
        # result = util.add_columns(result, kind='admin_jobs', **kwargs)
        
        logger.info("Admin all jobs data calculated successfully")
        return {
            "data": result, 
            # "cursor": cursor,                  
            "status": 200, 
            "message": ""
        }

    except Exception as e:
        logger.error(f"Error processing admin all jobs data: {str(e)}", exc_info=True)
        return {
            "data": [],  
            "cursor": [],
            "status": 500, 
            "message": f"Error processing data: {str(e)}"
        }

@routes.post("/admin_allchallenges_data", tags=["Admin Endpoints"])
async def calculate_admin_allchallenges_data(request: pemodel.AdminDataFiltering) -> Union[List, Dict]:
    """
    Calculate administrative data for all challenges by processing session data.

    Fetches all session data based on provided filters, calculates metrics,
    and returns summarized results for all challenges.

    Parameters
    ----------
    request : pemodel.AdminDataFiltering
        Object containing:
        - filter: Optional query filters
        - return_skip: Flag to include skipped items
        - information_level: Detail level for results
        - since: Starting point for pagination
        - limit: Maximum number of items to return
        - cursor: Pagination cursor

    Returns
    -------
    Union[List, Dict]
        Challenges data summary or error response with the format:
        {
            "data": list,
            "cursor": list,
            "status": int,
            "message": str
        }
    """
    run_stage = request.run_stage

    try:
        logger.info("Starting admin all challenges data calculation")
        ipersona_session = IpersonaSessionSchema(run_stage=run_stage)
        data = ipersona_session.get_alladmin_sessions(
            # cursor=cursor, 
            since=request.since, 
            limit=request.limit, 
            nopp=True, 
            dataframe=False,
            # **kwargs
        )

        if not data:
            logger.warn("No session data found for admin all challenges view")
            return {
                "data": [],  
                "cursor": [],
                "status": 404, 
                "message": "No data found with the given parameters"
            }

        logger.info(f"Processing all jobs metrics for {len(data)} sessions")
        
        # Step 2: Summarize all jobs data
        result = util.summarize_allchallenges_data(run_stage, data)
        # result = util.add_columns(result, kind='admin_jobs', **kwargs)
        
        logger.info("Admin all challenge data calculated successfully")
        return {
            "data": result, 
            # "cursor": cursor,                  
            "status": 200, 
            "message": ""
        }

    except Exception as e:
        logger.error(f"Error processing admin all jobs data: {str(e)}", exc_info=True)
        return {
            "data": [],  
            "cursor": [],
            "status": 500, 
            "message": f"Error processing data: {str(e)}"
        }
    
@routes.post("/admin_each_job_overview_data", tags=["Admin Endpoints"]) #-> Dict[str, Any]
async def calculate_admin_eachjob_data(request: pemodel.AdminJobDataTempFiltering) :
    """
    Calculate administrative data for all jobs by processing session data.

    Fetches all session data based on provided filters, calculates metrics,
    and returns summarized results for all jobs.

    Parameters
    ----------
    request : pemodel.AdminDataFiltering
        Object containing:
        - filter: Optional query filters
        - return_skip: Flag to include skipped items
        - information_level: Detail level for results
        - since: Starting point for pagination
        - limit: Maximum number of items to return
        - cursor: Pagination cursor

    Returns
    -------
    Dict[str, Any]
        Jobs data summary or error response with the format:
        {
            "data": list,
            "cursor": list,
            "status": int,
            "message": str
        }
    """
    run_stage = request.run_stage

    try:
        logger.info("Starting admin all jobs data calculation")
        
        # Process request parameters
        job_profile_id = request.job_profile_id
        query_filter = request.filter or {}
        since = max(request.since or 1, 1)  # Ensure minimum value of 1
        limit = max(request.limit or 1, 1)  # Ensure minimum value of 1
        cursor = request.cursor
        
        # Prepare query parameters
        kwargs = query_filter.copy() if query_filter else {}
        
        # -------------- fetch the data with the leap_base.py -------------- #

        # Step 1: Fetch all session data
        ipersona_session = IpersonaSessionSchema(run_stage=run_stage)
        data, cursor = ipersona_session.get_all_sessions(
            cursor=cursor, 
            since=since, 
            limit=limit, 
            nopp=True, 
            dataframe=False,
            **kwargs
        )        
        
        # Step 2: Apply additional filtering by 'job_profile_id'
        data = [
            session for session in data
            if (
                session.get('attributes', {}).get('tinder_job_profile')
                and session['attributes']['tinder_job_profile'].get('data')
                and session['attributes']['tinder_job_profile']['data'].get('id') == str(job_profile_id)
            )
        ]

        # data = ipersona_session.get_alladmin_sessions(
        #     # cursor=cursor, 
        #     since=request.since, 
        #     limit=request.limit, 
        #     nopp=True, 
        #     dataframe=False,
        #     # **kwargs
        # )
        # -------------- fetch the data with the leap_base.py -------------- #

        
        # -------------- fetch the data with the query -------------- #
        # ipersona_job = IpersonaJobSchema()
        # data, cursor = ipersona_job.get_trainee_job_profile(limit, since, cursor, query_filter, job_profile_id)
        # return data
        # -------------- fetch the data with the query -------------- #

        if not data:
            logger.warn("No session data found for admin all jobs view")
            data = []
            job_title = ''
            company_name = ''
            location = ''
            url = ''
            output = util.add_columns(
                        data, 
                        cursor, 
                        job_profile_id, 
                        job_title,
                        company_name,
                        location,
                        url,
                        kind='admin_each_job', 
                        **kwargs
                    )
            cursor['total'] = 0
            return {
                "trainees": output,
                "cursor": cursor,
                "status": 200,
                "message": ""
            }

        logger.info(f"Processing all jobs metrics for {len(data)} sessions")
        logger.info(f"Processing all jobs metrics for {len(data)} sessions")
        
        # Step 2: Summarize all jobs data
        result, total = util.summarize_eachjob_data(run_stage, data)
        cursor['total'] = total

        if result:
            data = result['trainees']
            job_title = result['job_title']
            company_name = result['company_name']
            location = result['location']
            url = result['url']
            
            result = util.add_columns(
                        data, 
                        cursor, 
                        job_profile_id, 
                        job_title,
                        company_name,
                        location,
                        url,
                        kind='admin_each_job', 
                        **kwargs
                    )
            
            logger.info("Admin all jobs data calculated successfully")
            return {
                "trainees": result, 
                "cursor": cursor,                  
                "status": 200, 
                "message": ""
            }

    except Exception as e:
        logger.error(f"Error processing admin all jobs data: {str(e)}", exc_info=True)
        return {
            "status": 500, 
            "message": f"Error processing data: {str(e)}"
        }

@routes.post("/admin_each_challenge_overview_data", tags=["Admin Endpoints"]) #-> Dict[str, Any]
async def calculate_admin_each_challenge_data(request: pemodel.AdminChallengeDataTempFiltering) :
    """
    Calculate administrative data for all challenges by processing session data.

    Fetches all session data based on provided filters, calculates metrics,
    and returns summarized results for all challenges.

    Parameters
    ----------
    request : pemodel.AdminDataFiltering
        Object containing:
        - filter: Optional query filters
        - return_skip: Flag to include skipped items
        - information_level: Detail level for results
        - since: Starting point for pagination
        - limit: Maximum number of items to return
        - cursor: Pagination cursor

    Returns
    -------
    Dict[str, Any]
        Jobs data summary or error response with the format:
        {
            "data": list,
            "cursor": list,
            "status": int,
            "message": str
        }
    """
    run_stage = request.run_stage

    try:
        logger.info("Starting admin all jobs data calculation")
        
        # Process request parameters
        challenge_id = request.challenge_id
        query_filter = request.filter or {}
        since = max(request.since or 1, 1)  # Ensure minimum value of 1
        limit = max(request.limit or 1, 1)  # Ensure minimum value of 1
        cursor = request.cursor
        
        # Prepare query parameters
        kwargs = query_filter.copy() if query_filter else {}
        
        # -------------- fetch the data with the leap_base.py -------------- #

        # Step 1: Fetch all session data
        ipersona_session = IpersonaSessionSchema(run_stage=run_stage)
        data, cursor = ipersona_session.get_all_sessions(
            cursor=cursor, 
            since=since, 
            limit=limit, 
            nopp=True, 
            dataframe=False,
            **kwargs
        )        

        # Step 2: Apply additional filtering by 'job_profile_id'
        data = [
            session for session in data
            if (
                session.get('attributes', {}).get('challenge_document')
                and session['attributes']['challenge_document'].get('data')
                and session['attributes']['challenge_document']['data'].get('id') == str(challenge_id)
            )
        ]     

        if not data:
            logger.warn("No session data found for admin all jobs view")
            data = []
            challenge_title= ''
            output = util.add_challenge_columns(
                        data, 
                        cursor, 
                        challenge_id, 
                        challenge_title,
                        kind='admin_each_challenge', 
                        **kwargs
                    )
            cursor['total'] = 0
            return {
                "trainees": output,
                "cursor": cursor,
                "status": 200,
                "message": ""
            }

        logger.info(f"Processing all jobs metrics for {len(data)} sessions")
        logger.info(f"Processing all jobs metrics for {len(data)} sessions")
        
        # Step 2: Summarize all jobs data
        result, total = util.summarize_eachchallenge_data(run_stage, data)
        cursor['total'] = total

        if result:
            data = result['trainees']
            challenge_title = result['challenge_title']
            
            result = util.add_challenge_columns(
                        data, 
                        cursor, 
                        challenge_id, 
                        challenge_title,
                        kind='admin_each_challenge', 
                        **kwargs
                    )
            
            logger.info("Admin all jobs data calculated successfully")
            return {
                "trainees": result, 
                "cursor": cursor,                  
                "status": 200, 
                "message": ""
            }

    except Exception as e:
        logger.error(f"Error processing admin all jobs data: {str(e)}", exc_info=True)
        return {
            "status": 500, 
            "message": f"Error processing data: {str(e)}"
        }
         
@routes.post("/admin_allusers_performance_data", tags=["Admin Endpoints"])
async def calculate_admin_allusers_performance_data(request: pemodel.AdminDataFiltering) :
    """
    Calculate performance metrics for all users by processing session data.

    Fetches all session data based on provided filters, calculates performance metrics,
    and returns detailed performance analysis for all users.

    Parameters
    ----------
    request : pemodel.AdminDataFiltering
        Object containing:
        - filter: Optional query filters
        - return_skip: Flag to include skipped items
        - information_level: Detail level for results
        - since: Starting point for pagination
        - limit: Maximum number of items to return
        - cursor: Pagination cursor

    Returns
    -------
    Union[List, Dict]
        Performance data summary or error response with the format:
        {
            "data": list,
            "cursor": list,
            "status": int,
            "message": str
        }
    """
    run_stage = request.run_stage

    try:
        logger.info("Starting admin all users performance data calculation")
        
        # Process request parameters
        # query_filter = request.filter or {}
        # since = max(request.since or 1, 1)  # Ensure minimum value of 1
        # limit = max(request.limit or 1, 1)  # Ensure minimum value of 1
        # cursor = request.cursor
        
        # # Prepare query parameters
        # kwargs = query_filter.copy() if query_filter else {}
        # Step 1: Fetch all session data
        ipersona_session = IpersonaSessionSchema(run_stage=run_stage)
        # data, cursor = ipersona_session.get_all_sessions(
        #     cursor=cursor, 
        #     since=request.since, 
        #     limit=request.limit, 
        #     nopp=True, 
        #     dataframe=False,
        #     **kwargs
        # )
        data = ipersona_session.get_alladmin_sessions(
            # cursor=cursor, 
            since=request.since, 
            limit=request.limit, 
            nopp=True, 
            dataframe=False,
            # **kwargs
        )
               
        if not data:
            logger.warn("No session data found for admin all users performance view")
            return {
                "data": [],  
                "cursor": [],
                "status": 404, 
                "message": "No data found with the given parameters"
            }

        logger.info(f"Processing performance metrics for {len(data)} sessions")
        
        # Step 2: Summarize all users performance data
        result = util.summarize_allusers_performance_data(run_stage, data)
        # result = util.add_columns(result, kind='admin_allusers_performance', **kwargs)
        
        logger.info("Admin all users performance data calculated successfully")
        return {
            "data": result, 
            # "cursor": cursor,                  
            "status": 200, 
            "message": ""
        }

    except Exception as e:
        logger.error(f"Error processing admin all users performance data: {str(e)}", exc_info=True)
        return {
            "data": [],  
            "cursor": [],
            "status": 500, 
            "message": f"Error processing data: {str(e)}"
        }

@routes.post("/admin_job_by_template_id", tags=["Admin Endpoints"])
async def calculate_admin_job_by_template_id(request: pemodel.AdminJobByTemplateIdFiltering) -> Union[List, Dict]:
    try:
        run_stage = request.run_stage
        template_id = request.template_id
        query_filter = request.filter or {}
        since = max(request.since or 1, 1)
        limit = max(request.limit or 1, 1)
        cursor = request.cursor
        kwargs = query_filter.copy() if query_filter else {}
        logger.info(f"Starting admin job by template ID calculation for template ID: {template_id}")
        
        ipersona_job = IpersonaJobSchema(run_stage=run_stage)
        result_tuple = ipersona_job.filter_by_template_id(
            template_id=template_id, 
            cursor=cursor, 
            since=since, 
            limit=limit, 
            nopp=True, 
            dataframe=False,
            **kwargs
        )

        # Improved error handling for None or invalid return
        if not result_tuple or not isinstance(result_tuple, (tuple, list)) or len(result_tuple) != 2:
            logger.warn(f"No jobs found or invalid template_id: {template_id}")
            data = []
            result = util.add_template_columns(
                data, 
                cursor, 
                kind='job_by_template', 
                **kwargs
            )
            return {
                "jobs": result, 
                "cursor": [],                  
                "status": 200, 
                "message": f"No jobs found for the given template_id: {template_id}."
            }

        data, cursors = result_tuple

        result = util.add_template_columns(
            data, 
            cursor, 
            kind='job_by_template', 
            **kwargs
        )
        return {
            "jobs": result, 
            "cursor": cursor,                  
            "status": 200, 
            "message": ""
        }
   
    except Exception as e:
        logger.error(f"Error processing admin job by template ID: {str(e)}", exc_info=True)
        return {
            "jobs": [],  
            "cursor": [],
            "status": 500, 
            "message": f"Error processing data: {str(e)}"
        }
    
@routes.post("/admin_challenge_by_template_id", tags=["Admin Endpoints"])
async def calculate_admin_challenge_by_template_id(request: pemodel.AdminJobByTemplateIdFiltering) -> Union[List, Dict]:
    try:
        run_stage = request.run_stage
        template_id = request.template_id
        query_filter = request.filter or {}
        since = max(request.since or 1, 1)  # Ensure minimum value of 1
        limit = max(request.limit or 1, 1)  # Ensure minimum value of 1
        cursor = request.cursor
        kwargs = query_filter.copy() if query_filter else {}
        logger.info(f"Starting admin challenge by template ID calculation for template ID: {template_id}")
        
        ipersona_challenge = IpersonaChallengeDocumentSchema(run_stage=run_stage, limit=limit, since=since)
        result_tuple = ipersona_challenge.filter_by_template_id(
            template_id=template_id, 
            since=request.since, 
            limit=request.limit, 
            nopp=True, 
            dataframe=False,
            **kwargs
        )

        # Improved error handling for None or invalid return
        if not result_tuple or not isinstance(result_tuple, (tuple, list)) or len(result_tuple) != 2:
            logger.warn(f"No challenges found or invalid template_id: {template_id}")

            data = []
            result = util.add_template_columns(
                data, 
                cursor, 
                kind='challenge_by_template', 
                **kwargs
            )
            return {
                "challenges": result, 
                "cursor": [],                  
                "status": 200, 
                "message": f"No challenges found for the given template_id: {template_id}."
            }
        
        data, cursor = result_tuple

        result = util.add_template_columns(
            data, 
            cursor, 
            kind='challenge_by_template', 
            **kwargs
        )
        return {
            "challenges": result, 
            "cursor": cursor,                  
            "status": 200, 
            "message": ""
        }
    
    except Exception as e:
        logger.error(f"Error processing admin challenge by template ID: {str(e)}", exc_info=True)
        return {
            "challenges": [],  
            "cursor": [],
            "status": 500, 
            "message": f"Error processing data: {str(e)}"
        }
    
@routes.post("/admin_interview_by_template", tags=["Admin Endpoints"])
async def calculate_admin_interview_by_template(request: pemodel.AdminInterviewByTemplateIdFiltering) -> Union[List, Dict]:
    try:
        run_stage = request.run_stage
        filter_by_status = request.status.lower()
        template_id = request.template_id
        query_filter = request.filter or {}
        since = max(request.since or 1, 1)  # Ensure minimum value of 1
        limit = max(request.limit or 1, 1)  # Ensure minimum value of 1
        cursor = request.cursor
        kwargs = query_filter.copy() if query_filter else {}
        logger.info(f"Starting admin interview by template ID calculation for template ID: {template_id}")
        
        ipersona_session = IpersonaSessionSchema(run_stage=run_stage)
        result_tuple = ipersona_session.filter_by_template_id(
            template_id=template_id, 
            cursor=cursor, 
            since=since, 
            limit=limit, 
            nopp=True, 
            dataframe=False,
            **kwargs
        )

        # Improved error handling for None or invalid return
        if not result_tuple or not isinstance(result_tuple, (tuple, list)) or len(result_tuple) != 2:
            logger.warn(f"No interviews found or invalid template_id: {template_id}")
            return {
                "interviews": [],
                "cursor": [],
                "status": 404,
                "message": f"No interviews found for the given template_id: {template_id}."
            }

        filtered_data, cursor = result_tuple

        data, cursor = util.summarize_interview_by_template_data(
            run_stage, 
            filtered_data, 
            cursor,
            filter_by_status
        )

        result = util.add_template_columns(
            data, 
            cursor, 
            kind='interview_by_template', 
            **kwargs
        )
        return {
            "interviews": result, 
            "cursor": cursor,                  
            "status": 200, 
            "message": ""
        }
    
    except Exception as e:
        logger.error(f"Error processing admin interview by template ID: {str(e)}", exc_info=True)
        return {
            "interviews": [],  
            "cursor": [],
            "status": 500, 
            "message": f"Error processing data: {str(e)}"
        }
# ----------------------------------- Fetching session Data ---------------------#
@routes.post("/fetch_user_session", tags=["Session Endpoints"])
async def fetch_user_session(request: pemodel.AlUserSessionRequestRecieved) :
    """
    Fetch session data for a specific user and job.

    Retrieves trainee profile data for the given user ID and then
    fetches associated session data for the specified job.

    Parameters
    ----------
    request : pemodel.UserSessionRequestRecieved
        Object containing:
        - all_user_id: User ID to fetch session data for
        - job_profile_id: Job ID to filter sessions

    Returns
    -------
    Union[Union[List, Dict], JSONResponse]
        Session data for the user and job, or an error response
    """  
    run_stage = request.run_stage
    job_profile_id = request.job_profile_id
    template_id = request.template_id
    challenge_id = request.challenge_id
    since = request.since
    # limit = request.limit

    try:
        logger.info(f"Fetching session data for user ID: {request.all_user_id} and job ID: {request.job_profile_id}")

        # Step 1: Retrieve trainee profile data
        ipersona_user = IpersonaTraineeSchema(run_stage=run_stage)
        trainee_profile_data = ipersona_user.filter_by_alluser_id(
            all_user_id=request.all_user_id, 
            nopp=True, 
            dataframe=False
        )

        if not trainee_profile_data:
            logger.warn(f"No trainee user profiles found for user ID: {request.all_user_id}")
            return JSONResponse(
                status_code=404, 
                content={"message": f"No trainee user profiles found for user ID: {request.all_user_id}"}
            )

        logger.info(f"Trainee profile data retrieved for user ID: {request.all_user_id}")

        # Step 2: Extract user profile ID
        tinder_user_profile_id = trainee_profile_data['id']
         
        # Step 3: Fetch session data by user and job ID
        if job_profile_id:
            ipersona_session = IpersonaSessionSchema(run_stage=run_stage)
            try:
                user_data = ipersona_session.filter_by_with_user_job_id_by_filtering(
                    user_profile_id=tinder_user_profile_id,
                    job_profile_id=request.job_profile_id,
                    since=since,
                    nopp=True, 
                    dataframe=False
                )

                if not user_data:
                    logger.warn(f"No session data found for user ID: {request.all_user_id} and job ID: {request.job_profile_id}")
                    return JSONResponse(
                        status_code=200, 
                        content={"message": f"No session data found for user ID: {request.all_user_id} and job ID: {request.job_profile_id}"}
                    )

                logger.info(f"Session data successfully retrieved for user ID: {request.all_user_id} and job ID: {request.job_profile_id}")
                return user_data
            
            except Exception as e:
                logger.error(f"Error fetching session data for user ID: {request.all_user_id} and job ID: {request.job_profile_id} - {str(e)}", exc_info=True)
                return JSONResponse(
                    status_code=500, 
                    content={"error": f"Error fetching user session: {str(e)}"}
                )
        
        elif template_id:
            ipersona_session = IpersonaSessionSchema(run_stage=run_stage)
            user_data = ipersona_session.filter_by_with_user_template_id_by_filtering(
                user_profile_id=tinder_user_profile_id,
                template_id=request.template_id,
                since=since,
                nopp=True, 
                dataframe=False
            )

            if not user_data:
                logger.warn(f"No session data found for user ID: {request.all_user_id} and template ID: {request.template_id}")
                return JSONResponse(
                    status_code=200, 
                    content={"message": f"No session data found for user ID: {request.all_user_id} and template ID: {request.template_id}"}
                )

            logger.info(f"Session data successfully retrieved for user ID: {request.all_user_id} and template ID: {request.template_id}")
            return user_data
        
        elif challenge_id:
            ipersona_session = IpersonaSessionSchema(run_stage=run_stage)
            user_data = ipersona_session.filter_by_with_user_challenge_id_by_filtering(
                user_profile_id=tinder_user_profile_id,
                challenge_id=request.challenge_id,
                since=since,
                nopp=True, 
                dataframe=False
            )

            if not user_data:
                logger.warn(f"No session data found for user ID: {request.all_user_id} and challenge ID: {request.challenge_id}")
                return JSONResponse(
                    status_code=200, 
                    content={"message": f"No session data found for user ID: {request.all_user_id} and challenge ID: {request.challenge_id}"}
                )

            logger.info(f"Session data successfully retrieved for user ID: {request.all_user_id} and challenge ID: {request.challenge_id}")
            return user_data

    except Exception as e:
        logger.error(f"Error processing session data for user ID: {request.all_user_id} - {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500, 
            content={"error": f"Error fetching user session: {str(e)}"}
        )
   
@routes.post("/fetch_chat_history", tags=["Session Endpoints"])
async def fetch_chat_history(request: pemodel.SessionIdRequestRecieved)-> Union[List, Dict]:
    """
    Fetch chat message history for a specific session.

    Retrieves all chat messages associated with the specified session ID,
    sorted in ascending order by timestamp.

    Parameters
    ----------
    request : pemodel.SessionIdRequestRecieved
        Object containing:
        - sessionId: ID of the session to fetch chat history for

    Returns
    -------
    Union[List[Union[List, Dict]], JSONResponse]
        List of chat messages or an error response
    """
    run_stage = request.run_stage

    try:
        logger.info(f"Fetching chat history for session ID: {request.sessionId}")

        # Step 1: Fetch chat history from the database
        ipersona_message = IpersonaSessionMessageSchema(run_stage=run_stage)
        session_chathistory = ipersona_message.filter_by_session_id(
            sessionId=request.sessionId, 
            nopp=True, 
            dataframe=False, 
            sort='asc'
        )

        if not session_chathistory:
            logger.warn(f"No chat history found for session ID: {request.sessionId}")
            return JSONResponse(
                status_code=404, 
                content={"message": f"No chat history found for session ID: {request.sessionId}"}
            )

        logger.info(f"Successfully fetched chat history for session ID: {request.sessionId}")
        return session_chathistory

    except Exception as e:
        logger.error(f"Error fetching chat history for session ID {request.sessionId}: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500, 
            content={"error": f"Error fetching chat history: {str(e)}"}
        )

@routes.post("/fetch_user_all_observer", tags=["Session Endpoints"])
async def fetch_user_all_observer(request: pemodel.SessionIdRequestRecieved)-> Union[List, Dict]:
    """
    Fetch all observers for a specific session.

    Retrieves all observer data associated with the specified session ID.

    Parameters
    ----------
    request : pemodel.SessionIdRequestRecieved
        Object containing:
        - sessionId: ID of the session to fetch observers for

    Returns
    -------
    Union[List[Union[List, Dict]], JSONResponse]
        List of observers or an error response
    """
    run_stage = request.run_stage

    try:
        logger.info(f"Fetching observers for session ID: {request.sessionId}")

        # Step 1: Fetch session observers from the database
        ipersona_observer = IpersonaSessionObserverSchema(run_stage=run_stage)
        session_chatobserver = ipersona_observer.filter_by_observer_session_id(
            sessionId=request.sessionId, 
            nopp=True, 
            dataframe=False
        )

        if not session_chatobserver:
            logger.warn(f"No observers found for session ID: {request.sessionId}")
            return JSONResponse(
                status_code=404, 
                content={"message": f"No observers found for session ID: {request.sessionId}"}
            )

        logger.info(f"Successfully fetched {len(session_chatobserver)} observers for session ID: {request.sessionId}")
        return session_chatobserver

    except Exception as e:
        logger.error(f"Error fetching observers for session ID {request.sessionId}: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500, 
            content={"error": f"Error fetching observers: {str(e)}"}
        )

@routes.post("/fetch_single_session", tags=["Session Endpoints"])
async def fetch_single_session(request: pemodel.SessionIdRequestRecieved):
    """
    Fetch data for a single session by its ID.

    Retrieves the session data associated with the specified session ID,
    removing the generated_questions field from the results.

    Parameters
    ----------
    request : pemodel.SessionIdRequestRecieved
        Object containing:
        - sessionId: ID of the session to fetch

    Returns
    -------
    Union[Dict[str, Any], JSONResponse]
        Session data or an error response
    """
    run_stage = request.run_stage

    try:
        logger.info(f"Fetching session data for session ID: {request.sessionId}")

        # Step 1: Fetch session data by session ID from the database
        ipersona_session = IpersonaSessionSchema(run_stage=run_stage)
        session_fetched = ipersona_session.get_by_id(
            sessionId=request.sessionId, 
            nopp=True, 
            dataframe=False
        )

        if not session_fetched:
            logger.warn(f"No session found for session ID: {request.sessionId}")
            return JSONResponse(
                status_code=404, 
                content={"message": f"No session found for session ID: {request.sessionId}"}
            )

        logger.info(f"Successfully fetched session data for session ID: {request.sessionId}")
        
        # Remove generated_questions field from response
        # session_fetched = util.remove_key(session_fetched, 'generated_questions')
        
        return session_fetched

    except Exception as e:
        logger.error(f"Error fetching session data for session ID {request.sessionId}: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500, 
            content={"error": f"Error fetching session: {str(e)}"}
        )

#----------------------------------- Question Template Processing APIS -----------------------------------#
@routes.post("/save_tinder_template", tags=["Template Endpoints"])
def tinder_template(request: pemodel.TinderTemplateRequestRecieved):
    try:
        name = request.name
        type = request.type
        tag = request.tag
        description = request.description
        template_questions = request.template_questions
        job_profile_ids = request.job_profile_ids
        prompt_ids = request.prompt_ids
        challenge_ids = request.challenge_ids

        ipersona_tinder = IpersonaTinderTemplateSchema()
        saved_data = ipersona_tinder.create_template(
            name, 
            type, 
            tag,
            description,
            template_questions, 
            job_profile_ids, 
            prompt_ids, 
            challenge_ids)
          
        if saved_data.get('status') == 'error':
            return {
                "template": saved_data,
                "success": 200,
                "message": 'Process Failed'
            }
        else:
            return {
                "template": saved_data,
                "success": 200,
                "message": 'Template Fetched Successfully.'
            }
             
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Error saving template: {str(e)}"}
        )
     
@routes.post("/get_tinder_templates", tags=["Template Endpoints"])
def get_tinder_template(request: pemodel.GetFilteredTinderTemplateRequestRecieved):
    try:
        job_profile_id = request.job_profile_id
        challenge_id = request.challenge_id
        prompt_id = request.prompt_id
        type = request.type
        query_filter = request.filter or {}
        since = max(request.since or 1, 1)  # Ensure minimum value of 1
        limit = max(request.limit or 1, 1)  # Ensure minimum value of 1
        cursor = request.cursor
        
        # Prepare query parameters
        kwargs = query_filter.copy() if query_filter else {}
        
        ipersona_template = IpersonaTinderTemplateSchema()

        # Conditional filtering
        if job_profile_id:  # If job_profile_id is provided (and not None)
            fetch_templates, cursor = ipersona_template.filter_by_with_job_id(
                job_profile_id=job_profile_id, 
                cursor=cursor, 
                since=since, 
                limit=limit, 
                nopp=True, 
                dataframe=False,
                **kwargs
            )
            
            # Transform the result to replace job profile list with a count
            transformed_templates = transform_job_profiles_to_count(fetch_templates)
            output = util.add_template_columns(transformed_templates, cursor, kind='template', **kwargs)    

            if not transformed_templates:
                cursor['total'] = 0
                return {
                    "template": output,
                    "cursor": cursor,
                    "success": 200,
                    "message": 'No templates found for the given job profile ID.'
                }
            else: 
                return {
                    "template": output,
                    "cursor": cursor,
                    "success": 200,
                    "message": 'Templates Fetched Successfully for Job Profile ID.'
                }
        elif challenge_id != 0:  # If job_profile_id is provided (and not None)
            fetch_templates, cursor = ipersona_template.filter_by_with_challenge_id(
                challenge_id=challenge_id, 
                cursor=cursor, 
                since=since, 
                limit=limit, 
                nopp=True, 
                dataframe=False,
                **kwargs
            )
            
            # Transform the result to replace job profile list with a count
            transformed_templates = util.transform_job_profiles_to_count(fetch_templates)
            output = util.add_template_columns(transformed_templates, cursor, kind='template', **kwargs)    

            if not transformed_templates:
                cursor['total'] = 0
                return {
                    "template": output,
                    "cursor": cursor,
                    "success": 200,
                    "message": 'No templates found for the given job profile ID.'
                }
            else: 
                return {
                    "template": output,
                    "cursor": cursor,
                    "success": 200,
                    "message": 'Templates Fetched Successfully for Job Profile ID.'
                }
            
        elif prompt_id != 0:  # If prompt_id is provided (and not None)
            fetch_templates, cursor = ipersona_template.filter_by_with_prompt_id(
                prompt_id=prompt_id, 
                cursor=cursor, 
                since=since, 
                limit=limit, 
                nopp=True, 
                dataframe=False,
                **kwargs
            )
            
            # Transform the result to replace job profile list with a count
            transformed_templates = util.transform_job_profiles_to_count(fetch_templates)
            output = util.add_template_columns(transformed_templates, cursor, kind='template', **kwargs)    

            if not transformed_templates:
                cursor['total'] = 0
                return {
                    "template": output,
                    "cursor": cursor,
                    "success": 200,
                    "message": 'No templates found for the given job profile ID.'
                }
            else: 
                return {
                    "template": output,
                    "cursor": cursor,
                    "success": 200,
                    "message": 'Templates Fetched Successfully for Job Profile ID.'
                }
            
        elif type:  # If only type is provided (not None)
            templates, cursor = ipersona_template.filter_by_type(
                type=type, 
                cursor=cursor, 
                since=since, 
                limit=limit, 
                nopp=True, 
                dataframe=False,
                **kwargs
            )

            # Transform the result to replace job profile list with a count
            transformed_templates = transform_job_profiles_to_count(templates)
            output = util.add_template_columns(transformed_templates, cursor, kind='template', **kwargs)    

            if not transformed_templates:
                cursor['total'] = 0
                return {
                    "templates": output,
                    "cursor": cursor,
                    "success": 200,
                    "message": f'No templates found for type: {type}.'
                }
            else:
                return {
                    "templates": output,
                    "cursor": cursor,
                    "success": 200,
                    "message": f'Templates Fetched Successfully for Type: {type}.'
                }

        else:  # If neither job_profile_id nor type is provided
            templates, cursor = ipersona_template.get_all_templates(
                cursor=cursor, 
                since=since, 
                limit=limit, 
                nopp=True, 
                dataframe=False,
                **kwargs
                )

            # Transform the result to replace job profile list with a count
            transformed_templates = transform_job_profiles_to_count(templates)
            output = util.add_template_columns(transformed_templates, cursor, kind='template', **kwargs)    

            if not transformed_templates:
                cursor['total'] = 0
                return {
                    "templates": output,
                    "cursor": cursor,
                    "success": 200,
                    "message": 'No templates found.'
                }
            else:
                return {
                    "templates": output,
                    "cursor": cursor,
                    "success": 200,
                    "message": 'All Templates Fetched Successfully.'
                }
        
    except Exception as e:
        logger.error(f"Error getting template: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": f"Error processing template request: {str(e)}"}
        )

def transform_job_profiles_to_count(templates):
    """
    Transform the `tinder_job_profiles` to include only the count of profiles 
    and move attributes fields to the root level.
    """
    if not templates:
        return []

    transformed_templates = []

    for template in templates:
        # Extract attributes and merge with root-level id
        transformed_template = {
            "id": template["id"],
            **template.get("attributes", {})
        }

        # Replace the list of job profile IDs with the count of profiles
        if "tinder_job_profiles" in transformed_template:
            job_profiles = transformed_template["tinder_job_profiles"].get("data", [])
            transformed_template["tinder_job_profiles"] = len(job_profiles)
        
        transformed_templates.append(transformed_template)
    
    return transformed_templates
    
@routes.post("/get_a_template", tags=["Template Endpoints"])
def get_tinder_template(request: pemodel.GetTemplateRequestRecieved):
    try:
        template_id = request.template_id
        ipersona_template = IpersonaTinderTemplateSchema()
        fetched_template = ipersona_template.get_tinder_template_id(
            templateId=template_id, 
            return_object=True, 
            nopp=True, 
            dataframe=False
        )
        
        if not fetched_template:
            return {
                "template": fetched_template,
                "success": 200,
                "message": ''
            }
        else: 
            return {
                "template": fetched_template,
                "success": 200,
                "message": 'Template Fetched Successfully.'
            }
    
        
    except Exception as e:
        logger.error(f"Error getting template: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": f"Error processing getting template: {str(e)}"}
        )
    
@routes.post("/update_tinder_template", tags=["Template Endpoints"])
def update_tinder_template(request: pemodel.UpdateTinderTemplateRequestRecieved):
    try:
        template_id = request.template_id
        name = request.name if request.name != "" else None
        type = request.type if request.type != "" else None
        tag = request.tag if request.tag != "" else None
        description = request.description if request.description != "" else None
        template_questions = request.template_questions if request.template_questions != "" else None
        job_profile_ids = request.job_profile_ids if request.job_profile_ids != "" else None
        prompt_ids = request.prompt_ids if request.prompt_ids != "" else None
        challenge_ids = request.challenge_ids if request.challenge_ids != "" else None
        session_ids = ""
        session_ids = None if session_ids == "" else session_ids

        ipersona_tinder = IpersonaTinderTemplateSchema()
        data = ipersona_tinder.update_template(
            template_id, 
            name, 
            type, 
            tag,
            description,
            template_questions, 
            job_profile_ids,
            prompt_ids, 
            challenge_ids,
            session_ids)
        
        if data.get('status') == 'error':
            return {
                "template": data,
                "success": 200,
                "message": 'Process Failed'
            }
        else:
            return {
                "template": data,
                "success": 200,
                "message": 'Template Updated Sucessfully.'
            }
     
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Error processing template update: {str(e)}"}
        )

@routes.post("/attach_job_id_to_template", tags=["Template Endpoints"])
def attach_id_to_template(request: pemodel.TinderTemplateAttachJobIdRequestRecieved):
    try:
        template_id = request.template_id
        job_profile_ids = request.job_profile_ids
        prompt_ids = request.prompt_ids
        challenge_ids = request.challenge_ids
        session_ids = []

        ipersona_template =  IpersonaTinderTemplateSchema()
        attach_template = ipersona_template.add_job_profiles_to_template(
            template_id, 
            job_profile_ids, 
            prompt_ids, 
            challenge_ids,
            session_ids)

        if attach_template.get('status') == 'error':
            return {
                "template": attach_template,
                "success": 200,
                "message": 'Process Failed'
            }
        else: 
            return {
                "template": attach_template,
                "success": 200,
                "message": 'Job Id is attached to the template successfully.'
            }
    
    except Exception as e:
        logger.error(f"Error attaching id to template: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": f"Error attaching id to template:: {str(e)}"}
        )

@routes.post("/create_template_by_llm", tags=["Template Endpoints"])
async def create_template_by_llm(request: pemodel.TemplateLLMContextRequestRecieved):
    try:
        context = request.context
        all_user_id = request.all_user_id
        job_profile_ids = request.job_profile_ids
        challenge_ids = request.challenge_ids
        run_stage = request.run_stage
        tinder_user_profile_data = ""
        
        if len(job_profile_ids) != 0:
            type='job_interview_config'
            persona_tag = 'parrot_persona'

            tinder_user_profile_data, tinder_user_profile_id = util.get_user_data(all_user_id, run_stage)
            tinder_job_data = util.get_job_data_template_for_multiple_ids(job_profile_ids, run_stage)
            # Load and format prompt templates
            response_obj = util.fetch_the_structure(type)
    

            if response_obj is False:        
                tag ='parrot_question_generator_default'
                generated_persona = util.read_prompt_persona(
                    tinder_job_data, 
                    tinder_user_profile_data, 
                    type, 
                    persona_tag)
                
                msg = util.read_prompt_data_for_default(
                    type, 
                    tag)
                
                content = generated_persona + msg

            else:
                section_count = response_obj.get('section_count', {})
                json_format = response_obj.get('json_format', {})

                tag = 'parrot_generate_question'
                generated_persona = util.read_prompt_persona(
                    tinder_job_data, 
                    tinder_user_profile_data, 
                    type, 
                    persona_tag)
                
                msg = util.read_generate_question_prompt(
                    json_format, 
                    section_count, 
                    context,
                    tag,
                    type)
                content = generated_persona + msg

        if len(challenge_ids) != 0:
            type = 'challenge_interview_config'
            persona_tag = 'parrot_persona'

            tinder_challenge_data = await util.analyze_multiple_challenges(challenge_ids)
            
            # Load and format prompt templates
            response_obj = util.fetch_the_structure(type)
         
            if response_obj is False:
                # if there no challenge structure found, fallback to default prompt    REMOVE THE JSON_DUMP FROM CHALLENGE
                tag ='parrot_challenge_question_generation_default'
                content = util.read_prompt_data_for_multiple_challenge_default(
                    tinder_challenge_data, 
                    type, 
                    tag)
            else: 
                section_count = response_obj.get('section_count', {})
                json_format = response_obj.get('json_format', {})
               
                tag = 'parrot_challenge_question_generation' 
                section_count = response_obj.get('section_count', {})
                json_format = response_obj.get('json_format', {})
                content = util.read_prompt_data_for_multiple_challenge(
                    json_format, 
                    section_count,
                    tinder_challenge_data, 
                    type, 
                    tag)
                

        # Generate interview questions
        response = gpt.openai_gpt_assistant_without_streaming(content)

        if not response:
            logger.error("Failed to generate questions: Empty AI response")
            return JSONResponse(
                status_code=500,
                content={"error": "Failed to generate interview questions"}
            )
            
        generated_question_json = util.extract_json(response, quite=False)
        logger.info("Persona and questions generated successfully")

        generated_question_json = util.add_question_number(generated_question_json)

        if generated_question_json:
            return {
                "response": generated_question_json,
                "success": 200,
                "message": 'Process Failed'
            }
        else: 
            return {
                "response": [],
                "success": 200,
                "message": ''
            }
    
    except Exception as e:
        logger.error(f"Error attaching id to template: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": f"Error attaching id to template:: {str(e)}"}
        )


#----------------------------------- External Audio Upload Processing APIS -----------------------------------#
# @routes.post("/audio_upload_external", tags=["Audio Endpoints"])
# async def speech_to_text(file: UploadFile = File(...)):
#     if not file or not file.filename:
#         logger.error("Invalid file: No file or filename provided")
#         return JSONResponse(
#             status_code=400,
#             content={
#                 "transcription": "Failed",
#                 "status": 400,
#                 "message": "No file provided or invalid file"
#             }
#         )
        
#     try:
#         logger.info(f"Starting audio processing for file: {file.filename}")
        
#         # Create directory if it doesn't exist
#         audio_dir = data_path('audio')
#         os.makedirs(audio_dir, exist_ok=True)
        
#         audio_path = os.path.join(audio_dir, file.filename)
#         logger.debug(f"Saving audio file to: {audio_path}")
        
#         # Save the uploaded file
#         contents = await file.read()
#         with open(audio_path, "wb") as f:
#             f.write(contents)
#         logger.info("Audio file saved successfully")
        
#         # Initialize transcriber and process file
#         transcriber = aai.Transcriber()
#         transcript = transcriber.transcribe(audio_path)

#         if transcript.status == aai.TranscriptStatus.error:
#             error_msg = getattr(transcript, 'error', 'Unknown transcription error')
#             logger.error(f"Transcription error: {error_msg}")
#             return {
#                 "transcription": "Failed",
#                 "status": 400, 
#                 "message": error_msg
#             }
            
#         logger.info("Transcription completed successfully")
#         logger.debug(f"Transcription text: {transcript.text}")
 
#         external_audio_prompt = util.file_reader(prompt_path('external_audio_analysis.txt'))
#         realtime_prompt = util.file_reader(prompt_path('realtime_evaluation.txt'))

#         # realtime_prompt = realtime_prompt \
#         #         .replace("{question}", str(transcript.text)) \
#         #         .replace("{candidate_response}", str(realtime_prompt)) 
      
#         external_aud_prompt = external_audio_prompt \
#                 .replace("{transcription}", str(transcript.text)) \
#                 .replace("{realtime}", str(realtime_prompt)) 
    
#         data = gpt.openai_gpt_assistant_without_streaming(external_aud_prompt)
#         response = util.extract_json(data, quite=False)
     
#         return {
#             "chat": response,
#             "status": 200,
#             "message": "Audio Successfully Transcribed"
#         }
    
#     except Exception as e:
#         logger.error(f"Error during transcription: {str(e)}", exc_info=True)
#         return JSONResponse(
#             status_code=500,
#             content={
#                 "transcription": "Failed",
#                 "status": 500,
#                 "message": f"System error: {str(e)}"
#             }
#         )
    
# @routes.post("/external_data_saving", tags=["Audio Endpoints"])
# async def external_data_saving(request: pemodel.ExternalRequestRecieved):
#     try:
#         run_stage = request.run_stage
#         transcribe_chat = request.transcribe_chat
#         all_user_id = request.all_user_id
#         job_profile_id = request.job_profile_id

#         ipersona_user = IpersonaTraineeSchema(run_stage=run_stage)
#         trainee_profile_data = ipersona_user.filter_by_alluser_id(
#             all_user_id=all_user_id, nopp=True, dataframe=False
#         )
    
#         if not trainee_profile_data:
#             logger.warn(f"No trainee user profiles found for all_user_id: {all_user_id}")
#             return JSONResponse(
#                 status_code=404,
#                 content={"error": "No trainee user profiles found for the given all_user_id"}
#             )

#         tinder_user_profile_id = trainee_profile_data.get('id')
#         if not tinder_user_profile_id:
#             return JSONResponse(
#                 status_code=500,
#                 content={"error": "Invalid trainee profile: missing ID"}
#             )
#         template_id = 0
#         challenge_id = 0
#         message = ''

#         saved_session =  util.create_session(
#             run_stage, 
#             request, 
#             all_user_id, 
#             tinder_user_profile_id, 
#             job_profile_id,
#             template_id, 
#             challenge_id,
#             message)
#         # saved_session = True
#         if saved_session:
#             sessionId = saved_session['id']
      
#             saved = strapi.save_messages_to_db(transcribe_chat , sessionId)
#             status = 'External'
#             type = 'job_interview_config'

#             overall = await util.overall_interview_evaluations_external(run_stage, transcribe_chat, status, sessionId, all_user_id, tinder_user_profile_id, job_profile_id)
#             return {
#                 "chat": saved,
#                 "overall": overall,
#                 "status": 200,
#                 "message": "Chat Saved Successfully"
#             }
#         else:
#             return {
#                 "chat": [],
#                 "status": 400,
#                 "message": "Chat Not Saved"
#             }

#     except Exception as e:
#         logger.error(f"Error creating user session: {str(e)}", exc_info=True)
#         return JSONResponse(
#             status_code=500,
#             content={"error": f"Error processing user session: {str(e)}"}
#         )


#----------------------------------- Challenge Document Processing APIS -----------------------------------#
@routes.post("/get_all_challenges", tags=["Challenge Endpoints"])
def fetch_all_challenges():
    try:
        ipersona_challenge = IpersonaChallengeDocumentSchema()
        challenges = ipersona_challenge.get_all_challenges(nopp=True, dataframe=False)

        return {
            "challenges": challenges,
            "success": 200,
            "message": 'Challenges are Fetched Successfully.'
        }
    
    except Exception as e:
        logger.error(f"Error creating user session: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": f"Error processing user session: {str(e)}"}
        )
 
@routes.post("/get_a_challenge", tags=["Challenge Endpoints"])
def fetch_a_challenge(request: pemodel.ChallengeRequestFiltering):
    try:
        ipersona_challenge = IpersonaChallengeDocumentSchema()
        challengeId=request.challenge_id
        challenge = ipersona_challenge.get_challenge_by_id(challengeId, nopp=True, dataframe=False)
   
        return {
            "challenge": challenge,
            "success": 200,
            "message": 'Challenge Fetched Successfully.'
        }
    
    except Exception as e:
        logger.error(f"Error creating user session: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": f"Error processing user session: {str(e)}"}
        )
 
@routes.post("/audio_upload_external_async", tags=["Audio Endpoints"])
async def audio_upload_external_async(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    job_profile_id: int = Form(0),
    challenge_id: int = Form(0),
    all_user_id: int = Form(0),
    template: bool = Form(False),
    generate: bool = Form(False),
    external: bool = Form(True),
    challenge: bool = Form(False)
):
    if not file or not file.filename:
        logger.error("Invalid file: No file or filename provided")
        return JSONResponse(
            status_code=400,
            content={
                "transcription": "Failed",
                "status": 400,
                "message": "No file provided or invalid file"
            }
        )
    try:
        logger.info(f"Starting async audio processing for file: {file.filename}")
        audio_dir = data_path('audio')
        os.makedirs(audio_dir, exist_ok=True)
        audio_path = os.path.join(audio_dir, file.filename)
        contents = await file.read()
        with open(audio_path, "wb") as f:
            f.write(contents)
        logger.info("Audio file saved successfully (async route)")

        background_tasks.add_task(
            process_audio_and_save_external,
            audio_path,
            job_profile_id,
            challenge_id,
            all_user_id,
            template,
            generate,
            external,
            challenge
        )
        return {
            "status": 202,
            "job_id": job_profile_id,
            "message": "Audio file received and is being processed in the background."
        }
    except Exception as e:
        logger.error(f"Error during async audio upload: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "transcription": "Failed",
                "status": 500,
                "message": f"System error: {str(e)}"
            }
        )

def process_audio_and_save_external(
        audio_path,
        job_profile_id, 
        challenge_id,
        all_user_id, 
        template, 
        generate, 
        external, 
        challenge):
    try:
        audio_processing_status[job_profile_id] = {"status": "processing", "message": ""}
        transcriber = aai.Transcriber()
        transcript = transcriber.transcribe(audio_path)
        if transcript.status == aai.TranscriptStatus.error:
            error_msg = getattr(transcript, 'error', 'Unknown transcription error')
            logger.error(f"Transcription error: {error_msg}")
            audio_processing_status[job_profile_id] = {"status": "failed", "message": error_msg}
            return
        logger.info("Transcription completed successfully (async route)")
        logger.debug(f"Transcription text: {transcript.text}")
        external_audio_prompt = util.file_reader(prompt_path('external_audio_analysis.txt'))
        realtime_prompt = util.file_reader(prompt_path('realtime_evaluation.txt'))
        external_aud_prompt = external_audio_prompt.replace("{transcription}", str(transcript.text)).replace("{realtime}", str(realtime_prompt))
        # external_aud_prompt = "Hello"
        data = gpt.openai_gpt_assistant_without_streaming(external_aud_prompt)
        response = util.extract_json(data, quite=False)
        run_stage = 'dev'
        transcribe_chat = response if isinstance(response, list) else [response]
        ipersona_user = IpersonaTraineeSchema(run_stage=run_stage)
        trainee_profile_data = ipersona_user.filter_by_alluser_id(
            all_user_id=all_user_id, nopp=True, dataframe=False
        )
        if not trainee_profile_data:
            logger.warn(f"No trainee user profiles found for all_user_id: {all_user_id}")
            audio_processing_status[job_profile_id] = {"status": "failed", "message": "No trainee user profiles found"}
            return
        tinder_user_profile_id = trainee_profile_data.get('id')
        if not tinder_user_profile_id:
            audio_processing_status[job_profile_id] = {"status": "failed", "message": "Invalid trainee profile: missing ID"}
            return
        
        template_id = 0
        message = ''
        type = {
            "template": template,
            "generate": generate,
            "external": external,
            "challenge": challenge
        }
        mode = 'external'
        saved_session = util.create_session(
            mode,
            run_stage,
            type,  
            all_user_id,
            tinder_user_profile_id,
            job_profile_id,
            template_id,
            challenge_id,
            message)
        
        if saved_session:
            sessionId = saved_session['id']
            saved = strapi.save_messages_to_db(transcribe_chat, sessionId)
            status = 'External'
            type = 'job_interview_config'
            def run_overall():
                try:
                    import asyncio
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    overall = loop.run_until_complete(
                        util.overall_interview_evaluations_external(
                            run_stage, 
                            transcribe_chat, 
                            status, 
                            sessionId, 
                            all_user_id, 
                            tinder_user_profile_id, 
                            job_profile_id,
                            type
                        )
                    )
                    
                    audio_processing_status[job_profile_id] = {
                        "status": "done", 
                        "message": "Chat Saved Successfully", 
                        "chat": saved, 
                        "overall": overall
                    }

                except Exception as e:
                    logger.error(f"Error in overall evaluation: {str(e)}", exc_info=True)
                    audio_processing_status[job_profile_id] = {"status": "failed", "message": str(e)}
            t = threading.Thread(target=run_overall)
            t.start()
        else:
            audio_processing_status[job_profile_id] = {"status": "failed", "message": "Chat Not Saved"}
    except Exception as e:
        logger.error(f"Error in background audio processing: {str(e)}", exc_info=True)
        audio_processing_status[job_profile_id] = {"status": "failed", "message": str(e)}

@routes.get("/audio_processing_status", tags=["Audio Endpoints"])
async def audio_processing_status_endpoint(job_id: str):
    status = audio_processing_status.get(job_id)
    if not status:
        return {"status": "not_found", "message": "No processing record found for this job_id."}
    return status



