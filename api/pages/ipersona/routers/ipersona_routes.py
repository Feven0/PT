import time, os, json
import assemblyai as aai
from fastapi import FastAPI, File, UploadFile, Form, Request, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Dict, List, Any, Union, Optional, Tuple
from pydub import AudioSegment
import io
import threading
import asyncio
import requests

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
from api.pages.ipersona.models.endpoint_responses import (
    UpdateSessionModeResponse, 
    ErrorResponse,
    CreateUserSessionResponse,
    sanitize_create_user_session_response
    )
import api.modules.ipersona_parrot_gpt as util
import api.llm.ipersona.ipersona_gpt as gpt
import api.pages.ipersona.models.persona as pemodel
from api.utils.logger import LLPackerLogger
import api.llm.ipersona.ipersona_strapi as strapi
from api.socket.core import sio
from api.services.celery.audio_tasks import (
    process_upload_external_audio_task, 
    process_upload_external_files_task,
    process_upload_external_answer_file_task,
    process_upload_external_answer_with_template_task
)   

from api.pages.ipersona.routers.celery_task import router as task_router

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
        # await sio.emit("processing_update", {"status": "processing cma healt check"})
        sessionId = 1879
        mode = 'Chat'
        run_stage = 'dev'
        updated_mode = util.updating_session_mode(sessionId, mode, run_stage)
        user_profile_id = 197
        template_id = 129
        ipersona_session = IpersonaSessionSchema(run_stage=run_stage)
        session = ipersona_session.filter_by_with_user_template_id(
                    user_profile_id=197,
                    template_id=129, 
                    nopp=True, 
                    dataframe=False
                    ) 
       
        return session
    except Exception as e:
        logger.error(f"Error in health check: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Health check failed: {str(e)}"}
        )

@routes.post(
    "/update_session_mode",
    response_model=UpdateSessionModeResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid input"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    tags=["Session Endpoints"],
    summary="Update the session mode",
    description="Updates the mode of a session and returns the updated status."
)
async def update_session_mode(request: pemodel.UpdateSessionModeRequestReceieved):
    """Update the mode of a session and return the updated status."""
    try:
        sessionId = request.sessionId
        mode = request.mode
        run_stage = request.run_stage
        result = util.updating_session_mode(sessionId, mode, run_stage)
        response_data = {
            "sessionId": result.get("id", sessionId),
            "mode": result.get("metadata", {}).get("mode", mode),
            "status": 200,
            "message": "Session mode updated successfully."
        }
        return UpdateSessionModeResponse(**response_data)
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

@routes.post(
    "/create_user_session",
    # response_model=CreateUserSessionResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid input"},
        404: {"model": ErrorResponse, "description": "Session not found or could not be updated"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    tags=["Session Endpoints"],
    summary="Create a new user session",
    description="Processes user session data and generates interview questions."
)
async def user_session_files(request: pemodel.UserSessionRequestRecieved):
    """
    Process user session data and generate interview questions.
    """
    run_stage = request.run_stage
    mode = request.mode
    template = request.template
    external = request.external
    challenge = request.challenge
    generate = request.generate
    job_profile_id = request.job_profile_id
    all_user_id = request.all_user_id
    template_id = request.template_id
    challenge_id = request.challenge_id

    try:
        logger.info(f"Starting user session creation for user ID: {all_user_id}, job ID: {job_profile_id}")
        # Step 1: Fetch user profile data
        _user_result = util.get_user_data(all_user_id, run_stage)
        if isinstance(_user_result, dict) and _user_result.get("status_code"):
            return JSONResponse(
                status_code=_user_result.get("status_code", 400),
                content=_user_result.get("content", {})
            )
        tinder_user_profile_data, tinder_user_profile_id = _user_result
        # Step 2: Fetch job profile data
        _job_result = util.get_job_data(job_profile_id, run_stage)
        if isinstance(_job_result, dict) and _job_result.get("status_code"):
            return JSONResponse(
                status_code=_job_result.get("status_code", 400),
                content=_job_result.get("content", {})
            )
        tinder_job_data = _job_result
        
        session_incomplete = util.check_if_session_exists(
            run_stage, 
            tinder_user_profile_id, 
            job_profile_id,
            challenge_id,
            template_id,
            template, 
            external, 
            challenge, 
            generate)
        
        print(f"session_template::: {template}")
        print(f"session_challenge::: {challenge}")
        print(f"session_generate::: {generate}")
        print(f"session_external::: {external}")
        
        if session_incomplete:
            logger.info(f"Incomplete session already exists for user ID: {all_user_id}")
            session_data = sanitize_create_user_session_response(session_incomplete)
            session_data["exist"] = True
            return CreateUserSessionResponse(**session_data)
        else:          
            response = await util.create_session_logics(
                run_stage, 
                mode,
                template, 
                external, 
                challenge, 
                generate, 
                job_profile_id, 
                all_user_id, 
                template_id, 
                challenge_id,
                tinder_user_profile_id,
                tinder_job_data, 
                tinder_user_profile_data)
            if response:
                session_data = sanitize_create_user_session_response(response)
                session_data['exist'] = False
            return CreateUserSessionResponse(**session_data)

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
        sessionId = request.data.get('user_session').get('id')
        response = await util.overall_interview_evaluations(
            run_stage, 
            request.data,
            status="Closed",
            sessionId=sessionId, 
            type="Closed")
        
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
    template_id = request.template_id
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
            # return session_chatobserver
        elif challenge_id:
            session_chatobserver = ipersona_overall.filter_by_with_user_and_challenge_id(
                user_profile_id=tinder_user_profile_id,
                challenge_id=challenge_id,
                nopp=True,
                dataframe=False)
        elif template_id:
            # Add template_id support for overall progress calculation
            session_chatobserver = ipersona_overall.filter_by_with_user_and_template_id(
                user_profile_id=tinder_user_profile_id,
                template_id=template_id,
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
        # return data
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

@routes.post("/engagement_template_status", tags=["Session Endpoints"])
def calculate_engagement_template_status(request: pemodel.AllUserSessionRequestRecieved):
    """
    Calculate interview engagement status for a user across all templates.
    
    Retrieves and summarizes a user's engagement with interview sessions grouped by template.
    
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
            "templates": [],
            "status": 400,
            "message": "User ID is required"
        }
        
    try:
        logger.info(f"Calculating template engagement status for user ID: {request.all_user_id}")
        
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
                "templates": [],
                "status": 404,
                "message": "No trainee profiles found for the given user ID"
            }
        
        tinder_user_profile_id = trainee_profile_data.get('id')

        if not tinder_user_profile_id:
            logger.error(f"Invalid trainee profile for user ID: {request.all_user_id}")
            return {
                "all_user_id": request.all_user_id,
                "templates": [],
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

        # Step 3: Fetch and summarize interview data grouped by templates
        data, cursor = util.summarize_template_interviews(
            run_stage,                                                 
            tinder_user_profile_id, 
            filter=query_filter,
            cursor=cursor, 
            since=since, 
            limit=limit,
            information_level=information_level,
            return_skip=return_skip            
        )
        # return data
        logger.info(f"Template engagement summary completed for user ID: {request.all_user_id}")

        # Step 4: Prepare response
        return {
            "all_user_id": request.all_user_id,
            "templates": data, 
            "status": 200, 
            "message": ""
        }

    except Exception as e:
        logger.error(f"Error calculating template engagement status: {str(e)}", exc_info=True)
        return {
            "all_user_id": request.all_user_id if hasattr(request, 'all_user_id') else [], 
            "templates": [],  
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
        
        # Step 2: Keep only sessions that have a non-null tinder_job_profile id
        data = [
            session for session in data
            if (
                isinstance(session, dict)
                and isinstance(session.get('attributes'), dict)
                and isinstance(session['attributes'].get('tinder_job_profile'), dict)
                and isinstance(session['attributes']['tinder_job_profile'].get('data'), dict)
                and session['attributes']['tinder_job_profile']['data'].get('id')
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

        # Step 2: Keep only sessions that have a non-null challenge_document id
        data = [
            session for session in data
            if (
                isinstance(session, dict)
                and isinstance(session.get('attributes'), dict)
                and isinstance(session['attributes'].get('challenge_document'), dict)
                and isinstance(session['attributes']['challenge_document'].get('data'), dict)
                and session['attributes']['challenge_document']['data'].get('id')
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
                    return []

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
                return []

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
                return []

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
@routes.post("/get_all_tinder_templates", tags=["Template Endpoints"])
def get_all_tinder_template(request: pemodel.GetAllTinderTemplateRequestRecieved):
    try:
        cursor = request.cursor
        since = request.since
        limit = request.limit
        run_stage = request.run_stage
        query_filter = request.filter or {}
        # Prepare query parameter
        kwargs = query_filter.copy() if query_filter else {}
        ipersona_tinder = IpersonaTinderTemplateSchema(run_stage=run_stage)
        templates, cursor = ipersona_tinder.get_all_templates(
                cursor=cursor, 
                since=since, 
                limit=limit, 
                nopp=True, 
                dataframe=False,
                **kwargs
                )          
        templates = util.simplify_templates(templates)
        cursor["total"] = len(templates)
        data = util.add_template_columns(templates, cursor, kind='tinder_template', **kwargs)    
# Step 4: Prepare response
        return {
            "templates": data, 
            # "cursor": cursor,                  
            "status": 200, 
            "message": ""
        }
    except Exception as e:
        logger.error(f"Error getting all tinder templates: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": f"Error getting all tinder templates: {str(e)}"}
        )

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
        tinder_challenge_data = ""
        content = ""
        tinder_job_data = ""
        
        if len(job_profile_ids) != 0:
            type='job_interview_config'
            persona_tag = 'parrot_persona'

            _user_result = util.get_user_data(all_user_id, run_stage)
            if isinstance(_user_result, dict) and _user_result.get("status_code"):
                return JSONResponse(
                    status_code=_user_result.get("status_code", 400),
                    content=_user_result.get("content", {})
                )
            tinder_user_profile_data, tinder_user_profile_id = _user_result
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
                
        if len(challenge_ids) == 0 and len(job_profile_ids) == 0:
            # Use content directly with structure instructions for custom JSON format
            structure_instruction = """
                IMPORTANT: Generate interview questions in this exact JSON format:
                [
                    {
                        "sectionType": "Technical",
                        "questions": [
                            {
                                "question": "Your question here",
                                "ideal_answer": "Expected answer here", 
                                "question_number": "1"
                            }
                        ]
                    }
                ]
                Generate 5 questions by default unless specified otherwise in the context.
            """
            content = context + structure_instruction
                

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
 

# ----------------------------------- External File Upload Celery Processing APIS -----------------------------------#

@routes.post("/audio_upload_external", tags=["Audio Endpoints - Celery"])
async def audio_upload_external_celery(
    file: UploadFile = File(...),
    target: Optional[str] = Form(None),
    external: bool = Form(True),
    run_stage: str = Form('dev')
):
    """
    Celery-based replica of audio_upload_external endpoint
    Uses Celery tasks instead of FastAPI background tasks
    """
    try:
        if not file or not file.filename:
            logger.error("Invalid file: No file or filename provided")
            return {"transcription": "Failed", "status": 400, "message": "No file provided or invalid file"}
                    

        # Initialize all target variables
        job_profile_id = None
        challenge_id = None
        template_id = None
        session_id = None
        all_user_id = None

        # Try parsing `target` as JSON
        if target:
            try:
                target_data = json.loads(target)
                # Extract all supported target types
                job_profile_id = target_data.get("job_profile_id")
                challenge_id = target_data.get("challenge_id")
                template_id = target_data.get("template_id")
                session_id = target_data.get("session_id")
                all_user_id = target_data.get("all_user_id")
                print("____________________________________________________________")
                print(job_profile_id)
                print(challenge_id)
                print(template_id)
                print(session_id)
                print(all_user_id)
                print("____________________________________________________________")

                logger.info(f"Parsed target - job_profile_id: {job_profile_id}, challenge_id: {challenge_id}, session_id: {session_id}, all_user_id: {all_user_id}")
            except json.JSONDecodeError:
                logger.error("Failed to parse 'target' as JSON")
                return {"transcription": "Failed", "status": 400, "message": "Failed to parse 'target' as JSON"}


        logger.info(f"Starting async audio processing for file: {file.filename}")
        audio_path = util.get_data_audio_path(file.filename)
        os.makedirs(os.path.dirname(audio_path), exist_ok=True)
        logger.debug(f"Audio file path resolved: {audio_path}")

        contents = await file.read()
        with open(audio_path, "wb") as f:
            f.write(contents)
        logger.info("Audio file saved successfully (async route)")

        # Call Celery task with all target types
        logger.info("Before calling celery task")
        process_upload_external_audio_task.delay(
            file.filename,
            file.content_type,
            audio_path,
            job_profile_id,
            challenge_id,
            template_id,
            session_id,
            all_user_id,
            external,
            run_stage
        )

        logger.info("After calling celery task")
        return {
            "status": 200,
            "message": "Uploaded file received and is being processed in the background."
        }
    except Exception as e:
        logger.error(f"Error in process_audio_upload: {str(e)}")
        return {'status': 500, 'message': str(e)}

@routes.post("/files_upload_external", tags=["Audio Endpoints - Celery"])
async def files_upload_external_celery(
    question_file: UploadFile = File(...),
    answer_file: UploadFile = File(...),
    target: Optional[str] = Form(None),
    external: bool = Form(True),
    run_stage: str = Form('dev')
):
    try:
        # 1. Input Validation for both files
        if not question_file.filename or not answer_file.filename:
            logger.error("Invalid input: Missing Question_file or Answer_file filename.")
            return {'status': 400, 'message': 'Invalid input: Missing Question_file or Answer_file filename.'}
        
        # Initialize all target variables
        job_profile_id = None
        challenge_id = None
        template_id = None
        session_id = None
        all_user_id = None

        # 2. Parse `target` JSON
        # Try parsing `target` as JSON
        if target:
            try:
                target_data = json.loads(target)
                # Extract all supported target types
                job_profile_id = target_data.get("job_profile_id")
                challenge_id = target_data.get("challenge_id")
                template_id = target_data.get("template_id")
                session_id = target_data.get("session_id")
                all_user_id = target_data.get("all_user_id")

                logger.info(f"Parsed target - job_profile_id: {job_profile_id}, challenge_id: {challenge_id}, session_id: {session_id}, all_user_id: {all_user_id}")
            except json.JSONDecodeError:
                logger.error("Failed to parse 'target' as JSON")
                return {"transcription": "Failed", "status": 400, "message": "Failed to parse 'target' as JSON"}

        try:
            audio_dir = util.get_data_audio_path()
            os.makedirs(audio_dir, exist_ok=True)
            logger.debug(f"Audio directory ensured at: {audio_dir}")

            # --- Handle Question_file ---
            question_audio_path = os.path.join(audio_dir, question_file.filename)
            question_contents = await question_file.read()
            
            with open(question_audio_path, "wb") as f:
                f.write(question_contents)
            logger.info(f"Question audio file saved: {question_file.filename}")

            # --- Handle Answer_file ---
            answer_audio_path = os.path.join(audio_dir, answer_file.filename)
            answer_contents = await answer_file.read()

            with open(answer_audio_path, "wb") as f:
                f.write(answer_contents)
            logger.info(f"Answer audio file saved: {answer_file.filename}")
            
            logger.debug("Adding background task for dual audio processing")
        
            process_upload_external_files_task.delay(
                question_filename=question_file.filename,
                question_content_type=question_file.content_type,
                question_audio_path=question_audio_path,
                question_contents=question_contents,
                
                answer_filename=answer_file.filename,
                answer_content_type=answer_file.content_type,
                answer_audio_path=answer_audio_path,
                answer_contents=answer_contents,
                
                job_profile_id=job_profile_id,
                challenge_id=challenge_id,
                template_id=template_id,
                session_id=session_id,
                all_user_id=all_user_id,
                external=external,
                run_stage=run_stage
            )

            logger.info("After calling celery task")
            return {
                "status": 200,
                "message": "Uploaded file received and is being processed in the background."
            }

        except Exception as e:
            logger.error(f"Error in process_audio_upload: {str(e)}")
            return {'status': 500, 'message': str(e)}

    except Exception as e:
        logger.error(f"Error in process_audio_upload: {str(e)}")
        return {'status': 500, 'message': str(e)}

@routes.post("/answer_file_upload_external", tags=["Audio Endpoints - Celery"])
async def files_upload_external_celery(
    answer_file: UploadFile = File(...),
    target: Optional[str] = Form(None),
    external: bool = Form(True),
    run_stage: str = Form('dev')
):
    try:
        # 1. Input Validation for both files
        if not answer_file.filename:
            logger.error("Invalid input: Missing Answer_file filename.")
            return {'status': 400, 'message': 'Invalid input: Missing Answer_file filename.'}
        
        # Initialize all target variables
        job_profile_id = 0
        challenge_id = 0
        session_id = 0
        all_user_id = 0
        template_id = 0

        # 2. Parse `target` JSON
    # Try parsing `target` as JSON
        if target:
            try:
                target_data = json.loads(target)
                # Extract all supported target types
                job_profile_id = target_data.get("job_profile_id", 0)
                challenge_id = target_data.get("challenge_id", 0)
                session_id = target_data.get("session_id", 0)
                all_user_id = target_data.get("all_user_id", 0)
                template_id = target_data.get("template_id", 0)

                logger.info(f"Parsed target - job_profile_id: {job_profile_id}, challenge_id: {challenge_id}, session_id: {session_id}, template_id: {template_id}, all_user_id: {all_user_id}")
            except json.JSONDecodeError:
                logger.error("Failed to parse 'target' as JSON")
                return {"transcription": "Failed", "status": 400, "message": "Failed to parse 'target' as JSON"}

        try:
            audio_dir = util.get_data_audio_path()
            os.makedirs(audio_dir, exist_ok=True)
            logger.debug(f"Audio directory ensured at: {audio_dir}")

            # --- Handle Answer_file ---
            answer_audio_path = os.path.join(audio_dir, answer_file.filename)
            answer_contents = await answer_file.read()

            with open(answer_audio_path, "wb") as f:
                f.write(answer_contents)
            logger.info(f"Answer audio file saved: {answer_file.filename}")
            
            logger.debug("Adding background task for template answer processing")
        
            process_upload_external_answer_with_template_task.delay(
                answer_filename=answer_file.filename,
                answer_content_type=answer_file.content_type,
                answer_audio_path=answer_audio_path,
                answer_contents=answer_contents,
                
                job_profile_id=job_profile_id,
                challenge_id=challenge_id,
                template_id=template_id,
                session_id=session_id,
                all_user_id=all_user_id,
                external=external,
                run_stage=run_stage
            )
        
            logger.info("After calling celery task")
            return {
                "status": 200,
                    "message": "Uploaded file received and is being processed in the background."
            }

        except Exception as e:
                logger.error(f"Error in process_audio_upload: {str(e)}")
                return {'status': 500, 'message': str(e)}

    except Exception as e:
        logger.error(f"Error in process_audio_upload: {str(e)}")
        return {'status': 500, 'message': str(e)}

















































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


# ----------------------------------- External File Upload Processing APIS -----------------------------------#
# @routes.post("/audio_upload", tags=["Audio Endpoints"])
# async def speech_to_text(file: UploadFile = File(...)) -> Dict:
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

#         result = audio_transcription_logics(file.filename, audio_path, file.content_type)

#         if "error" in result:
#             logger.error("Transcription failed: " + result.get("error", "Unknown error"))
#             return JSONResponse(
#                 status_code=result.get("status_code", 500),
#                 content={
#                     "transcription": "Failed",
#                     "status": result.get("status_code", 500),
#                     "message": result.get("error"),
#                     "details": result.get("details", "")
#                 }
#             )

#         # Success
#         logger.info("Transcription completed successfully")
#         return {
#             "transcription": result.get("content", "No transcription returned"),
#             "status": 200,
#             "message": ""
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

# @routes.post("/audio_upload_external_background", tags=["Audio Endpoints"])
# async def audio_upload_external(
#     background_tasks: BackgroundTasks,
#     file: UploadFile = File(...),
#     target: Optional[str] = Form(None),
#     external: bool = Form(True),
#     run_stage: str = Form('dev')
# ):
#     # Initialize variables for parsed target data
#     job_profile_id: Optional[str] = None
#     challenge_id: Optional[str] = None
#     all_user_id: Optional[str] = None
    
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
#     # Try parsing `target` as JSON
#     if target:
#         try:
#             target_data = json.loads(target)
#             job_profile_id = target_data.get("job_profile_id")
#             challenge_id = target_data.get("challenge_id")
#             all_user_id = target_data.get("all_user_id")

#             logger.info(f"Parsed target - job_profile_id: {job_profile_id}, challenge_id: {challenge_id}, all_user_id: {all_user_id}")
#         except json.JSONDecodeError:
#             logger.error("Failed to parse 'target' as JSON")

#     try:
#         logger.info(f"Starting async audio processing for file: {file.filename}")
        
#         # Read file content (this is necessary for the background task)
#         contents = await file.read()
        
#         logger.debug("Adding background task for audio processing")
#         background_tasks.add_task(
#             process_audio_and_save_external,
#             file.filename,
#             file.content_type,
#             contents,  # Pass raw content instead of file path
#             job_profile_id,
#             challenge_id,
#             all_user_id,
#             external,
#             run_stage
#         )
#         return {
#             "status": 200,
#             "message": "Uploaded file received and is being processed in the background."
#         }
#     except Exception as e:
#         logger.error(f"Error during async audio upload: {str(e)}", exc_info=True)
#         return JSONResponse(
#             status_code=500,
#             content={
#                 "transcription": "Failed",
#                 "status": 500,
#                 "message": f"System error: {str(e)}"
#             }
#         )

# @routes.post("/files_upload_external_background", tags=["Audio Endpoints"])
# async def files_upload_external(
#     background_tasks: BackgroundTasks,
#     Question_file: UploadFile = File(...),
#     Answer_file: UploadFile = File(...),
#     target: Optional[str] = Form(None),
#     external: bool = Form(True),
#     run_stage: str = Form('dev')
# ):
#     # 1. Input Validation for both files
#     if not Question_file.filename or not Answer_file.filename:
#         logger.error("Invalid input: Missing Question_file or Answer_file filename.")
#         return JSONResponse(
#             status_code=400,
#             content={
#                 "status": 400,
#                 "message": "Both Question_file and Answer_file are required."
#             }
#         )

#     # Initialize variables for parsed target data
#     job_profile_id: Optional[str] = None
#     challenge_id: Optional[str] = None
#     all_user_id: Optional[str] = None

#     # 2. Parse `target` JSON
#     if target:
#         try:
#             target_data: Dict[str, Any] = json.loads(target)
#             job_profile_id = target_data.get("job_profile_id")
#             challenge_id = target_data.get("challenge_id")
#             all_user_id = target_data.get("all_user_id")

#             logger.info(f"Parsed target - job_profile_id: {job_profile_id}, challenge_id: {challenge_id}, all_user_id: {all_user_id}")
#         except json.JSONDecodeError:
#             logger.error("Failed to parse 'target' as JSON. Proceeding without target data.")
#     try:
#         logger.info(f"Starting dual file processing")
        
#         # Read both files (necessary for background task)
#         question_contents = await Question_file.read()
#         answer_contents = await Answer_file.read()
        
#         logger.debug("Adding background task for dual audio processing")
#         background_tasks.add_task(
#             process_upload_external_files,
#             question_filename=Question_file.filename,
#             question_content_type=Question_file.content_type,
#             question_contents=question_contents,
            
#             answer_filename=Answer_file.filename,
#             answer_content_type=Answer_file.content_type,
#             answer_contents=answer_contents,
            
#             job_profile_id=job_profile_id,
#             challenge_id=challenge_id,
#             all_user_id=all_user_id,
#             external=external,
#             run_stage=run_stage
#         )
        
#         return {
#             "status": 200,
#             "message": "Both audio files received and are being processed in the background."
#         }

#     except Exception as e:
#         logger.error(f"Error during async dual audio upload: {str(e)}", exc_info=True)
#         return JSONResponse(
#             status_code=500,
#             content={
#                 "transcription": "Failed", 
#                 "status": 500,
#                 "message": f"System error during file upload: {str(e)}"
#             }
#         )
    

# async def process_audio_and_save_external(
#         filename,
#         content_type,
#         contents,
#         job_profile_id, 
#         challenge_id,
#         all_user_id, 
#         external,
#         run_stage):
#     try:
#         logger.info(f"🔊 Processing audio file: {filename}")
#         logger.info(f"🔍 DEBUG: Starting background task with job_profile_id: {job_profile_id}")
        
#         # Save file to disk in background task
#         audio_dir = data_path('audio')
#         os.makedirs(audio_dir, exist_ok=True)
#         audio_path = os.path.join(audio_dir, filename)
        
#         with open(audio_path, "wb") as f:
#             f.write(contents)
#         logger.info("Audio file saved successfully in background task")
        
#         # Update status stores and emit WebSocket update
#         audio_processing_status[job_profile_id] = {"status": "processing", "message": "Starting audio processing"}
      
#         template_id = 0
#         message = ''
#         template = False
#         challenge = False  
#         mode = None
#         transcript = None  # Initialize transcript variable

#         try:
#             if "audio" in content_type or "video" in content_type:
#                 original_format = content_type.split("/")[-1].lower()
#                 if original_format != "mpeg" and original_format != "mp3":
#                     logger.info(f"🔄 Converting media file from {original_format} to mp3")
#                     contents = convert_to_mp3(contents, original_format)
#                     converted_filename = filename.rsplit(".", 1)[0] + ".mp3"
#                     audio_path = os.path.join(data_path("audio"), converted_filename)
                    
#                     # Actually save the converted MP3 file to disk
#                     with open(audio_path, "wb") as f:
#                         f.write(contents)
#                     logger.success(f"🎧 MP3 file saved to: {audio_path}")
#                 else:
#                     logger.info("✅ File already in mp3 format. Skipping conversion.")
#                     audio_path = os.path.join(data_path("audio"), filename)
#                     os.makedirs(os.path.dirname(audio_path), exist_ok=True)
#                     with open(audio_path, "wb") as f:
#                         f.write(contents)
#                     logger.success(f"🎧 MP3 file saved to: {audio_path}")
#                 logger.info(f"🔍 DEBUG: Starting transcription for job_profile_id: {job_profile_id}")
                
#                 # Update status stores and emit WebSocket update
#                 audio_processing_status[job_profile_id] = {"status": "processing", "message": "Starting transcription"}
                
#                 result =  audio_transcription_logics(
#                     filename=filename,
#                     audio_path=audio_path,
#                     content_type="audio/mpeg"
#                 )

#                 if "error" in result:
#                     return JSONResponse(
#                         status_code=result.get("status_code", 500),
#                         content={
#                             "result": "Failed",
#                             "status": result.get("status_code", 500),
#                             "message": result.get("error"),
#                             "details": result.get("details", "")
#                         }
#                     )
                
#                 logger.debug("Initializing transcription")
#                 transcript = result.get("content", "No transcription returned")

#             elif any(x in content_type for x in ["text", "pdf", "msword", "officedocument"]):
#                 logger.info(f"📝 Text-based file detected: {filename}")
#                 result = content_extraction_logics(filename, contents, content_type)
           
#                 if "error" in result:
#                     logger.error(f"❌ Text extraction failed: {result['error']}")
#                     audio_processing_status[job_profile_id] = {
#                         "status": "failed",
#                         "message": result.get("error")
#                     }
#                     return

#                 logger.success(f"✅ Text extraction successful: {filename}")
#                 logger.info(f"🔍 DEBUG: Transcription completed for job_profile_id: {job_profile_id}")
                
#                 # Update status stores and emit WebSocket update
#                 audio_processing_status[job_profile_id] = {
#                     "status": "processing",
#                     "message": "Transcription completed, starting analysis"
#                 }
                
#                 logger.debug("Initializing transcription")
#                 transcript = result.get("content", "No transcription returned")

#             else:
#                 logger.warn(f"🚫 Unsupported file type: {content_type}")
#                 audio_processing_status[job_profile_id] = {
#                     "status": "failed",
#                     "message": f"Unsupported file type: {content_type}"
#                 }
#                 return

#         except Exception as conversion_error:
#             logger.error(f"❌ MP3 conversion failed: {conversion_error}", exc_info=True)
#             audio_processing_status[job_profile_id] = {
#                 "status": "failed",
#                 "message": f"MP3 conversion failed: {conversion_error}"
#             }
#             return

#         # --- Existing logic continues here ---
#         logger.debug("Fetching trainee profile data")
#         ipersona_user = IpersonaTraineeSchema(run_stage=run_stage)
#         trainee_profile_data = ipersona_user.filter_by_alluser_id(
#             all_user_id=all_user_id, nopp=True, dataframe=False
#         )
#         if not trainee_profile_data:
#             logger.warn(f"No trainee user profiles found for all_user_id: {all_user_id}")
#             audio_processing_status[job_profile_id] = {"status": "failed", "message": "No trainee user profiles found"}
#             return

#         tinder_user_profile_id = trainee_profile_data.get('id')
#         if not tinder_user_profile_id:
#             logger.error("Invalid trainee profile: missing ID")
#             audio_processing_status[job_profile_id] = {"status": "failed", "message": "Invalid trainee profile: missing ID"}
#             return

#         logger.debug("Reading external audio analysis prompt")
#         external_audio_prompt = util.file_reader(prompt_path('external_audio_analysis.txt'))
#         realtime_prompt = util.file_reader(prompt_path('realtime_evaluation.txt'))

#         logger.debug("Replacing placeholders in prompts")
#         external_aud_prompt = external_audio_prompt.replace("{transcription}", str(transcript)).replace("{realtime}", str(realtime_prompt))

#         logger.debug("Sending prompt to GPT for analysis")
#         data = gpt.openai_gpt_assistant_without_streaming(external_aud_prompt)
#         response = util.extract_json(data, quite=False)

#         if not response:
#             logger.error("❌ Failed to process upload file: No data returned from transcription")
#             audio_processing_status[job_profile_id] = {"status": "failed", "message": "No data returned"}
#             return
        
#         logger.debug("Creating session for audio processing")
#         saved_session = util.create_session(
#             mode,
#             run_stage,
#             template, 
#             external, 
#             challenge, 
#             all_user_id,
#             tinder_user_profile_id,
#             job_profile_id,
#             template_id,
#             challenge_id,
#             message
#         )

#         if saved_session:
#             sessionId = saved_session['id']
#             logger.info(f"📥 Session created successfully with ID: {sessionId}")
#             logger.debug("Saving transcribed chat to database")
#             saved = strapi.save_messages_to_db(response, sessionId)

#             logger.debug("Starting overall evaluation in a separate thread")
#             def run_overall():
#                 try:
#                     loop = asyncio.new_event_loop()
#                     asyncio.set_event_loop(loop)
#                     overall = loop.run_until_complete(
#                         util.overall_interview_evaluations_external(
#                             run_stage, 
#                             response, 
#                             'External', 
#                             sessionId, 
#                             all_user_id, 
#                             tinder_user_profile_id, 
#                             job_profile_id,
#                             'job_interview_config'
#                         )
#                     )
#                     logger.info("✅ Overall evaluation completed successfully")
                    
#                     # Update status stores and emit WebSocket update for completion
#                     audio_processing_status[job_profile_id] = {
#                         "status": "done", 
#                         "message": "Chat Saved Successfully", 
#                         "chat": saved, 
#                         "overall": overall
#                     }
#                     # Emit WebSocket update (in thread - use create_task)
#                     # try:
#                     #     asyncio.create_task(sio.emit("processing_update_success", {"status": "Processing 'the uploaded files completed successfully!"}))
#                     # except Exception as e:
#                     #     logger.warn(f"Failed to emit WebSocket update: {e}")

#                 except Exception as e:
#                     logger.error(f"Error in overall evaluation: {str(e)}", exc_info=True)
#                     audio_processing_status[job_profile_id] = {"status": "failed", "message": str(e)}

#             t = threading.Thread(target=run_overall)
#             t.start()
#             logger.success("🎉 EXTERNAL AUDIO PROCESSED AND SAVED SUCCESSFULLY!")
#         else:
#             logger.error("❌ Failed to save session")
#             audio_processing_status[job_profile_id] = {"status": "failed", "message": "Chat Not Saved"}
  
#     except Exception as e:
#         logger.error(f"🔥 Error in background audio processing: {str(e)}", exc_info=True)
        
#         # Update status stores and emit WebSocket update for error
#         audio_processing_status[job_profile_id] = {"status": "failed", "message": str(e)}
#         # try:
#         #         asyncio.create_task(sio.emit("processing_update_failed", {"status": "Processing failed. Likely causes: not interview content, unclear audio, or no detectable Q/A. Please re-upload a clear interview file, then try again."}))

#         # except Exception as emit_error:
#         #     logger.warn(f"Failed to emit WebSocket update: {emit_error}")

# def content_extraction_logics(filename: str, content: bytes, content_type: str) -> dict:
#     try:
#         files = {
#                     'file': (filename, content, content_type)
#                 }
#         data = {
#             'request_source': 'text_extraction_endpoint',
#             'visual_description': 'false',
#             'description_prompt': 'Extract readable content',
#             'input_format': 'text'
#         }

#         endpoint_url = "https://content-extractor.10academy.org/content-extractor/extract"
#         response = requests.post(endpoint_url, data=data, files=files, timeout=60)
#         response.raise_for_status()
#         result = response.json()
#         return result

#     except requests.exceptions.HTTPError as e:
#         return {
#             "error": f"HTTP error: {e}",
#             "details": e.response.text,
#             "status_code": e.response.status_code
#         }

#     except Exception as e:
#         return {
#             "error": f"Unexpected error: {str(e)}",
#             "status_code": 500
#         }

# def audio_transcription_logics(filename: str, audio_path: str, content_type: str) -> dict:
#     try:
#         # Debug: Check if file exists before opening
#         import os
#         if not os.path.exists(audio_path):
#             logger.error(f"❌ Audio file does not exist: {audio_path}")
#             return {
#                 "error": f"Audio file not found: {audio_path}",
#                 "status_code": 404
#             }
        
#         logger.info(f"✅ Audio file exists, size: {os.path.getsize(audio_path)} bytes")
        
#         # Send to the content-extractor transcription endpoint
#         endpoint_url = "https://content-extractor.10academy.org/content-extractor/audio_transcript"

#         with open(audio_path, 'rb') as audio_file:
#             files = {
#                 'file': (filename, audio_file, content_type)
#             }
#             data = {
#                 'request_id': 'audio-upload-001',
#                 'request_source': 'fastapi_audio_upload',
#                 'prompt': 'Extract the text from the audio file.',
#                 'llm_provider': 'openai',
#                 'llm_model': 'gpt-4o'
#             }

#             logger.debug("Sending audio file to external transcription endpoint...")
#             response = requests.post(endpoint_url, files=files, data=data, timeout=90)
#             response.raise_for_status()
#             result = response.json()
  
#         return result

#     except requests.exceptions.HTTPError as e:
#         return {
#             "error": f"HTTP error: {e}",
#             "details": e.response.text,
#             "status_code": e.response.status_code
#         }

#     except Exception as e:
#         return {
#             "error": f"Unexpected error: {str(e)}",
#             "status_code": 500
#         }

# def convert_to_mp3(input_bytes: bytes, original_format: str) -> bytes:
#     logger.info(f"Starting conversion of format: {original_format}")
#     try:
#         audio = AudioSegment.from_file(io.BytesIO(input_bytes), format=original_format)
#         mp3_io = io.BytesIO()
#         audio.export(mp3_io, format="mp3")
#         mp3_bytes = mp3_io.getvalue()
#         logger.info(f"Conversion successful. Original size: {len(input_bytes) / 1024 / 1024:.2f} MB | MP3 size: {len(mp3_bytes) / 1024 / 1024:.2f} MB")
#         return mp3_bytes
#     except Exception as e:
#         logger.error(f"Error during mp3 conversion: {e}")
#         raise

# # --- New Helper Function for Single File Processing ---
# def _process_and_transcribe_file(
#     filename: str,
#     content_type: str,
#     contents: bytes,
#     file_type_label: str 
# ) -> Tuple[Optional[str], Optional[str]]: 
#     """
#     Handles the common logic for converting, saving, and transcribing/extracting content from a single file.
#     Returns the transcript if successful, or None and an error message if failed.
#     """
#     logger.info(f"🔊 Processing {file_type_label} file: {filename}")
    
#     try:
#         audio_dir = data_path("audio") 
#         os.makedirs(audio_dir, exist_ok=True) 
#         final_file_path = os.path.join(audio_dir, filename) 

#         transcript: Optional[str] = None

#         if "audio" in content_type or "video" in content_type:
#             original_format = content_type.split("/")[-1].lower()
            
#             if original_format not in ["mpeg", "mp3", "wav", "mp4", "webm"]:
#                 logger.info(f"🔄 Converting {file_type_label} media file from {original_format} to mp3")
#                 contents = convert_to_mp3(contents, original_format)
#                 final_file_path = os.path.join(audio_dir, filename.rsplit(".", 1)[0] + ".mp3")
                
#                 with open(final_file_path, "wb") as f:
#                     f.write(contents)
#                 logger.success(f"🎧 {file_type_label} MP3 file saved to: {final_file_path}")
#             else:
#                 logger.info(f"✅ {file_type_label} file already in supported audio/video format. Skipping re-saving.")
   
#             result = audio_transcription_logics( 
#                 filename=filename,
#                 audio_path=final_file_path,
#                 content_type="audio/mpeg" 
#             )
         
#             if "error" in result:
#                 return None, f"Transcription failed: {result['error']}"
            
#             transcript = result.get("content", "No transcription returned")
#             prompt = f"""
#                 You are given a raw block of text transcribed from an interview. This text may include either interview **questions** or **answers**, but not both at the same time.

#                 Your task is to segment this text into a list of **logically grouped full responses** — where each item in the list represents **a complete question or answer**, not just an individual sentence or phrase.

#                 🧠 IMPORTANT RULES:
#                 - DO NOT break an answer or question into parts unless there's a **clear topic shift or speaker change**.
#                 - Consider the **semantic flow** and meaning of the text — some responses are long and should remain as one block.
#                 - DO NOT split just because a sentence ends. Multiple sentences can and often do belong to the same complete response.
#                 - Only split when it is evident that a **new question** or **new response** has begun.
#                 - If unsure whether to split or not — DO NOT split. Keep it as one unified chunk.

#                 Your output must be a JSON list of grouped conversation turns, like:
#                 [
#                 "First full question or answer here.",
#                 "Second full question or answer here.",
#                 ...
#                 ]

#                 Now segment the following transcription:
#                 {transcript}
#                 """
#             transcript = gpt.openai_gpt_assistant_without_streaming(prompt) 

#             logger.debug(f"{file_type_label} transcription initialized")

#         elif any(x in content_type for x in ["text", "pdf", "msword", "officedocument"]):
#             logger.info(f"📝 {file_type_label} text-based file detected: {filename}")

#             # Assuming you save it, then extract.
#             with open(final_file_path, "wb") as f:
#                 f.write(contents)
#             logger.success(f"💾 {file_type_label} text file saved to: {final_file_path}")

#             result = content_extraction_logics(filename, contents, content_type) # Ensure this is async

#             if "error" in result:
#                 return None, f"Text extraction failed: {result['error']}"

#             transcript = result.get("content", "No content returned")
#             prompt = f"""
#                 You are given a raw block of text transcribed from an interview. This text may include either interview **questions** or **answers**, but not both at the same time.

#                 Your task is to segment this text into a list of **logically grouped full responses** — where each item in the list represents **a complete question or answer**, not just an individual sentence or phrase.

#                 🧠 IMPORTANT RULES:
#                 - DO NOT break an answer or question into parts unless there's a **clear topic shift or speaker change**.
#                 - Consider the **semantic flow** and meaning of the text — some responses are long and should remain as one block.
#                 - DO NOT split just because a sentence ends. Multiple sentences can and often do belong to the same complete response.
#                 - Only split when it is evident that a **new question** or **new response** has begun.
#                 - If unsure whether to split or not — DO NOT split. Keep it as one unified chunk.

#                 Your output must be a JSON list of grouped conversation turns, like:
#                 [
#                 "First full question or answer here.",
#                 "Second full question or answer here.",
#                 ...
#                 ]

#                 Now segment the following transcription:
#                 {transcript}
#                 """

#             transcript = gpt.openai_gpt_assistant_without_streaming(prompt) # Ensure async
         
#             logger.success(f"✅ {file_type_label} text extraction successful: {filename}")
#             logger.debug(f"{file_type_label} content extraction initialized")

#         else:
#             return None, f"Unsupported file type for {file_type_label}: {content_type}"

#         return transcript, None # Success

#     except Exception as e:
#         logger.error(f"❌ Error in {file_type_label} file processing: {e}", exc_info=True)
#         return None, f"Processing failed for {file_type_label}: {e}"

# # --- Main Background Task Function ---
# async def process_upload_external_files(
#     question_filename: str,
#     question_content_type: str,
#     question_contents: bytes,
#     answer_filename: str,
#     answer_content_type: str,
#     answer_contents: bytes,
#     job_profile_id: Optional[str],
#     challenge_id: Optional[str],
#     all_user_id: Optional[str],
#     external: bool,
#     run_stage: str
# ):
#     try:
#         if not job_profile_id:
#             logger.error("job_profile_id is missing, cannot track processing status.")
#             return
        
#         audio_processing_status[job_profile_id] = {"status": "processing", "message": "Starting dual file processing."}
#         logger.info(f"🔊 Starting combined processing for Job ID: {job_profile_id}")

#         # Save files to disk in background task
#         audio_dir = data_path('audio')
#         os.makedirs(audio_dir, exist_ok=True)
        
#         question_audio_path = os.path.join(audio_dir, question_filename)
#         answer_audio_path = os.path.join(audio_dir, answer_filename)
        
#         with open(question_audio_path, "wb") as f:
#             f.write(question_contents)
#         logger.info(f"Question audio file saved: {question_filename}")
        
#         with open(answer_audio_path, "wb") as f:
#             f.write(answer_contents)
#         logger.info(f"Answer audio file saved: {answer_filename}")

#         # --- Process Question File using helper ---
#         question_transcript, question_error_msg = _process_and_transcribe_file(
#             question_filename, question_content_type, question_contents, "Question"
#         )
  
    
#         if question_error_msg:
#             audio_processing_status[job_profile_id] = {"status": "failed", "message": f"Question file processing failed: {question_error_msg}"}
#             return

#         # --- Process Answer File using helper ---
#         answer_transcript, answer_error_msg = _process_and_transcribe_file(
#             answer_filename, answer_content_type, answer_contents, "Answer"
#         )
#         if answer_error_msg:
#             audio_processing_status[job_profile_id] = {"status": "failed", "message": f"Answer file processing failed: {answer_error_msg}"}
#             return
        
           
#         # Ensure transcripts are not None after helper calls (should be handled by error_msg)
#         if question_transcript is None or answer_transcript is None:
#             logger.error("One or both transcripts are missing after file processing. Cannot proceed.")
#             audio_processing_status[job_profile_id] = {"status": "failed", "message": "Missing transcripts for analysis."}
#             return

#         logger.info("✅ Both question and answer files processed successfully.")        

#         # --- Remaining Original Logic (now much cleaner) ---
#         logger.debug("Fetching trainee profile data")
#         ipersona_user = IpersonaTraineeSchema(run_stage=run_stage)
#         trainee_profile_data = ipersona_user.filter_by_alluser_id(
#             all_user_id=all_user_id, nopp=True, dataframe=False
#         )
#         if not trainee_profile_data:
#             logger.warn(f"No trainee user profiles found for all_user_id: {all_user_id}")
#             audio_processing_status[job_profile_id] = {"status": "failed", "message": "No trainee user profiles found"}
#             return

#         tinder_user_profile_id = trainee_profile_data.get('id')
#         if not tinder_user_profile_id:
#             logger.error("Invalid trainee profile: missing ID")
#             audio_processing_status[job_profile_id] = {"status": "failed", "message": "Invalid trainee profile: missing ID"}
#             return

#         logger.debug("Reading external audio analysis prompt")
#         external_audio_prompt = util.file_reader(prompt_path('external_audio_analysis_for_separate_inputs.txt'))
#         external_all_file_prompt = util.file_reader(prompt_path('external_audio_analysis.txt'))
#         answer_question_matching = util.file_reader(prompt_path('answer_question_match.txt'))
#         realtime_prompt = util.file_reader(prompt_path('realtime_evaluation.txt'))

#         logger.debug("Replacing placeholders in prompts")
#         answer_question_match_scoring = answer_question_matching.replace("{questions_data}", question_transcript)\
#                                                    .replace("{answers_data}", answer_transcript)

#         logger.debug("Sending prompt to GPT for analysis")
#         data = gpt.openai_gpt_assistant_without_streaming(answer_question_match_scoring) # Ensure async
#         response = util.extract_json(data, quite=False)

#         # Filter out items with relevance_score > 80
#         filtered_data = [
#             {'question': item['question'], 'answer': item['answer']}
#             for item in response
#             if item['relevance_score'] >= 90
#         ]

#         # return response
#         if not filtered_data:
#             # Get detailed error information for user action
#             relevance_scores = [item.get('relevance_score', 0) for item in response] if response else []
#             max_score = max(relevance_scores) if relevance_scores else 0
            
#             logger.error("❌ Failed to process upload files: No Valuable matched question-answer data returned from LLM analysis")
            
#             # Update status stores and emit WebSocket update with detailed error
#             audio_processing_status[job_profile_id] = {
#                 "status": "failed", 
#                 "message": f"No valuable matches found (best score: {max_score}/100, need 90+)"
#             }
#             # Emit WebSocket update
#             try:
#                 logger.info(f"[SOCKET EMIT] Processing update sent for job")
#                 await sio.emit("processing_update_failed", {"status": f"❌ No valuable matches found between the question and answer files for Job with id: {job_profile_id}. Please re-upload a clear interview file, then try again."})
      
#             except Exception as emit_error:
#                 logger.warn(f"Failed to emit WebSocket update: {emit_error}")
#             return
        
#         external_audio_prompt = external_audio_prompt.replace("{question_answer_data}", str(filtered_data))\
#                                                    .replace("{realtime}", str(realtime_prompt))
#         # external_all_file_prompt = external_all_file_prompt.replace("{transcription}", str(filtered_data))\
#         #                                                   .replace("{realtime}", str(realtime_prompt))
        
#         data = gpt.openai_gpt_assistant_without_streaming(external_audio_prompt) # Ensure async
#         response = util.extract_json(data, quite=False)

#         # Initialize these for util.create_session (as per original logic)
#         template_id = 0 
#         message = '' 
#         template = False
#         challenge = False  
#         mode = None 

#         saved_session = util.create_session(
#             mode,
#             run_stage,
#             template, 
#             external, 
#             challenge, 
#             all_user_id,
#             tinder_user_profile_id,
#             job_profile_id,
#             template_id,
#             challenge_id,
#             message
#         )
       
#         sessionId = saved_session.get('id') if isinstance(saved_session, dict) else None
#         if not sessionId:
#             logger.error(f"Saved session missing id. saved_session={saved_session}")
#             audio_processing_status[job_profile_id] = {"status": "failed", "message": "Session missing id"}
#             return
#         if saved_session:
#             sessionId = saved_session['id']
#             logger.info(f"📥 Session created successfully with ID: {sessionId}")
#             logger.debug("Saving analyzed chat to database")
#             saved = strapi.save_messages_to_db(response, sessionId) 

#             logger.debug("Starting overall evaluation in a separate thread")
#             async def run_overall_sync_wrapper():
#                 try:
#                     # Run the blocking operation in a thread pool
#                     loop = asyncio.get_event_loop()
#                     overall = await loop.run_in_executor(
#                         None,  # Use default thread pool
#                         lambda: util.overall_interview_evaluations_external(
#                             run_stage, 
#                             response, 
#                             'External', 
#                             sessionId, 
#                             all_user_id, 
#                             tinder_user_profile_id, 
#                             job_profile_id,
#                             'job_interview_config'
#                         )
#                     )
#                     logger.info("✅ Overall evaluation completed successfully")
                    
#                     # Update status stores and emit WebSocket update for completion
#                     audio_processing_status[job_profile_id] = {
#                         "status": "done", 
#                         "message": "Chat Saved Successfully", 
#                         "chat": saved, 
#                         "overall": overall
#                     }
                    
#                     # Now we can use await sio.emit!
#                     await sio.emit("processing_update_success", {"status": "Processing the uploaded interview files completed successfully!"})
#                     logger.info(f"[SOCKET EMIT TRY] Processing update sent for job")
                    
#                 except Exception as e:
#                     logger.error(f"Error in overall evaluation: {str(e)}", exc_info=True)
#                     audio_processing_status[job_profile_id] = {"status": "failed", "message": str(e)}

#             # Start the async task
#             asyncio.create_task(run_overall_sync_wrapper())
#             logger.success("🎉 EXTERNAL DUAL AUDIO PROCESSED AND SAVED SUCCESSFULLY!")
#         else:
#             logger.error("❌ Failed to save session")
#             audio_processing_status[job_profile_id] = {"status": "failed", "message": "Session Not Saved"}
  
#     except Exception as e:
#         logger.error(f"🔥 Critical error in dual audio background processing: {str(e)}", exc_info=True)
#         if job_profile_id:
#             audio_processing_status[job_profile_id] = {"status": "failed", "message": f"System error: {str(e)}"}

# def sanitize_create_user_session_response(data):
#     return {
#         "id": data.get("id") or "",
#         "status": str(data.get("status") or "Incomplete"),
#         "mode": str(data.get("mode") or ""),
#         "user_profile_id": data.get("user_profile_id") or "",
#         "job_profile_id": data.get("job_profile_id") or "",
#         "template_id": data.get("template_id") or "",
#         "challenge_id": data.get("challenge_id") or "",
#     }


# Include task management routes
routes.include_router(task_router)



