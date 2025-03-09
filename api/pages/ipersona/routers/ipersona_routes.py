
import time, os
import assemblyai as aai
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi import FastAPI, File, UploadFile, Form, Request
from fastapi.responses import JSONResponse
from typing import Dict, List, Tuple, Any, Optional, Union
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
from api.utils.request_manager import JobReactionManager
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
    Convert an audio file to text using a speech-to-text service.
    
    Processes an uploaded audio file, saves it to the specified location,
    and uses an Assembly AI transcriber to convert the audio to text.
    
    Parameters
    ----------
    file : UploadFile
        The audio file uploaded by the user.
        
    Returns
    -------
    Dict[str, Any]
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
    
@routes.post("/create_user_session")
async def user_session_files(request: pemodel.UserSessionRequestRecieved):
    """
    Process user session data and generate interview questions.
    
    Creates a persona from job descriptions, generates interview questions,
    and stores session data in the database.
    
    Parameters
    ----------
    request : pemodel.UserSessionRequestRecieved
        Object containing:
        - all_user_id: User identifier
        - job_profile_id: Job profile identifier
        
    Returns
    -------
    Dict[str, Any]
        Session data with generated questions removed or error response
        
    Raises
    ------
    Exception
        If any error occurs during processing
    """
    run_stage = request.run_stage

    if not request or not request.all_user_id or not request.job_profile_id:
        logger.error("Invalid request: Missing required parameters")
        return JSONResponse(
            status_code=400,
            content={"error": "Missing required parameters: all_user_id or job_profile_id"}
        )
        
    try:
        logger.info(f"Starting user session creation for user ID: {request.all_user_id}, job ID: {request.job_profile_id}")

        # Step 1: Fetch trainee profile data
        ipersona_user = IpersonaTraineeSchema(run_stage=run_stage)
        trainee_profile_data = ipersona_user.filter_by_alluser_id(
            all_user_id=request.all_user_id, nopp=True, dataframe=False
        )
    
        if not trainee_profile_data:
            logger.warn(f"No trainee user profiles found for all_user_id: {request.all_user_id}")
            return JSONResponse(
                status_code=404,
                content={"error": "No trainee user profiles found for the given all_user_id"}
            )

        tinder_user_profile_id = trainee_profile_data.get('id')
        if not tinder_user_profile_id:
            return JSONResponse(
                status_code=500,
                content={"error": "Invalid trainee profile: missing ID"}
            )
            
        tinder_user_profile_data = util.extract_trainee_neccessary_values(trainee_profile_data)
        logger.info(f"User profile data extracted for user ID: {tinder_user_profile_id}")

        # Step 2: Fetch job profile data
        ipersona_job = IpersonaJobSchema(run_stage=run_stage)
        tinder_job_data = ipersona_job.filter_by_job_id(
            job_profile_id=request.job_profile_id, nopp=True, dataframe=False
        )

        if not tinder_job_data:
            logger.warn(f"No job data found for job_profile_id: {request.job_profile_id}")
            return JSONResponse(
                status_code=404,
                content={"error": "No job data found for the job_profile_id"}
            )

        tinder_job_data = util.extract_job_neccessary_values(tinder_job_data)
        logger.info(f"Job data extracted for job_profile_id: {request.job_profile_id}")

        # Step 3: Create persona and generate questions
        created_persona = util.create_persona(str(tinder_job_data))
        
        # Load and format prompt templates
        prompt_text = util.file_reader(prompt_path('persona.txt'))
        generated_persona = prompt_text \
            .replace("{hr_persona}", created_persona) \
            .replace("{job_description}", str(tinder_job_data)) \
            .replace("{profile}", str(tinder_user_profile_data))

        question_template = util.file_reader(prompt_path('generate_question.txt'))
        msg = question_template \
            .replace("{introduction_count}", str(1)) \
            .replace("{background_count}", str(2)) \
            .replace("{technical_count}", str(2)) \
            .replace("{behavioral_count}", str(2)) \
            .replace("{ability_count}", str(2))\
            .replace("{closing_count}", str(1))

        # Generate interview questions
        content = generated_persona + msg
        response = gpt.openai_gpt_assistant_without_streaming(content)
        
        if not response:
            logger.error("Failed to generate questions: Empty AI response")
            return JSONResponse(
                status_code=500,
                content={"error": "Failed to generate interview questions"}
            )
            
        generated_question_json = util.extract_json(response, quite=False)
        logger.info("Persona and questions generated successfully")

        # Step 4: Add question numbers
        question_number = 1
        for category, questions in generated_question_json.items():
            for question in questions:
                question["question_number"] = str(question_number)
                question_number += 1

        # Step 5: Save session data
        session_data = {
            "slug": str(f"all_user_id: {request.all_user_id}"),
            "status": "Incomplete",
            "attributes": {
                "persona": generated_persona,
                "generated_questions": generated_question_json
            },
            "user_profile_id": tinder_user_profile_id,
            "job_profile_id": request.job_profile_id
        }
        
        ipersona_session = IpersonaSessionSchema(run_stage=run_stage)
        saved_session = ipersona_session.save_session(
            params=session_data, return_object=True, nopp=True, dataframe=False
        )

        if not saved_session:
            logger.error("Failed to save session")
            return JSONResponse(
                status_code=500,
                content={"error": "Failed to save session data"}
            )
            
        logger.info(f"Session created successfully with ID: {saved_session.get('id', 'unknown')}")
        
        # Remove large questions data before returning
        saved_session = util.remove_key(saved_session, 'generated_questions')
        return saved_session

    except Exception as e:
        logger.error(f"Error creating user session: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": f"Error processing user session: {str(e)}"}
        )
        
@routes.post("/clarify")
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

@routes.post("/delete_session")
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

@routes.post("/close_session")
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

@routes.post("/calculate_session_overall_progress")
async def calculate_overall_progress(request: pemodel.UserSessionRequestRecieved):
    """
    Fetch overall progress metrics for a job.

    Parameters:
    ----------
    request : pemodel.UserSessionRequestRecieved
        The request object containing user and job profile data.

    Returns:
    -------
    JSONResponse or dict
        A dictionary containing the overall progress metrics, or an error message if an exception occurs.
    """
    run_stage = request.run_stage

    try:
        ipersona_overall = IpersonaSessionOverallObserverSchema(run_stage=run_stage)
        ipersona_user = IpersonaTraineeSchema(run_stage=run_stage)

        trainee_profile_data = ipersona_user.filter_by_alluser_id(all_user_id=request.all_user_id, nopp=True, dataframe=False)
        if not trainee_profile_data:
            logger.warn(f"No trainee profiles found for user_id: {request.all_user_id}")
            return JSONResponse(status_code=200, content={"message": "No trainee profiles found by the given all_user_id"})


        tinder_user_profile_id = trainee_profile_data.get('id', None)
        if not tinder_user_profile_id:
            logger.error(f"Trainee profile missing 'id' for user_id: {request.all_user_id}")
            return JSONResponse(status_code=500, content={"error": "Trainee profile is invalid."})

        session_chatobserver = ipersona_overall.filter_by_with_user_and_job_id(
            user_profile_id=tinder_user_profile_id,
            job_profile_id=request.job_profile_id,
            nopp=True,
            dataframe=False
        )

        if "all_sessions" not in session_chatobserver or not session_chatobserver["all_sessions"]:
            logger.warn(f"No session data found for user_profile_id: {tinder_user_profile_id}, job_profile_id: {request.job_profile_id}")
            return JSONResponse(status_code=200, content={"message": "No session overall observer data found."})

        logger.info(f"Successfully fetched overall session data for user_profile_id: {tinder_user_profile_id}, job_profile_id: {request.job_profile_id}")
        return session_chatobserver["all_sessions"][0]

    except Exception as e:
        logger.error(f"Unexpected error during session progress calculation: {str(e)}")
        return JSONResponse(status_code=500, content={"error": f"Unexpected error: {str(e)}"})


@routes.post("/calculate_allstat_progress")
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

@routes.post("/engagement_jobs_status")
def calculate_engagement_jobs_status(request: pemodel.AllUserSessionRequestRecieved) -> Dict[str, Any]:
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
        if data:
            return {
                "all_user_id": request.all_user_id,
                "jobs": data, 
                "cursor": cursor,                  
                "status": 200, 
                "message": ""
            }
        else: 
            return {
                "all_user_id": request.all_user_id, 
                "jobs": [],  
                "cursor": [],
                "status": 404, 
                "message": "No data found with the given parameters"
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
        
@routes.post("/admin_overview_status")
async def calculate_admin_overview_status(request: pemodel.AdminDataFiltering) -> Dict[str, Any]:
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
    Dict[str, Any]
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

@routes.post("/admin_allusers_data")
async def calculate_admin_allusers_data(request: pemodel.AdminDataFiltering) -> Dict[str, Any]:
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
    Dict[str, Any]
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

@routes.post("/admin_alljobs_data")
async def calculate_admin_alljobs_data(request: pemodel.AdminDataFiltering) -> Dict[str, Any]:
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

@routes.post("/admin_allusers_performance_data")
async def calculate_admin_allusers_performance_data(request: pemodel.AdminDataFiltering) -> Dict[str, Any]:
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
    Dict[str, Any]
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

@routes.post("/fetch_user_session")
async def fetch_user_session(request: pemodel.UserSessionRequestRecieved) -> Union[List, Dict]:
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
    Union[Dict[str, Any], JSONResponse]
        Session data for the user and job, or an error response
    """  
    run_stage = request.run_stage
 
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
        ipersona_session = IpersonaSessionSchema(run_stage=run_stage)
        user_data = ipersona_session.filter_by_with_user_job_id(
            user_profile_id=tinder_user_profile_id,
            job_profile_id=request.job_profile_id,
            nopp=True, 
            dataframe=False
        )

        if not user_data:
            logger.warn(f"No session data found for user ID: {request.all_user_id} and job ID: {request.job_profile_id}")
            return JSONResponse(
                status_code=404, 
                content={"message": f"No session data found for user ID: {request.all_user_id} and job ID: {request.job_profile_id}"}
            )

        logger.info(f"Session data successfully retrieved for user ID: {request.all_user_id} and job ID: {request.job_profile_id}")
        return user_data

    except Exception as e:
        logger.error(f"Error processing session data for user ID: {request.all_user_id} - {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500, 
            content={"error": f"Error fetching user session: {str(e)}"}
        )
   
@routes.post("/fetch_chat_history")
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
    Union[List[Dict[str, Any]], JSONResponse]
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

@routes.post("/fetch_user_all_observer")
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
    Union[List[Dict[str, Any]], JSONResponse]
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

@routes.post("/fetch_single_session")
async def fetch_single_session(request: pemodel.SessionIdRequestRecieved) -> Union[List, Dict]:
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
        session_fetched = ipersona_session.get_session_by_id(
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
        session_fetched = util.remove_key(session_fetched, 'generated_questions')
        
        return session_fetched

    except Exception as e:
        logger.error(f"Error fetching session data for session ID {request.sessionId}: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500, 
            content={"error": f"Error fetching session: {str(e)}"}
        )