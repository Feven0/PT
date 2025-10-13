from openai import OpenAI
import json, os
import os
import json_repair
import asyncio
from datetime import datetime, timedelta, timezone
from collections import defaultdict
import api.llm.ipersona.ipersona_strapi as strapi
from datetime import datetime
from api.utils.logger import LLPackerLogger
import api.llm.ipersona.ipersona_gpt as gpt
from api.llm.ipersona.ipersona_strapi_schemas import (
    IpersonaSessionTinderUserJobMatchSchema, 
    IpersonaSessionTinderUserReactionSchema, 
    IpersonaSessionSchema, IpersonaTraineeSchema, 
    IpersonaJobSchema, 
    IpersonaSessionOverallObserverSchema, 
    IpersonaSessionMessageSchema, 
    IpersonaSessionObserverSchema, 
    IpersonaAllUserSchema, 
    IpersonaProfileInformationSchema,
    IpersonaTinderTemplateSchema,
    IpersonaChallengeDocumentSchema)

from api.utils.request_manager import JobReactionManager
from api.services.async_task_analyzer import AsyncTaskAnalyzer
import api.modules.reading_fallback_prompts as fallback
from collections import defaultdict
from fastapi.responses import JSONResponse

logger = LLPackerLogger(os.path.basename(__file__))

from api.services.secret import get_auth

OPENAI_API_KEY  = get_auth(ssmkey='OPENAI_PARROT_API_KEY')
openai_client = OpenAI(api_key=OPENAI_API_KEY )

module_dir= os.path.dirname(__file__)
prompts_path = lambda x: os.path.join(module_dir, "prompts", x)
data_path = lambda x: os.path.join(module_dir, "data", x)



# hr_agent = agents()

#-------------------------------------------- create persona --------------------------------------------
def create_persona(job_desc):
    """
    Creates a persona from the provided job description (JD).

    Analyzes the input `job_desc`, identifies relevant classes, and generates a
    formatted persona string based on predefined prompts.

    Parameters:
    ----------
    job_desc : str
        A job description used to create the persona.

    Returns:
    -------
    str
        A formatted string representing the persona, or an error message if 
        an exception occurs during processing.

    """
    try:
        persona_class_prompts = data_path("Geminigenerated.json") 
        classes = json.loads(file_reader(data_path("persona_class.txt")))       
        class_prompts = json.loads(file_reader(persona_class_prompts))       
        x = identify_class(classes, job_desc)
        persona = ""
        for key in x:
            persona += key + ": "
            persona += class_prompts[key][x[key]] + "\n"
        
        return persona

    except Exception as e:
            # logger.error(f"Persona Creation Error: {str(e)}")
            return f'Error: {str(e)}'             


#--------------------------------------------  Generate Interview Questions --------------------------------
async def generate_interview_question(run_stage, data: dict, question_count, template_id, challenge_id, sessionId, template):
    """
    Generates interview questions based on user session data.

    This asynchronous function updates the system message with the user's persona 
    and retrieves a set of interview questions tailored to the session.

    Parameters:
    ----------
    data : dict
        A dictionary containing user session information, including persona and 
        generated questions.

    Returns:
    -------
    dict
        A JSON object containing the generated interview questions, or an error message 
        if an exception occurs during processing.
    """
    try:
        # Retrieve either generated_questions or template_questions
        user_attributes = data['user_session']['attributes']['attributes']
        
        # Choose between generated_questions and template_questions
        collection = user_attributes.get('generated_questions') or user_attributes.get('template_questions') or user_attributes.get('challenge_questions')
        collection = json.loads(collection) if isinstance(collection, str) else collection

        if(challenge_id != 0):
            response = await choose_interview_question_challenge_new_structure(
                run_stage, 
                collection, 
                question_count, 
                data, 
                template_id, 
                challenge_id, 
                sessionId,
                template)
            return response
        
        if not collection:
            raise ValueError("No questions available in generated_questions or template_questions.")
        
        response = await choose_interview_question_new_structure(
            run_stage, 
            collection, 
            question_count, 
            data, 
            template_id, 
            challenge_id, 
            sessionId,
            template)
        
        return response
    
    except Exception as e:
        logger.error(f"Persona Creation Error: {str(e)}")
        return {'error': str(e)}
    
    
#-------------------------------------------- Choose Question from Generated ----------------------------------
async def choose_interview_question_new_structure(
        run_stage, 
        collection: list,  # Changed from dict to list 
        question_count, 
        data: dict, 
        template_id, 
        challenge_id, 
        sessionId,
        template):
    try: 
        # Fetch session chat history
        type = 'job_interview_config'
        ipersona_message = IpersonaSessionMessageSchema(run_stage=run_stage)
        session_chathistory = ipersona_message.filter_by_session_id(
            sessionId=sessionId, 
            nopp=True, 
            dataframe=False,
            sort='asc')
  
        # Determine chat count
        chat = session_chathistory['count']
        global chat_count
        chat_count = 1
        
        if chat != 0:  
            chat = session_chathistory['total']
            assistant_count = sum(1 for entry in chat if entry["user_type"] == "assistant")
            chat_count += assistant_count 
            logger.info(f"Number of assistant entries: {chat_count}")
        else:
            logger.error("Chat is empty.")
        
        # Dynamically calculate section question counts
        question_counts = {section['sectionType']: len(section['questions']) for section in collection}
        total_questions = sum(question_counts.values())
        
        # Create a cumulative section boundaries
        section_boundaries = {}
        current_boundary = 1  # Start from 1
        for section in collection:
            section_type = section['sectionType']
            count = len(section['questions'])
            section_boundaries[section_type] = {
                'start': current_boundary,
                'end': current_boundary + count
            }
            current_boundary += count
        
        # Dynamically determine the current section
        current_section = None
        final_flag = False
        for section in collection:
            section_type = section['sectionType']
            boundaries = section_boundaries[section_type]
            
            # print('telegramapp====================================================')
            # print(chat_count)
            # print(boundaries['end'])
            # print('telegramapp====================================================')
            
            if chat_count < boundaries['end']:
                current_section = section
                break
            else:
                final_flag = True
                # print('final_flag====================================================')
        
        # If a section is found, process the interview question
        if current_section:
            print('whathapp====================================================')
            print(current_section['sectionType'])
            print('whathapp====================================================')
            
            question_type = current_section['sectionType']
            
            # Determine if this is a specific chat count moment (optional)
            count = None
            section_start = section_boundaries[question_type]['start']
            print(f"DEBUG: question_type = '{question_type}', chat_count = {chat_count}, section_start = {section_start}")
            if chat_count == section_start:
                count = chat_count
                print(f"DEBUG: chat_count ({chat_count}) == section_start ({section_start}) - Setting count = {count}")
            else:
                print(f"DEBUG: chat_count ({chat_count}) != section_start ({section_start}) - count remains None")
            
            # Call helper function to fetch or generate question
            response = await helper_func(
                run_stage, 
                total_questions,
                chat_count, 
                count, 
                question_type, 
                current_section['questions'], 
                data, 
                sessionId,
                template_id,
                challenge_id,
                type,
                template)

            return response
        
        # If no section is found (all questions exhausted)
        if final_flag:
            interview_question_json = None
            realtime_evaluation = None
            status = None
            
            # Fetch last assistant response
            last_assistant_response = fetch_the_last_question(run_stage, data, sessionId) 

            # Prepare closing evaluation prompt
            # ipersona_metric = IpersonaSmgCretrionMetricSchema()
            # data_content = ipersona_metric.get_smgCriterionMetric_by_id(metricId=167, nopp=True, dataframe=False)
            # data_content = data_content.get('attributes', {}).get('content', {})
            # tag = 'parrot_closing_question_realtime_evaluation'
            # content = fetch_config_template(type, tag)
            # data_content = content.get('content', '')
            # closing_content = data_content.replace("{closing_question}", str(last_assistant_response))
            # closing_content = data_content.replace("{candidate_response}" , str(data['response']))
            candidate_response = data['response']

            if data.get("template_id") and data.get("challenge_id"):
                print("whyare you doing thesesss====================================================")
                closing_content = realtime_response_evaluation(run_stage, data, sessionId, type)
            else: 
                print("whyare you doing thes NOTTTTe====================================================")
                closing_content = read_prompt_closing_question_realtime_evaluation(
                    type, 
                    last_assistant_response, 
                    candidate_response)

            # Get realtime evaluation
            realtime_evaluation_response = gpt.openai_gpt_assistant_without_streaming(closing_content)

            realtime_evaluation_response = extract_json(realtime_evaluation_response, quite=False) 
            realtime_evaluation = "null" if realtime_evaluation_response is None else realtime_evaluation_response.get("realtime_evaluation")

            logger.info(f"Realtime evaluation is: {realtime_evaluation}")
            if realtime_evaluation != "null":
                status = "final"
                final = 'true'
                strapi.step3_insert_message(run_stage, realtime_evaluation, final, sessionId)
                
               
                # print('my daaaaaaaaaaaaaaaaaaaaaaaaa=====================================')
                # print(realtime_evaluation)
            
            rstage = run_stage
            
            status = "Completed"
            
            # Run overall calculation in background to avoid blocking socket emission
            logger.info(f"🔍 [DEBUG] === STARTING BACKGROUND OVERALL CALCULATION ===")
            logger.info(f"🔍 [DEBUG] SessionID: {sessionId}, Status: {status}, Type: {type}")
            logger.info(f"🔍 [DEBUG] Run stage: {rstage}")
            
            asyncio.create_task(overall_interview_evaluations(rstage, data, status, sessionId, type))
            logger.info("✅ Started overall calculation in background - socket emission will not be blocked")            
                
            response = {
                "interview": interview_question_json,
                "status": status,
                "realtime": realtime_evaluation
            }

            return response

    except Exception as e:
        logger.error(f"Choosing question process failed: {str(e)}")
        return {'error': str(e)}
    
async def choose_interview_question_challenge_new_structure(
    run_stage, 
    collection: list, 
    question_count, 
    data: dict, 
    template_id, 
    challenge_id, 
    sessionId,
    template):
    try: 
        # Fetch session chat history
        type = 'challenge_interview_config'
        ipersona_message = IpersonaSessionMessageSchema(run_stage=run_stage)
        session_chathistory = ipersona_message.filter_by_session_id(
            sessionId=sessionId, 
            nopp=True, 
            dataframe=False,
            sort='asc')
  
        # Determine chat count
        chat = session_chathistory['count']
        global chat_count
        chat_count = 1
        
        if chat != 0:  
            chat = session_chathistory['total']
            assistant_count = sum(1 for entry in chat if entry["user_type"] == "assistant")
            chat_count += assistant_count 
            logger.info(f"Number of assistant entries: {chat_count}")
        else:
            logger.info("Chat is empty.")


        # Dynamically calculate section question counts
        question_counts = {section['sectionType']: len(section['questions']) for section in collection}
        total_questions = sum(question_counts.values())
        # print("question_counts is here ==========================================")
        # print(question_counts)
        # print(total_questions)
        # print("question_counts is here ==========================================")
        # Create a cumulative section boundaries
        section_boundaries = {}
        current_boundary = 1  # Start from 1
        for section in collection:
            section_type = section['sectionType']
            count = len(section['questions'])
            section_boundaries[section_type] = {
                'start': current_boundary,
                'end': current_boundary + count
            }
            current_boundary += count
        
        # Dynamically determine the current section
        current_section = None
        final_flag = False
        # for section in collection:
        #     section_type = section['sectionType']
        #     boundaries = section_boundaries[section_type]
        #     if chat_count < boundaries['end']:
        #         current_section = section
        #         break
        #     else:
        #         final_flag = True
        
        for section in collection:
            section_type = section['sectionType']
            boundaries = section_boundaries[section_type]
            
            # print('telegramapp====================================================')
            # print(chat_count)
            # print(boundaries['end'])
            # print('telegramapp====================================================')
            
            if chat_count < boundaries['end']:
                current_section = section
                break
            else:
                final_flag = True
                # print('final_flag====================================================')
        
        
        # If a section is found, process the interview question
        if current_section:
            question_type = current_section['sectionType']
            
            # Determine if this is a specific chat count moment (optional)
            count = None
            section_start = section_boundaries[question_type]['start']
            print(f"DEBUG: question_type = '{question_type}', chat_count = {chat_count}, section_start = {section_start}")
            if chat_count == section_start:
                count = chat_count
                print(f"DEBUG: chat_count ({chat_count}) == section_start ({section_start}) - Setting count = {count}")
            else:
                print(f"DEBUG: chat_count ({chat_count}) != section_start ({section_start}) - count remains None")
            # print("CURRENT SECTION IS HERE ==========================================")
            # print(current_section)
            # print("CURRENT SECTION IS HERE ==========================================")

            # print("USER RESONPSEN=====================================================")
            # print(data['response'])
            # print("USER RESONPSEN=====================================================")
            # Call helper function to fetch or generate question
            response = await helper_func(
                run_stage, 
                total_questions,
                chat_count, 
                count, 
                question_type, 
                current_section['questions'], 
                data, 
                sessionId,
                template_id,
                challenge_id,
                type,
                template)

            return response
        
        # If no section is found (all questions exhausted)
        if final_flag:
            interview_question_json = None
            realtime_evaluation = None
            status = None
            
            # Realtime evaluation response
            realtime_evaluation_response_json = realtime_response_evaluation(run_stage, data, sessionId, type)
            realtime_evaluation = "null" if realtime_evaluation_response_json is None else realtime_evaluation_response_json.get("realtime_evaluation")
           
            logger.info(f"Realtime evaluation i______s: {realtime_evaluation}")
            if realtime_evaluation != "null":
                status = "final"
                final = 'true'
                strapi.step3_insert_message(run_stage, realtime_evaluation, final, sessionId)

            rstage = run_stage
            status = "Completed"
            
            # Run overall calculation in background to avoid blocking socket emission
            logger.info(f"🔍 [DEBUG] === STARTING BACKGROUND OVERALL CALCULATION ===")
            logger.info(f"🔍 [DEBUG] SessionID: {sessionId}, Status: {status}, Type: {type}")
            logger.info(f"🔍 [DEBUG] Run stage: {rstage}")
            
            asyncio.create_task(overall_interview_evaluations(rstage, data, status, sessionId, type))
            logger.info("✅ Started overall calculation in background - socket emission will not be blocked")            
                
            response = {
                "interview": interview_question_json,
                "status": status,
                "realtime": realtime_evaluation
            }

            return response

    except Exception as e:
        logger.error(f"Choosing question process failed: {str(e)}")
        return {'error': str(e)}
    
#----------------------------------------- Helper Functions for Choosing Question ---------------------------------
async def helper_func(
    run_stage, 
    question_count,
    chat_count, 
    count, 
    question_type: str, 
    section: list, 
    data: dict, 
    sessionId,
    template_id,
    challenge_id,
    type,
    template):
    """
    Processes interview questions and evaluations based on candidate responses.

    This asynchronous function evaluates candidate responses and fetches 
    appropriate interview questions from the specified section. It also handles 
    real-time and overall evaluations based on the current question counter.

    Parameters:
    ----------
    count : int
        The current question count, indicating which question is being processed.

    question_type : str
        The type of question being asked (e.g., Background, Technical).

    section : list
        A list of questions from which to fetch the current interview question.

    data : dict
        A dictionary containing session information, including candidate responses 
        and the current question counter.

    Returns:
    -------
    dict
        A JSON object containing the interview question, real-time evaluations, 
        overall evaluations, and metrics. If an error occurs, it returns an error 
        message instead.
    """
    try: 
        interview_question_json = None
        realtime_evaluation = None
        status = None

        if chat_count < question_count + 2:
            if data['response']:
                if count is not None:
                    interview_question_json = await fetch_interview_question(section, question_type, data, question_count, type, template_id, sessionId, run_stage) 
                  
                    # await append_asked_question_number_from_sections(
                    #     interview_question_json, 
                    #     section, 
                    #     sessionId,
                    #     run_stage)
                else:
                    if not template:
                        response = await check_if_followup(data['response'], type)
                        if not response:
                            interview_question_json = await fetch_interview_question(section, question_type, data, question_count, type, template_id, sessionId, run_stage)
                        else:
                            interview_question_json = await generate_followup(data, type)
                    else:
                        interview_question_json = await fetch_interview_question(section, question_type, data, question_count, type, template_id, sessionId, run_stage)
                        # await append_asked_question_number_from_sections(
                        #     interview_question_json, 
                        #     section, 
                        #     sessionId,
                        #     run_stage)

                        
            else:
                interview_question_json = await fetch_interview_question(section, question_type, data, question_count, type, template_id, sessionId, run_stage) 
                # await append_asked_question_number_from_sections(
                #         interview_question_json, 
                #         section, 
                #         sessionId,
                #         run_stage)
   
        else:  
            realtime_evaluation_response_json = realtime_response_evaluation(run_stage, data, sessionId, type)
            realtime_evaluation = "null" if realtime_evaluation_response_json is None else realtime_evaluation_response_json.get("realtime_evaluation")
            logger.info(f"Realtime evaluation i______s: {realtime_evaluation}")
            if realtime_evaluation != "null":
                status = "final"
                final = 'true'
                strapi.step3_insert_message(run_stage, realtime_evaluation, final, sessionId)
            rstage = run_stage
            status = "Completed"
   
            # Run overall calculation in background to avoid blocking socket emission
            logger.info(f"🔍 [DEBUG] === STARTING BACKGROUND OVERALL CALCULATION ===")
            logger.info(f"🔍 [DEBUG] SessionID: {sessionId}, Status: {status}, Type: {type}")
            logger.info(f"🔍 [DEBUG] Run stage: {rstage}")
            
            asyncio.create_task(overall_interview_evaluations(rstage, data, status, sessionId, type))
            logger.info("✅ Started overall calculation in background - socket emission will not be blocked")            
                
        response = {
            "interview": interview_question_json,
            "status": status,
            "realtime": realtime_evaluation
        }
        
        return response
    
    except Exception as e:
        logger.error(f"Choosing question helper process failed: {str(e)}")
        return {'error': str(e)}
   
#----------------------------------------- picking the right Question ----------------------------------------- 
async def fetch_interview_question(
    section: list, 
    question_type: str, 
    data: dict, 
    question_count,
    type, 
    template_id,
    sessionId,
    run_stage):
    """
    Fetches an interview question based on the provided section and candidate response.

    This asynchronous function generates an interview question by replacing placeholders 
    in a prompt template with the specified section of questions and the candidate's response. 
    It then calls the HR agent to generate the question.

    Parameters:
    ----------
    section : list
        A list of questions relevant to the specific interview section.

    data : dict
        A dictionary containing session information, including the candidate's response.

    Returns:
    -------
    dict
        A JSON object containing the generated interview question, or an error message 
        if an exception occurs during processing.
    """
    try:
        if chat_count == question_count + 2:
            message = read_prompt_interview_closing(type)
        else:
            if template_id:
                message = file_reader(prompts_path('ipersona/template_question_picking.txt'))
            else:
                message = read_prompt_pick_interview_question(type)
            
        # Ensure asked_question_numbers is defined to avoid NameError
        ipersona_user = IpersonaSessionSchema(run_stage=run_stage)
        session_fetched = ipersona_user.get_session_by_id(
            sessionId=sessionId, 
            nopp=True, 
            dataframe=False
        )

        if not session_fetched:
            logger.error(f"Session not found: {sessionId}")
            print(f"DEBUG: Session fetch failed for session_id: {sessionId}")
            return []
            
        print(f"DEBUG: Session fetched successfully: {sessionId}")
        
        # Get current attributes - session_fetched['attributes']['attributes'] is the inner attributes
        session_attributes = session_fetched.get('attributes', {})
        current_attrs = session_attributes.get('attributes', {})
        asked_numbers = current_attrs.get('asked_question_numbers', [])
        message = message.replace("{collection}", str(section))
        message = message.replace("{type}", str(question_type))
        message = message.replace("{candidate_response}", data['response'])
        message = message.replace("{question_numbers}", str(asked_numbers))
        msg = message

        
        persona = data['user_session']['attributes']['attributes'].get('persona', '')
        content = persona + msg
        
        # Call both LLM functions directly (they're not async)
        response = gpt.openai_gpt_assistant_with_streaming(content)
        
  
        if template_id != 0 or template_id is not None:
            # Use asyncio.create_task for background processing in regular functions
            import asyncio
            asyncio.create_task(process_question_generation_background(
                content,
                asked_numbers,
                section,
                sessionId,
                run_stage,
                current_attrs
            ))
        return response
    except Exception as e:
        logger.error(f"Choosing the right question process failed: {str(e)}")
        return {'error': str(e)}

async def process_question_generation_background(
    content: str,
    asked_numbers: list,
    section: list,
    sessionId: str,
    run_stage: str,
    current_attrs: dict
):
    """
    Background task to process question generation without blocking the main response
    """
    try:
        picked_question_text = gpt.openai_gpt_assistant_without_streaming(content)
        
        await append_asked_question_number_from_sections(
            asked_numbers,
            picked_question_text, 
            section, 
            sessionId,
            run_stage,
            current_attrs
        )
        logger.info("✅ [BACKGROUND] Question generation completed successfully")
    except Exception as e:
        logger.error(f"❌ [BACKGROUND] Question generation failed: {str(e)}")

async def calculate_template_time_limit_sync(
    response: str,
    section: list,
    sessionId: str,
    run_stage: str,
    sio,
    sid: str,
    chat: bool
):
    """
    Synchronous calculation of time limit for template questions
    Returns the timelimit dict for immediate use in database save
    """
    try:
        logger.info("🔄 [SYNC] Starting synchronous time limit calculation...")
        print(response)
        # Find the specific question in the section to get its time limit
        time_limit = None
        
        # Normalize the response text for matching
        def normalize(text: str) -> str:
            if text is None:
                return ""
            # Remove trailing question marks and normalize whitespace
            normalized = " ".join(str(text).strip().split()).lower()
            # Remove trailing question mark for better matching
            if normalized.endswith('?'):
                normalized = normalized[:-1]
            return normalized
        
        response_norm = normalize(response)
        logger.info(f"🔄 [SYNC] Normalized response: '{response_norm}'")
        
        # Search through sections to find matching question
        logger.info(f"🔄 [SYNC] Searching through {len(section)} section items...")
        for i, section_item in enumerate(section):
            logger.info(f"🔄 [SYNC] Section item {i}: {type(section_item)}")
            if isinstance(section_item, dict) and 'questions' in section_item:
                questions = section_item.get('questions', [])
                logger.info(f"🔄 [SYNC] Found {len(questions)} questions in section {i}")
                for j, question in enumerate(questions):
                    if isinstance(question, dict):
                        question_text = question.get('question', '')
                        question_norm = normalize(question_text)
                        
                        # Check if this question matches the response
                        if question_norm == response_norm or response_norm in question_norm:
                            time_limit = question.get('time_limit')
                            if time_limit:
                                logger.info(f"[SYNC] Found matching question with time limit: {time_limit}")
                                break
                if time_limit:
                    break
            else:
                logger.info(f"🔄 [SYNC] Section item {i} is not a dict with questions or has no questions key")
        
        # If no specific time limit found, use default value of 3 minutes
        if not time_limit or time_limit == '':
            logger.info("🔄 [SYNC] No specific time limit found, using default 3 minutes")
            time_limit = "3"
        
        # Convert time limit to MM:SS format
        def format_time_limit(time_str):
            """Convert time limit to MM:SS format"""
            try:
                # Handle different input formats
                if time_str in ['null', None, '']:
                    return "03:00"  # Default 3 minutes
                
                # If it's already a number (string), treat as minutes
                if time_str.isdigit():
                    minutes = int(time_str)
                    return f"{minutes:02d}:00"
                
                # If it contains 'min' or 'mins', extract the number
                if 'min' in str(time_str).lower():
                    import re
                    match = re.search(r'(\d+)', str(time_str))
                    if match:
                        minutes = int(match.group(1))
                        return f"{minutes:02d}:00"
                
                # If it's already in MM:SS format, return as is
                if ':' in str(time_str):
                    return str(time_str)
                
                # Default fallback
                return "03:00"
            except Exception as e:
                logger.error(f"❌ [SYNC] Error formatting time limit '{time_str}': {e}")
                return "03:00"  # Default fallback
        
        formatted_time_limit = format_time_limit(time_limit)
        logger.info(f"🔄 [SYNC] Original time limit: '{time_limit}' -> Formatted: '{formatted_time_limit}'")
        
        
        # Emit the time limit to the socket
        message = [{
            "content": {
                "time_limit": formatted_time_limit,
            }
        }]
        
        logger.info(f"[SYNC] Emitting formatted time limit {formatted_time_limit} to SID {sid}")
        
        if chat:
            await sio.emit("time_limit", message, room=sid)
        else:
            await sio.emit("audio_time_limit", message, room=sid)

        logger.info(f"[SYNC] Time limit emission completed successfully for SID {sid}")
        
        # Return the timelimit dict in the expected format
        return {"time_limit": formatted_time_limit}
        
    except Exception as e:
        logger.error(f"Synchronous time limit calculation failed: {str(e)}")
        return {"time_limit": "03:00"}  # Default fallback

async def append_asked_question_number_from_sections(
    asked_numbers: list,
    picked_question_text: str,
    sections: list,
    session_id: str,
    run_stage: str,
    current_attrs: dict
):
    """
    Find the question_number of the picked question by matching against the nested
    sections structure, then append it to session's asked_question_numbers.

    Returns: updated_asked_list: list
    """
    try:
        # Ensure it's a list of strings
        asked_numbers = [str(x) for x in asked_numbers] if isinstance(asked_numbers, list) else []
        logger.info(f"DEBUG: Normalized asked_numbers = {asked_numbers}")
        
        def normalize(text: str) -> str:
            if text is None:
                return ""
            t = " ".join(str(text).strip().split()).lower()
            # Ignore a trailing '?' difference for matching
            return t[:-1] if t.endswith("?") else t

        picked_norm = normalize(picked_question_text)
        logger.info(f"DEBUG: Normalized picked question = '{picked_norm}'")

        # Flatten questions from sections
        flat_questions = []
        logger.info(f"DEBUG: Processing sections for flattening...")
        
        # Check if sections is a flat list of questions or nested structure
        if sections and isinstance(sections, list):
            # Check if first item has 'questions' key (nested structure)
            if sections[0] and isinstance(sections[0], dict) and 'questions' in sections[0]:
                logger.info(f"DEBUG: Detected nested structure with 'questions' key")
                # Nested structure: [{"questions": [...]}]
                for i, section in enumerate(sections):
                    logger.info(f"DEBUG: Section {i}: {type(section)} - {section}")
                    if isinstance(section, dict):
                        questions = section.get("questions", [])
                        logger.info(f"DEBUG: Section {i} has {len(questions)} questions")
                        for j, q in enumerate(questions or []):
                            logger.info(f"DEBUG: Question {j}: {q}")
                            if isinstance(q, dict):
                                flat_questions.append(q)
                                logger.info(f"DEBUG: Added question {j} to flat_questions")
            else:
                logger.info(f"DEBUG: Detected flat structure - each item is a question")
                # Flat structure: [{"question": "...", "question_number": 1}, ...]
                for i, question in enumerate(sections):
                    logger.info(f"DEBUG: Question {i}: {type(question)} - {question}")
                    if isinstance(question, dict):
                        flat_questions.append(question)
                        logger.info(f"DEBUG: Added question {i} to flat_questions")
        
        logger.info(f"DEBUG: Total flattened questions: {len(flat_questions)}")
        for i, q in enumerate(flat_questions):
            logger.info(f"DEBUG: Flat question {i}: question_number={q.get('question_number')}, question='{q.get('question', '')[:50]}...'")

        # Collect exact normalized matches (prefer exact over fuzzy)
        matches = []
        logger.info(f"DEBUG: Starting exact match comparison...")
        for i, q in enumerate(flat_questions):
            q_text = q.get("question")
            qn = q.get("question_number")
            qn_norm = normalize(q_text)
            is_exact_match = qn_norm == picked_norm
            logger.info(f"DEBUG: Question {i} (qn={qn}): '{qn_norm}' == '{picked_norm}' ? {is_exact_match}")
            if is_exact_match:
                if qn is not None:
                    try:
                        matches.append(int(qn))
                        logger.info(f"DEBUG: EXACT MATCH FOUND! Added question_number {qn} to matches")
                    except Exception as e:
                        logger.info(f"DEBUG: Error converting question_number {qn} to int: {e}")
                        pass
                else:
                    logger.info(f"DEBUG: Question {i} has no question_number, skipping")

        logger.info(f"DEBUG: Exact matches found: {matches}")

        # Fallback: containment-based match if exact failed
        if not matches:
            logger.info(f"DEBUG: No exact matches found, trying containment matching...")
            for i, q in enumerate(flat_questions):
                q_text = q.get("question")
                qn = q.get("question_number")
                if qn is None:
                    logger.info(f"DEBUG: Question {i} has no question_number, skipping containment check")
                    continue
                qn_norm = normalize(q_text)
                is_containment_match = picked_norm and (qn_norm.startswith(picked_norm) or picked_norm.startswith(qn_norm) or picked_norm in qn_norm)
                logger.info(f"DEBUG: Question {i} (qn={qn}): containment check '{qn_norm}' vs '{picked_norm}' ? {is_containment_match}")
                if is_containment_match:
                    try:
                        matches.append(int(qn))
                        logger.info(f"DEBUG: CONTAINMENT MATCH FOUND! Added question_number {qn} to matches")
                    except Exception as e:
                        logger.info(f"DEBUG: Error converting question_number {qn} to int: {e}")
                        pass
            logger.info(f"DEBUG: Containment matches found: {matches}")
        else:
            logger.info(f"DEBUG: Skipping containment matching since exact matches were found")

        matched_number = None
        if matches:
            # If duplicates exist, choose the lowest number deterministically
            matched_number = str(min(matches))
            logger.info(f"DEBUG: Selected matched_number = '{matched_number}' from matches {matches}")
        else:
            logger.info(f"DEBUG: No matches found, matched_number = None")

        # Append to asked list if found and update session
        if matched_number is not None and matched_number not in asked_numbers:
            logger.info(f"DEBUG: matched_number '{matched_number}' is not in asked_numbers {asked_numbers}, proceeding with update")
            asked_numbers.append(matched_number)
            logger.info(f"DEBUG: After append, asked_numbers = {asked_numbers}")
            
            # Update session attributes - current_attrs is the inner attributes object
            current_attrs['asked_question_numbers'] = asked_numbers
            logger.info(f"DEBUG: Updated current_attrs = {current_attrs}")
            
            # Update the session in database
            update_data = {
                "i_persona_session_id": session_id,
                "attributes": current_attrs
            }
            logger.info(f"DEBUG: Update data structure = {update_data}")
            
            ipersona_session = IpersonaSessionSchema(run_stage=run_stage)
            logger.info(f"DEBUG: Calling update_session with params...")
            updated_session = ipersona_session.update_session(
                params=update_data, 
                nopp=True, 
                dataframe=False, 
                return_object=True
            )
            
        else:
            if matched_number is None:
                logger.info(f"DEBUG: No matched_number found, skipping update")
            elif matched_number in asked_numbers:
                logger.info(f"DEBUG: matched_number '{matched_number}' already in asked_numbers {asked_numbers}, skipping update")
            else:
                logger.info(f"DEBUG: Unexpected condition, skipping update")

        logger.info(f"DEBUG: Final asked_numbers to return: {asked_numbers}")
        logger.info("=== DEBUG: Ending append_asked_question_number_from_sections ===")
        return asked_numbers
        
    except Exception as e:
        logger.error(f"Error in append_asked_question_number_from_sections: {str(e)}")
        return []

#-------------------------------- Interview question time limit generation ---------------------------- 
def interview_question_time_limit(question: str):
    try:
        type = 'job_interview_config'
        msg = read_prompt_time_limit_generator(type, question)

        response = gpt.openai_gpt_assistant_without_streaming(msg)
        response = extract_json(response, quite=False)
        return response
    except Exception as e:
        logger.error(f"generating time limit process failed: {str(e)}")
        return {'error': str(e)}
    
#---------------------------------------- Follow up Question Checker -------------------------------
async def check_if_followup(candidate_response: str, type) -> bool:
    """
    Checks if a follow-up question is needed based on the candidate's response.

    This asynchronous function generates a prompt to determine if a follow-up 
    question should be asked, using the provided candidate response. It then 
    calls the HR agent to assess the need for a follow-up.

    Parameters:
    ----------
    candidate_response : str
        The candidate's response to the interview question.

    Returns:
    -------
    dict
        A JSON object indicating whether a follow-up question is needed, 
        or an error message if an exception occurs during processing.
    """
    try:
        msg = read_prompt_followup_checker(type, candidate_response)

        response = gpt.openai_gpt_assistant_without_streaming(msg)
        response_json = extract_json(response, quite=False)

        return response_json["follow-up"]
    
    except Exception as e:
        logger.error(f"Checking follow up process failed: {str(e)}")
        return {'error': str(e)}
     
#-------------------------------------------- Generate Follow up Question -----------------------------------
async def generate_followup(data, type) -> dict:
    """
    Generates a follow-up question based on the candidate's response.

    This asynchronous function creates a prompt for a follow-up question using 
    the provided candidate response. It then calls the HR agent to generate the 
    appropriate follow-up question.

    Parameters:
    ----------
    candidate_response : str
        The candidate's previous response to the interview question.

    Returns:
    -------
    dict
        A JSON object containing the generated follow-up question, 
        with an end message prompting the candidate for a detailed response, 
        or an error message if an exception occurs during processing.
    """
    try:
        candidate_response = data['response']
        msg = read_prompt_followup_question_generator(type, candidate_response)

        persona = data['user_session']['attributes']['attributes'].get('persona', '')
        content = persona + msg
        response = gpt.openai_gpt_assistant_with_streaming(content)

        return response
    
    except Exception as e:
        logger.error(f"Generating follow up failed: {str(e)}")
        return {'error': str(e)}

#---------------------------------------- Realtime Chat Evaluation Function -------------------------------
def fetch_the_last_question(run_stage, data: dict, sessionId) -> dict:
    try:
        ipersona_message = IpersonaSessionMessageSchema(run_stage=run_stage)
        session_chathistory = ipersona_message.filter_by_session_id(
            sessionId=sessionId, 
            nopp=True, 
            dataframe=False,
            sort='asc')
        
        history = session_chathistory['total']
        
        last_assistant_response = None
        for entry in reversed(history):
            message = entry            
            if message["user_type"] == "assistant":
                last_assistant_response = message["content"].get("full_response")  
                break  

        if last_assistant_response:
            logger.info("Last assistant response For Realtime Evaluation")
        else:
            logger.warn("No assistant response found in the chat history.")

        return last_assistant_response   

    except Exception as e:
        logger.error(f"Real time evaluation process failed: {str(e)}")
        return {'error': str(e)} 
    
def realtime_response_evaluation(run_stage, data: dict, sessionId, type) -> dict:
    """
    Evaluates the candidate's response in real-time based on the previous question.

    This asynchronous function generates an evaluation prompt using the previous 
    question and candidate response. It then calls the HR agent to assess the 
    candidate's response in real-time.

    Parameters:
    ----------
    data : dict
        A dictionary containing the previous question and the candidate's response.

    Returns:
    -------
    dict
        A JSON object containing the results of the real-time evaluation, 
        or an error message if an exception occurs during processing.
    """
    try:
        
        last_assistant_response = fetch_the_last_question(run_stage, data, sessionId)  
        logger.info(f"Last assistant response: {last_assistant_response}")
        msg = read_prompt_realtime_evaluation(type, data, last_assistant_response)
   
        persona = data['user_session']['attributes']['attributes'].get('persona', '')
        content = persona + msg
        realtime_evaluation_response = gpt.openai_gpt_assistant_without_streaming(content)
        realtime_evaluation_response = extract_json(realtime_evaluation_response, quite=False)            
        return realtime_evaluation_response
    
    except Exception as e:
        logger.error(f"Real time evaluation process failed: {str(e)}")
        return {'error': str(e)} 
    
#---------------------------------------- Overall EXTERNAL AUDIO Evaluation -------------------------------
def process_audio_and_save_external(
        audio_processing_status,
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
        external_audio_prompt = file_reader(prompt_path('external_audio_analysis.txt'))
        realtime_prompt = file_reader(prompt_path('realtime_evaluation.txt'))
        external_aud_prompt = external_audio_prompt.replace("{transcription}", str(transcript.text)).replace("{realtime}", str(realtime_prompt))
        # external_aud_prompt = "Hello"
        data = gpt.openai_gpt_assistant_without_streaming(external_aud_prompt)
        response = extract_json(data, quite=False)
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
        upload_metadata = None
        mode = None
        saved_session = create_session(
            run_stage,
            mode,
            template,
            external,
            challenge,
            all_user_id,
            tinder_user_profile_id,
            job_profile_id,
            template_id,
            challenge_id,
            message,
            upload_metadata)

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
                        overall_interview_evaluations_external(
                            run_stage, 
                            transcribe_chat, 
                            status, 
                            sessionId, 
                            all_user_id, 
                            tinder_user_profile_id, 
                            job_profile_id,
                            challenge_id,
                            0,  # template_id (not available in this context)
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
            import threading
            t = threading.Thread(target=run_overall)
            t.start()
        else:
            audio_processing_status[job_profile_id] = {"status": "failed", "message": "Chat Not Saved"}
    except Exception as e:
        logger.error(f"Error in background audio processing: {str(e)}", exc_info=True)
        audio_processing_status[job_profile_id] = {"status": "failed", "message": str(e)}

#----------------------------------------- Overall Interview Evaluation -------------------------------
async def overall_interview_evaluations(run_stage, data: dict, status, sessionId, type) -> dict:
    """
    Evaluates the overall performance of a candidate in an interview.

    This asynchronous function assesses the candidate's overall performance 
    using their interview history and real-time evaluation results. It generates 
    overall evaluation metrics and saves the final chat history to the database.

    Parameters:
    ----------
    data : dict
        A dictionary containing session information, including the candidate's 
        responses and interview history.

    realtime_evaluation_response_json : dict
        A JSON object containing the results of the real-time evaluation.

    Returns:
    -------
    dict
        A JSON object containing the overall interview metrics and evaluation response, 
        or an error message if an exception occurs during processing.
    """
    try:
        # 🔍 DEBUG: Overall calculation function started
        import time
        start_time = time.time()
        logger.info(f"🔍 [DEBUG] === overall_interview_evaluations FUNCTION STARTED ===")
        logger.info(f"🔍 [DEBUG] SessionID: {sessionId}, Status: {status}, Type: {type}")
        logger.info(f"🔍 [DEBUG] Run stage: {run_stage}")
        
        ipersona_message = IpersonaSessionMessageSchema(run_stage=run_stage)
        all_chat_history = ipersona_message.filter_by_session_id(
            sessionId=sessionId, 
            nopp=True, 
            dataframe=False,
            sort='asc')
        history = all_chat_history['total']
        history_str = '\n'.join(str(item) for item in history)

        # ipersona_metric = IpersonaSmgCretrionMetricSchema()
        # data_content = ipersona_metric.get_smgCriterionMetric_by_id(metricId=163, nopp=True, dataframe=False)
        # message = data_content.get('attributes', {}).get('content', {})
        
        # tag = 'parrot_overall_evaluation'
        # content = fetch_config_template(type, tag)
        # message = content.get('content', '')
        # message = message.replace("{history}", history_str)  
        # overall_evaluation_msg = message
      
        overall_evaluation_msg = read_prompt_overall_evaluation(type, history_str)
        

        # data_content_metrics = ipersona_metric.get_smgCriterionMetric_by_id(metricId=173, nopp=True, dataframe=False)
        # message = data_content_metrics.get('attributes', {}).get('content', {})
        
        # tag = 'parrot_interview_evaluation_metrics'
        # content = fetch_config_template(type, tag)
        # message = content.get('content', '')
        # message = message.replace("{history}", history_str)  
        # overall_metrics_msg = message
        overall_metrics_msg = read_prompt_interview_evaluation_metrics(type, history_str)
        
        
        # persona = data['user_session']['attributes']['attributes'].get('persona', '')
        # content = persona + overall_evaluation_msg
        content = overall_evaluation_msg
        overall_evaluation_response = gpt.openai_gpt_assistant_without_streaming(content)
       
        overall_evaluation_response_json = extract_json(overall_evaluation_response, quite=False)
   
        # persona = data['user_session']['attributes']['attributes'].get('persona', '')
        # content = persona + overall_metrics_msg
        content = overall_metrics_msg

        overall_interview_metrics_response = gpt.openai_gpt_assistant_without_streaming(content)
        overall_interview_metrics_json = extract_json(overall_interview_metrics_response, quite=False)
           
        time_array = calculate_time(history)
        relevancy = filter_the_relevancies(history)
        percent_term = percentage_term(relevancy["average"])
        
        overall_evaluation_response_json["overall_evaluation"]["message"] = percent_term["term"]
        overall_interview_metrics_json["evaluation_metrics"]["message"] = percent_term["term"]
        overall_interview_metrics_json["evaluation_metrics"]["time_management"] = time_array
        overall_interview_metrics_json["evaluation_metrics"]["relevancy"] = relevancy["relevancy"]
        overall_interview_metrics_json["evaluation_metrics"]["overall_performance_score"] = relevancy["average"]
        overall_interview_metrics_json["evaluation_metrics"]["rating"] = percent_term["rating"]
        overall_interview_metrics_json["evaluation_metrics"]["competency"] = overall_evaluation_response_json["overall_evaluation"]["competency"]
        
        ############################## Save final chat history to strapi #########################################        
        overall_interview_metrics_json = overall_interview_metrics_json["evaluation_metrics"]
        overall_evaluation_response_json = overall_evaluation_response_json["overall_evaluation"]
        overall_json = {
                "attributes": {
                    "interview_evaluation": overall_evaluation_response_json,
                    "interview_evaluation_metrics": overall_interview_metrics_json,
                },
                "metadata": None,
                "i_persona_session": sessionId,
                "status": status            
            }

        ipersona_observer = IpersonaSessionObserverSchema(run_stage=run_stage)
        save_observer = ipersona_observer.save_observer(params=overall_json, nopp=True, dataframe=False)
 
        ipersona_session = IpersonaSessionSchema(run_stage=run_stage)
        if save_observer:
            logger.info("session observer to database")

        session_data = {
            "i_persona_session_id": sessionId, 
            "status": status,
        }
        updated_session = ipersona_session.update_session(
            params=session_data, 
            nopp=True, 
            dataframe=False, 
            return_object=True)
     
        if updated_session:
            logger.info("session status updated to closed")
            
    
        # ipersona_user = IpersonaTraineeSchema(run_stage=run_stage)

        # trainee_profile_data = ipersona_user.filter_by_alluser_id(
        #     all_user_id=data['all_user_id'], 
        #     nopp=True, 
        #     dataframe=False
        #     )
        
        # if not trainee_profile_data:
        #     logger.warn("No trainee user profiles found.")
        #     return []
        
        ipersona_session = IpersonaSessionSchema(run_stage=run_stage) 

   
        session = ipersona_session.get_session_by_id(
            sessionId=sessionId, 
            nopp=True, 
            dataframe=False)

        session_chatobserver = extract_observers_metrics(session)

        if status == 'Completed':  
            await calculate_overall_progress(
                run_stage, 
                data, 
                session_chatobserver) 
            
        response = {
            "overall_interview_metrics": overall_interview_metrics_json,
            "overall_evaluation_response": overall_evaluation_response_json
        }
        
        # 🔍 DEBUG: Overall calculation function completed
        end_time = time.time()
        duration = end_time - start_time
        logger.info(f"🔍 [DEBUG] === overall_interview_evaluations FUNCTION COMPLETED ===")
        logger.info(f"🔍 [DEBUG] SessionID: {sessionId}")
        logger.info(f"🔍 [DEBUG] Duration: {duration:.2f} seconds")
        logger.info("✅ Calculate the overall and save to database done.")
        
        return response
        
    except Exception as e:
        logger.error(f"Overall evaluation process failed: {str(e)}")
        return {'error': str(e)}    
                  
async def overall_interview_evaluations_external(
        run_stage, 
        data: dict, 
        status, 
        sessionId, 
        all_user_id, 
        tinder_user_profile_id, 
        job_profile_id,
        type) -> dict:
    """
    Evaluates the overall performance of a candidate in an interview.

    This asynchronous function assesses the candidate's overall performance 
    using their interview history and real-time evaluation results. It generates 
    overall evaluation metrics and saves the final chat history to the database.

    Parameters:
    ----------
    data : dict
        A dictionary containing session information, including the candidate's 
        responses and interview history.

    realtime_evaluation_response_json : dict
        A JSON object containing the results of the real-time evaluation.

    Returns:
    -------
    dict
        A JSON object containing the overall interview metrics and evaluation response, 
        or an error message if an exception occurs during processing.
    """
    try:
        history_str = '\n'.join(str(item) for item in data)

        # ipersona_metric = IpersonaSmgCretrionMetricSchema()
        # data_content = ipersona_metric.get_smgCriterionMetric_by_id(metricId=163, nopp=True, dataframe=False)
        # message = data_content.get('attributes', {}).get('content', {})
        # tag = 'parrot_overall_evaluation'
        # content = fetch_config_template(type, tag)
        # message = content.get('content', '')
        # message = message.replace("{history}", history_str)  
       
        overall_evaluation_msg = read_prompt_overall_evaluation(type, history_str)


        # data_content_metrics = ipersona_metric.get_smgCriterionMetric_by_id(metricId=173, nopp=True, dataframe=False)
        # message = data_content_metrics.get('attributes', {}).get('content', {})
        # tag = 'parrot_interview_evaluation_metrics'
        # content = fetch_config_template(type, tag)
        # message = content.get('content', '')
        # message = message.replace("{history}", history_str) 
         
        overall_metrics_msg = read_prompt_interview_evaluation_metrics(type, history_str)

        persona = ''
        content = persona + overall_evaluation_msg
        
        overall_evaluation_response = gpt.openai_gpt_assistant_without_streaming(content)

        overall_evaluation_response_json = extract_json(overall_evaluation_response, quite=False)
        
        persona = ''
        content = persona + overall_metrics_msg

        overall_interview_metrics_response = gpt.openai_gpt_assistant_without_streaming(content)
        overall_interview_metrics_json = extract_json(overall_interview_metrics_response, quite=False)
        time_array = calculate_time(data)
        relevancy = filter_the_relevancies_external(data)
        percent_term = percentage_term(relevancy["average"])
        
        overall_evaluation_response_json["overall_evaluation"]["message"] = percent_term["term"]
        overall_interview_metrics_json["evaluation_metrics"]["message"] = percent_term["term"]
        overall_interview_metrics_json["evaluation_metrics"]["time_management"] = time_array
        overall_interview_metrics_json["evaluation_metrics"]["relevancy"] = relevancy["relevancy"]
        overall_interview_metrics_json["evaluation_metrics"]["overall_performance_score"] = relevancy["average"]
        overall_interview_metrics_json["evaluation_metrics"]["rating"] = percent_term["rating"]
        overall_interview_metrics_json["evaluation_metrics"]["competency"] = overall_evaluation_response_json["overall_evaluation"]["competency"]
        
        ############################## Save final chat history to strapi #########################################        
        overall_interview_metrics_json = overall_interview_metrics_json["evaluation_metrics"]
        
        overall_evaluation_response_json = overall_evaluation_response_json["overall_evaluation"]
        overall_json = {
                "attributes": {
                    "interview_evaluation": overall_evaluation_response_json,
                    "interview_evaluation_metrics": overall_interview_metrics_json,
                },
                "i_persona_session": sessionId,
                "status": status            
            }

        ipersona_observer = IpersonaSessionObserverSchema(run_stage=run_stage)
        save_observer = ipersona_observer.save_observer(params=overall_json, nopp=True, dataframe=False)
        ipersona_session = IpersonaSessionSchema(run_stage=run_stage)
        if save_observer:
            logger.info("session observer to database")

        session_data = {
            "i_persona_session_id": sessionId, 
            "status": status,
        }
        updated_session = ipersona_session.update_session(params=session_data, nopp=True, dataframe=False, return_object=True)
     
        if updated_session:
            logger.info("session status updated to closed")
                      
        session = ipersona_session.filter_by_with_user_job_id(
            user_profile_id=tinder_user_profile_id,
            job_profile_id=job_profile_id, 
            nopp=True, 
            dataframe=False
            ) 
        # return session
        session_chatobserver = extract_observers_metrics(session)

        if status == 'External':  
            await calculate_overall_progress_external(
                run_stage, 
                all_user_id, 
                tinder_user_profile_id, 
                job_profile_id, 
                session_chatobserver) 
      
      
        response = {
            "overall_interview_metrics": overall_interview_metrics_json,
            "overall_evaluation_response": overall_evaluation_response_json
        }
        
        return response
        
    except Exception as e:
        logger.error(f"Overall evaluation process failed: {str(e)}")
        return {'error': str(e)}    
                  
#---------------------------------------- Interview Question Clarification ---------------------------------
async def clarify_question(question: str) -> dict:
    """
    Clarifies a given interview question.

    This asynchronous function generates a clarification request for the provided 
    question and calls the HR agent to obtain a clarified version.

    Parameters:
    ----------
    question : str
        The interview question that needs clarification.

    Returns:
    -------
    dict
        A JSON object containing the clarified question, or an error message if 
        an exception occurs during processing.
    """
    try:
        message = file_reader(prompts_path("ipersona/clarify_question.txt"))
        context = str(message)
        msg = context.replace("{question}", question)
        # response = await hr_agent.interview_question_clarification(msg)
        response = gpt.openai_gpt_assistant_without_streaming(msg)
        response = extract_json(response, quite=False)
    
        return response
    
    except Exception as e:
        logger.error(f"Overall evaluation process failed: {str(e)}")

        return {'error': str(e)}


#------------------- Job Description Class Identifier -------------------
def identify_class(all_class: list, jd: str) -> dict:
    """
    Identifies the class of a given job description (JD).

    This function uses the OpenAI API to classify the provided job description 
    into one of the specified classes. It aims to determine the most relevant 
    class if the JD could belong to multiple types.

    Parameters:
    ----------
    all_class : list
        A list of possible classes to which the job description could belong.

    jd : str
        The job description to classify.

    Returns:
    -------
    dict
        A JSON object containing the identified class for the job description, 
        or an error message if an exception occurs during processing.
    """
    try:
        result = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": f"I need you to give to which class this JD belongs to classes. The types should be only be one for each class. If the JD holds more types then decide the one the can hold others {str(all_class)} JD: {jd} as json",
                }
            ],
            response_format={"type": "json_object"},
        )
        
        return json.loads(result.choices[0].message.content)

    
    except Exception as e:
        logger.error(f"Persona class identification failed: {str(e)}")
        return {'error': str(e)}
    
def time_to_seconds(time_str):
    """Convert time in 'HH:MM:SS' or 'MM:SS' format to seconds."""
    try:
        # Handle null/None values
        if time_str is None or time_str == "null" or time_str == "null":
            return 0
            
        if not time_str or time_str == "00:00" or time_str == "00:00:00":
            return 0
        
        # Handle text-based time formats like "1 minute", "2 minutes", etc.
        if isinstance(time_str, str) and "minute" in time_str.lower():
            import re
            # Extract number from text like "1 minute", "2 minutes"
            match = re.search(r'(\d+)', time_str)
            if match:
                minutes = int(match.group(1))
                return minutes * 60
            else:
                return 0
        
        # Handle colon-separated formats
        time_parts = time_str.split(':')
        
        if len(time_parts) == 2:
            m, s = map(int, time_parts)
            return m * 60 + s
        elif len(time_parts) == 3:
            h, m, s = map(int, time_parts)
            return h * 3600 + m * 60 + s
        else:
            raise ValueError(f"Invalid time format: {time_str}")
    except ValueError as e:
        logger.error(f"Error converting time: {e}")
        return 0

def seconds_to_time(seconds):
    try:
        """Convert seconds back to 'HH:MM:SS' format."""
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60
        return f"{h:02}:{m:02}:{s:02}"
    except Exception as e:
        logger.error(f"Error processing files: {e}")
        return {'error': str(e)}

#----------------------------------------- Overall Time Data Calculator ----------------------------------------- 
def calculate_time(interview: list) -> dict:
    """
    Calculates the time taken by candidates in relation to the time limits set by the assistant.

    This function iterates through the interview data to determine how many times a candidate 
    exceeded the time limits for their responses compared to the limits set by the assistant.

    Parameters:
    ----------
    interview : list
        A list of dictionaries representing the interview history, where each dictionary 
        contains the responses from both the assistant and the candidate.

    Returns:
    -------
    dict
        A JSON object containing the counts of times a candidate exceeded the time limits 
        ("fail") and those count times it stayed within the limits ("pass") for a single entire interview, or an error message 
        if an exception occurs during processing.
    """
    try:
        exceeded_count = 0
        not_exceeded_count = 0
        total_time_taken_by_candidate = 0
        
        for i in range(len(interview)):
            if interview[i]['user_type'] == 'assistant':
                assistant_response = interview[i]['content']
                if assistant_response and 'time_limit' in assistant_response:
                    time_limit = assistant_response['time_limit']
                    time_limit_seconds = time_to_seconds(time_limit)
                    
                    if i + 1 < len(interview) and interview[i+1]['user_type'] == 'candidate':
                        candidate_response = interview[i + 1]['content']
                        time_taken = candidate_response.get('time_taken', '00:00:00')  
                        time_taken_seconds = time_to_seconds(time_taken)
                    
                        total_time_taken_by_candidate += time_taken_seconds

                        if time_taken_seconds > time_limit_seconds:
                            exceeded_count += 1
                        else:
                            not_exceeded_count += 1
        
        total_time_taken_formatted = seconds_to_time(total_time_taken_by_candidate)

        time_data = {
            "fail": exceeded_count,
            "pass": not_exceeded_count,
            "total_time_taken_by_candidate": total_time_taken_formatted
        }
        
        return time_data
    
    except Exception as e:
        print(f"Calculating overall time failed: {str(e)}")
        return {'error': str(e)}
 
#----------------------------------------- Overall Answer Relevancy Data Calculator -----------------------------------------   
def filter_the_relevancies(data: list) -> dict:
    """
    Extracts relevancy data from real-time evaluations and calculates overall performance.

    This function filters and extracts relevancy levels and reasons from the assistant's 
    real-time evaluations of the interview data. It then computes the average relevancy 
    score to assess overall performance.

    Parameters:
    ----------
    data : list
        A list of dictionaries representing the interview history, where each 
        dictionary includes evaluations from the assistant.

    Returns:
    -------
    dict
        A JSON object containing a list of relevancy assessments with their 
        corresponding levels, as well as the average relevancy score, 
        or an error message if an exception occurs during processing.
    """
    try:
        relevancy = []
        index_counter = 1
        
        for entry in data:
            if entry['user_type'] == 'assistant' and entry['content'].get('realtime_evaluation'):
                evaluation = entry['content']['realtime_evaluation']
                if 'answer_relevancy' in evaluation:
                    for relevance in evaluation['answer_relevancy']:
                        relevance_with_index = {
                            "question_no": index_counter,  
                            "level": relevance['level'],
                            "reason": relevance['reason']
                        }
                        relevancy.append(relevance_with_index)
                        index_counter += 1 
                        
        levels = [int(item["level"]) for item in relevancy]
        average_relevancy = sum(levels) / len(levels) if levels else 0
        
        average_relevancy = round(average_relevancy, 2)
        
        data = {
            "relevancy": relevancy,
            "average": average_relevancy
        }
        return data
    
    except Exception as e:
        print(f"Filtering overall relevance process failed: {str(e)}")
        return {'error': str(e)}

def filter_the_relevancies_external(data: list) -> dict:
    """
    Extracts relevancy data from real-time evaluations and calculates overall performance.

    This function filters and extracts relevancy levels and reasons from the assistant's 
    real-time evaluations of the interview data. It then computes the average relevancy 
    score to assess overall performance.

    Parameters:
    ----------
    data : list
        A list of dictionaries representing the interview history, where each 
        dictionary includes evaluations from the assistant.

    Returns:
    -------
    dict
        A JSON object containing a list of relevancy assessments with their 
        corresponding levels, as well as the average relevancy score, 
        or an error message if an exception occurs during processing.
    """
    try:
        relevancy = []
        index_counter = 1
        
        for entry in data:
            if entry['user_type'] == 'candidate' and entry['content'].get('realtime_evaluation'):
                evaluation = entry['content']['realtime_evaluation']
                if 'answer_relevancy' in evaluation:
                    for relevance in evaluation['answer_relevancy']:
                        relevance_with_index = {
                            "question_no": index_counter,  
                            "level": relevance['level'],
                            "reason": relevance['reason']
                        }
                        relevancy.append(relevance_with_index)
                        index_counter += 1 
                        
        levels = [int(item["level"]) for item in relevancy]
        average_relevancy = sum(levels) / len(levels) if levels else 0
        
        average_relevancy = round(average_relevancy, 2)
        
        data = {
            "relevancy": relevancy,
            "average": average_relevancy
        }
        return data
    
    except Exception as e:
        print(f"Filtering overall relevance process failed: {str(e)}")
        return {'error': str(e)}

#----------------------------------------- Assigning Rating Metrics Value Range -----------------------------------------   
def percentage_term(percent: float) -> dict:
    """
    Assigns a rating metric based on the provided percentage.

    This function evaluates the given percentage and assigns a corresponding 
    term and rating based on predefined ranges.

    Parameters:
    ----------
    percent : float
        A numeric value representing the percentage (0 to 100).

    Returns:
    -------
    dict
        A JSON object containing the corresponding term and rating, or an error 
        message if the input is invalid or an exception occurs during processing.
    """
    try:
        if not isinstance(percent, (int, float)):
            return {'error': 'Invalid input'}  

        if percent < 0 or percent > 100:
            return {'error': 'Invalid input'}  

        if 90 <= percent <= 100:
            data = {
                "term": "Excellent",
                "rating": 4
            }
            return data
        elif 75 <= percent < 90:
            data = {
                "term": "Satisfactory",
                "rating": 3
            }
            return data
        elif 50 <= percent < 75:
            data = {
                "term": "Good",
                "rating": 2
            }
            return data
        else:
            data = {
                "term": "Poor",
                "rating": 1
            }
            return data
        
    except Exception as e:
        logger.error(f"Percentage term assignation process failed: {str(e)}")

        return {'error': str(e)}
    
#----------------------------------------- Entire Data Progress Calculator -----------------------------------------   
async def calculate_overall_progress(run_stage, userdata, data: list):
    try:
        # Log what the function received first
        logger.info(f"=== calculate_overall_progress function called ===")
        logger.info(f"Function received - run_stage: {run_stage}")
        logger.info(f"Function received - data length: {len(data) if data else 0}")
        
        confidence_overtime = []  
        clarity_overtime = []     
        engagement_overtime = [] 
        overall_time_managements = []
        overall_competencies = []
        overall_performance_scores = []
        obs_ids = []      

        # Extract parameters from the correct nested structure
        user_session = userdata.get('user_session', {})
        attributes = user_session.get('attributes', {})

        # Extract challenge_id from challenge_document.data.id
        challenge_doc = attributes.get('challenge_document', {})
        challenge_id = challenge_doc.get('data', {}).get('id', 0) if challenge_doc.get('data') else 0

        # Extract job_profile_id from tinder_job_profile.data.id
        job_profile = attributes.get('tinder_job_profile', {})
        job_profile_id = job_profile.get('data', {}).get('id', 0) if job_profile.get('data') else 0
        
        # Extract template_id from tinder_template.data.id
        template_id = user_session.get('id', 0)

        # ✅ Correct way to extract all_user_id (from root, not attributes)
        all_user_id = userdata.get('all_user_id', 0)

        logger.info(f"challenge_id::: {challenge_id}")
        logger.info(f"job_profile_id::: {job_profile_id}")
        logger.info(f"template_id::: {template_id}")
        logger.info(f"all_user_id::: {all_user_id}")
        
        # Convert to integers and handle empty strings
        try:
            challenge_id = int(challenge_id) if challenge_id and challenge_id != "" else 0
            job_profile_id = int(job_profile_id) if job_profile_id and job_profile_id != "" else 0
            template_id = int(template_id) if template_id and template_id != "" else 0
            all_user_id = int(all_user_id) if all_user_id and all_user_id != "" else 0
        except (ValueError, TypeError):
            challenge_id = 0
            job_profile_id = 0
            template_id = 0
            all_user_id = 0

        for entry in data:
            if isinstance(entry, dict):  
                iso_time = entry.get("createdAt", "")
                created_time = convert_iso_to_readable_format(iso_time)
                performance = entry.get("performance", [])
                realtime = entry.get('communication_skills', []) 
                time = entry.get('time_management', {})
                competency = entry.get('competency', [])
                overall_performance_score = entry.get("overall_performance_score", "")
                obs_id = entry.get("obs_id")  
                
                if obs_id:
                    obs_ids.append(int(obs_id))  
                
                obj_time = {
                    "time": created_time,
                    "time_management": time
                }
                overall_time_managements.append(obj_time)
                
                obj_competency = {
                    "time": created_time,
                    "competency": competency
                }
                overall_competencies.append(obj_competency)   
                
                obj_score = {
                    "time": created_time,
                    "score": overall_performance_score
                }
                overall_performance_scores.append(obj_score)   
                 
                if isinstance(performance, list):
                    for item in performance:
                        confidence_level = item.get('level', '').lower()
                        if confidence_level == 'poor':
                            value = 1
                        elif confidence_level == 'good':
                            value = 2
                        elif confidence_level == 'excellent':
                            value = 3
                        confidence = {"time": created_time, "level": confidence_level, "value": value}
                        confidence_overtime.append(confidence)                        
               
                if isinstance(realtime, list):
                    for communication in realtime:  
                        if communication.get('skill') == "clarity":  
                            clarity_level = communication['level'].lower() 
                            value = 1 if clarity_level == 'poor' else 2 if clarity_level == 'good' else 3
                            clarity = {"time": created_time, "level": clarity_level, "value": value}
                            clarity_overtime.append(clarity)

                        if communication.get('skill') == "engagement":  
                            engagement_level = communication['level'].lower()  
                            value = 1 if engagement_level == 'poor' else 2 if engagement_level == 'good' else 3
                            engagement = {"time": created_time, "level": engagement_level, "value": value}
                            engagement_overtime.append(engagement)
                            
        ipersona_overall = IpersonaSessionOverallObserverSchema(run_stage=run_stage)
        ipersona_user = IpersonaTraineeSchema(run_stage=run_stage)

        trainee_profile_data = ipersona_user.filter_by_alluser_id(all_user_id = all_user_id, nopp=True, dataframe=False)
        
        if not trainee_profile_data:
            logger.error(f"No trainee user profiles found for all_user_id: {all_user_id}")
            return f'Error: No trainee profile found for user {all_user_id}'
        
        tinder_user_profile_id = trainee_profile_data['id']    
        session_chatobserver = None

        if job_profile_id: 
            session_chatobserver = ipersona_overall.filter_by_with_user_and_job_id(
                user_profile_id = tinder_user_profile_id, 
                job_profile_id = job_profile_id, 
                nopp=True, 
                dataframe=False)
            
        elif challenge_id:
            session_chatobserver = ipersona_overall.filter_by_with_user_and_challenge_id(
                user_profile_id = tinder_user_profile_id, 
                challenge_id = challenge_id, 
                nopp=True, 
                dataframe=False)

        elif template_id:
            session_chatobserver = ipersona_overall.filter_by_with_user_and_template_id(
                user_profile_id = tinder_user_profile_id, 
                template_id = template_id, 
                nopp=True, 
                dataframe=False)

        # Add comprehensive null check
        if session_chatobserver is None:
            logger.error(f"Database query returned None for user {tinder_user_profile_id}")
            logger.error(f"Query parameters - job_profile_id: {job_profile_id}, challenge_id: {challenge_id}, template_id: {template_id}")
            return f'Error: No session data found for the given parameters'
        
        # Handle both list and dict cases from database query
        session_id = None
        if isinstance(session_chatobserver, list) and len(session_chatobserver) > 0:
            # Database returned a list - take the first item
            session_data = session_chatobserver[0]
            if isinstance(session_data, dict) and not session_data.get("error"):
                logger.info(f"Session job overall observer data exists, so updating the data")          
                session_chatobserver_sessions = session_data['all_sessions']
                session_id = session_data['id']
            else:
                session_chatobserver_sessions = None
        elif isinstance(session_chatobserver, dict) and not session_chatobserver.get("error"):
            logger.info(f"Session job overall observer data exists, so updating the data")          
            session_chatobserver_sessions = session_chatobserver['all_sessions']
            session_id = session_chatobserver['id']
        else:
            session_chatobserver_sessions = None
        
        if session_chatobserver_sessions and len(session_chatobserver_sessions) > 0:
                logger.info(f"Updating session job overall observer data")
                new_overall_data = {
                    "overall_confidence": confidence_overtime,
                    "overall_clarity": clarity_overtime,
                    "overall_engagement": engagement_overtime,
                    "overall_time_management": overall_time_managements,
                    "overall_competency": overall_competencies,
                    "overall_performance": overall_performance_scores
                }
                existing_overall_data = session_chatobserver_sessions[0]
                update_overall_data = append_new_session_metrics(existing_overall_data, new_overall_data)
                            
                message_data = {
                    "i_persona_session_overall_observer_id": session_id, 
                    "attributes": update_overall_data,
                    "i_persona_observers": obs_ids
                }
                if job_profile_id:
                    message_data["tinder_user_profile"] = tinder_user_profile_id
                    message_data["tinder_job_profile"] = job_profile_id
                elif challenge_id:
                    message_data["tinder_user_profile"] = tinder_user_profile_id
                    message_data["challenge_document"] = challenge_id
                elif template_id:
                    message_data["tinder_user_profile"] = tinder_user_profile_id
                    message_data["tinder_template"] = template_id

                response = ipersona_overall.update_session(
                    params=message_data, 
                    nopp=True, 
                    dataframe=False, 
                    return_object=True)
                
                if response:
                    logger.success(f"session overall observer data update with new insert anlaysis")   
        else:  
            logger.info(f"Creating a new session job overall observer data")          
                    
            ipersona_overall = IpersonaSessionOverallObserverSchema(run_stage=run_stage)
            ipersona_user = IpersonaTraineeSchema(run_stage=run_stage)

            trainee_profile_data = ipersona_user.filter_by_alluser_id(
                all_user_id=all_user_id, 
                nopp=True, 
                dataframe=False)
            
            if not trainee_profile_data:
                    logger.error(f"No trainee user profiles found for all_user_id: {all_user_id} in else block")
                    return f'Error: No trainee profile found for user {all_user_id} in else block'
            
            tinder_user_profile_id = trainee_profile_data['id']    
            message_data = {
                "attributes": {
                    "overall_confidence": confidence_overtime,
                    "overall_clarity": clarity_overtime,
                    "overall_engagement": engagement_overtime,
                    "overall_time_management": overall_time_managements,
                    "overall_competency": overall_competencies,
                    "overall_performance": overall_performance_scores
                },
                "i_persona_observers": obs_ids
            }

            # Add the correct attribute based on which ID is present
            if job_profile_id:
                message_data["tinder_user_profile"] = tinder_user_profile_id
                message_data["tinder_job_profile"] = job_profile_id
            elif challenge_id:
                message_data["tinder_user_profile"] = tinder_user_profile_id
                message_data["challenge_document"] = challenge_id
            elif template_id:
                message_data["tinder_user_profile"] = tinder_user_profile_id
                message_data["tinder_template"] = template_id

            response = ipersona_overall.save_Session_Overall_Observer(
                params=message_data, 
                nopp=True, 
                dataframe=False)
            
            logger.success(f"new entry make on session overall observer")
            return response
    
    except Exception as e:
        logger.error(f"Process failed: {str(e)}")
        logger.error(f"Exception type: {type(e).__name__}")
        return f'Error: {str(e)}'    

def append_new_session_metrics(existing_data: dict, new_session_metrics: dict) -> dict:
    """
    Appends new session metrics to the existing observer data for each metric key.
    Modifies and returns the existing_data dict.
    """
    metric_keys = [
        "overall_clarity",
        "overall_competency",
        "overall_confidence",
        "overall_engagement",
        "overall_performance",
        "overall_time_management"
    ]
    for key in metric_keys:
        existing_list = existing_data.get(key, [])
        new_list = new_session_metrics.get(key, [])
        # Ensure both are lists
        if not isinstance(existing_list, list):
            existing_list = []
        if not isinstance(new_list, list):
            new_list = []
        existing_data[key] = existing_list + new_list
    return existing_data

async def calculate_overall_progress_external(
        run_stage, 
        all_user_id,  
        tinder_user_profile_id, 
        job_profile_id, 
        data: list):
    try:
        logger.info(f"calculating overall progress for a job overtime")
        confidence_overtime = []  
        clarity_overtime = []     
        engagement_overtime = [] 
        overall_time_managements = []
        overall_competencies = []
        overall_performance_scores = []
        session_ids = []         

        for entry in data:
            if isinstance(entry, dict):  
                iso_time = entry.get("createdAt", "")
                created_time = convert_iso_to_readable_format(iso_time)
                performance = entry.get("performance", [])
                realtime = entry.get('communication_skills', []) 
                time = entry.get('time_management', {})
                competency = entry.get('competency', [])
                overall_performance_score = entry.get("overall_performance_score", "")
                obs_id = entry.get("obs_id")  
                
                if obs_id:
                    session_ids.append(int(obs_id))  
                
                obj_time = {
                    "time": created_time,
                    "time_management": time
                }
                overall_time_managements.append(obj_time)
                
                obj_competency = {
                    "time": created_time,
                    "competency": competency
                }
                overall_competencies.append(obj_competency)   
                
                obj_score = {
                    "time": created_time,
                    "score": overall_performance_score
                }
                overall_performance_scores.append(obj_score)   
                 
                if isinstance(performance, list):
                    for item in performance:
                        confidence_level = item.get('level', '').lower()
                        if confidence_level == 'poor':
                            value = 1
                        elif confidence_level == 'good':
                            value = 2
                        elif confidence_level == 'excellent':
                            value = 3
                        confidence = {"time": created_time, "level": confidence_level, "value": value}
                        confidence_overtime.append(confidence)                        
               
                if isinstance(realtime, list):
                    for communication in realtime:  
                        if communication.get('skill') == "clarity":  
                            clarity_level = communication['level'].lower() 
                            value = 1 if clarity_level == 'poor' else 2 if clarity_level == 'good' else 3
                            clarity = {"time": created_time, "level": clarity_level, "value": value}
                            clarity_overtime.append(clarity)

                        if communication.get('skill') == "engagement":  
                            engagement_level = communication['level'].lower()  
                            value = 1 if engagement_level == 'poor' else 2 if engagement_level == 'good' else 3
                            engagement = {"time": created_time, "level": engagement_level, "value": value}
                            engagement_overtime.append(engagement)
                            
        ipersona_overall = IpersonaSessionOverallObserverSchema(run_stage=run_stage)
        ipersona_user = IpersonaTraineeSchema(run_stage=run_stage)

        trainee_profile_data = ipersona_user.filter_by_alluser_id(all_user_id=all_user_id, nopp=True, dataframe=False)
        if not trainee_profile_data:
                logger.warn("No trainee user profiles found.")
                return []
        tinder_user_profile_id = trainee_profile_data['id']    
            
        session_chatobserver = ipersona_overall.filter_by_with_user_and_job_id(user_profile_id=tinder_user_profile_id, job_profile_id=job_profile_id, nopp=True, dataframe=False)
       
        
        # Handle both list and dict cases from database query
        session_id = None
        if isinstance(session_chatobserver, list) and len(session_chatobserver) > 0:
            # Database returned a list - take the first item
            session_data = session_chatobserver[0]
            if isinstance(session_data, dict) and not session_data.get("error"):
                logger.info(f"Session job overall observer data exists, so updating the data")          
                session_chatobserver_sessions = session_data['all_sessions']
                session_id = session_data['id']
            else:
                session_chatobserver_sessions = None
        elif isinstance(session_chatobserver, dict) and not session_chatobserver.get("error"):
            logger.info(f"Session job overall observer data exists, so updating the data")          
            session_chatobserver_sessions = session_chatobserver['all_sessions']
            session_id = session_chatobserver['id']
        else:
            session_chatobserver_sessions = None
            
        if session_chatobserver_sessions and len(session_chatobserver_sessions) > 0:
                logger.info(f"Updating session job overall observer data")
                attributes = {
                    "overall_confidence": confidence_overtime,
                    "overall_clarity":  clarity_overtime,
                    "overall_engagement": engagement_overtime,
                    "overall_time_management": overall_time_managements,
                    "overall_competency": overall_competencies,
                    "overall_performance": overall_performance_scores
                }
                            
                overall_data = {
                    "i_persona_session_overall_observer_id": session_id, 
                    "attributes": attributes,
                }
                response = ipersona_overall.update_session(params=overall_data, nopp=True, dataframe=False, return_object=True)
                if response:
                    logger.success(f"session overall observer data update with new insert anlaysis")   
        else:  
            logger.info(f"Creating a new session job overall observer data")          
                    
            ipersona_overall = IpersonaSessionOverallObserverSchema(run_stage=run_stage)
            ipersona_user = IpersonaTraineeSchema(run_stage=run_stage)

            trainee_profile_data = ipersona_user.filter_by_alluser_id(all_user_id=all_user_id, nopp=True, dataframe=False)
            if not trainee_profile_data:
                    logger.warn("No trainee user profiles found.")
                    return []
            tinder_user_profile_id = trainee_profile_data['id']    
            message_data = {
                "attributes": {
                    "overall_confidence": confidence_overtime,
                    "overall_clarity": clarity_overtime,
                    "overall_engagement": engagement_overtime,
                    "overall_time_management": overall_time_managements,
                    "overall_competency": overall_competencies,
                    "overall_performance": overall_performance_scores
                },
                "sessionIds": session_ids,
                "tinder_user_profile": tinder_user_profile_id,
                "tinder_job_profile": job_profile_id
            }
            
            response = ipersona_overall.save_Session_Overall_Observer(params=message_data, nopp=True, dataframe=False)
            logger.success(f"new entry make on session overall observer")
            return response
    
    except Exception as e:
        logger.error(f"Process failed: {str(e)}")
        return f'Error: {str(e)}'  
    
#-------------- Entire User Session Progress Over All Types of Jobs ---------------
def all_session_jobs_average_metrics(data):
    try:
        if not isinstance(data, list) or len(data) == 0:
            raise ValueError("Data is empty or not in the expected list format")

        # Aggregate all values across all sessions
        all_confidence = []
        all_clarity = []
        all_engagement = []
        all_time_management = []

        for session in data:
            # Some values may be strings or missing, skip if not a list
            conf = session.get('overall_confidence', [])
            if isinstance(conf, list):
                all_confidence.extend(conf)
            clar = session.get('overall_clarity', [])
            if isinstance(clar, list):
                all_clarity.extend(clar)
            eng = session.get('overall_engagement', [])
            if isinstance(eng, list):
                all_engagement.extend(eng)
            tm = session.get('overall_time_management', [])
            if isinstance(tm, list):
                all_time_management.extend(tm)

        avg_confidence = calculate_average(all_confidence)
        avg_clarity = calculate_average(all_clarity)
        avg_engagment = calculate_average(all_engagement)
        avg_time_management = calculate_average_time_management(all_time_management)

        overall_data = {
            "avg_confidence": avg_confidence,
            "avg_clarity": avg_clarity,
            "avg_engagment": avg_engagment,
            "avg_time_management": avg_time_management
        }

        return overall_data

    except Exception as e:
        logger.error(f"Process failed in all_session_jobs_average_metrics: {str(e)}")
        return {"error": f"Process failed: {str(e)}"}
    
def calculate_average(data):
    try:
        if not isinstance(data, list) or len(data) == 0:
            raise ValueError("Data is empty or not in the expected list format")

        total_score = 0
        count = 0

        for entry in data:
            if isinstance(entry, dict):
                value = entry.get("value", 0)
                total_score += value
                count += 1
            else:
                logger.warn(f"Skipping invalid entry in calculate_average: {entry}")

        average = total_score / count if count > 0 else 0
        return round(average, 2)

    except Exception as e:
        logger.error(f"Error calculating average: {str(e)}")
        return {'error': f"Error calculating average: {str(e)}"}

def calculate_average_time_management(data):
    try:
        if not isinstance(data, list) or len(data) == 0:
            raise ValueError("Data is empty or not in the expected list format")

        total_passes = 0
        total_fails = 0

        for entry in data:
            if isinstance(entry, dict):
                time_management = entry.get("time_management", {})
                passes = time_management.get("pass", 0)
                fails = time_management.get("fail", 0)

                total_passes += passes
                total_fails += fails
            else:
                logger.warn(f"Skipping invalid entry in calculate_average_time_management: {entry}")

        total_questions = total_passes + total_fails

        average_pass_rate = round((total_passes / total_questions) * 100, 2) if total_questions > 0 else 0
        average_fail_rate = round((total_fails / total_questions) * 100, 2) if total_questions > 0 else 0

        return {
            "total_passes": total_passes,
            "total_fails": total_fails,
            "average_pass_rate": average_pass_rate,
            "average_fail_rate": average_fail_rate
        }

    except Exception as e:
        logger.error(f"Error calculating time management averages: {str(e)}")
        return {'error': f"Error calculating time management averages: {str(e)}"}

#-------------------------------------------- user engagment jobs --------------------------------------------
def add_columns(
    params, 
    cursor, 
    job_profile_id, 
    job_title,
    company_name,
    location,
    url,
    kind, 
    **kwargs):
    try:
        output = []
        if kwargs.get('information_level','minimal')=='minimal':
            try:
                job_reaction_manager = JobReactionManager()
                output = job_reaction_manager.prepare_table(
                    params, 
                    cursor, 
                    job_profile_id, 
                    job_title,
                    company_name,
                    location,
                    url,
                    kind=kind)
            except Exception as e:
                logger.error(f'Error preparing leap table: {e}')
                output = []
                
            if isinstance(output, dict):
                output = [output]
            elif not isinstance(output, list):
                output = [output]            
        else:
            output = params
            
        return output
    except Exception as e:
        logger.error(f'Error adding columns to leap table: {e}')
        output = [] 

def add_challenge_columns(
    params, 
    cursor, 
    challenge_id, 
    challenge_title,
    kind, 
    **kwargs):
    try:
        output = []
        if kwargs.get('information_level','minimal')=='minimal':
            try:
                job_reaction_manager = JobReactionManager()
                output = job_reaction_manager.prepare_table_challenge(
                    params, 
                    cursor, 
                    challenge_id, 
                    challenge_title,
                    kind=kind)
            except Exception as e:
                logger.error(f'Error preparing leap table: {e}')
                output = []
                
            if isinstance(output, dict):
                output = [output]
            elif not isinstance(output, list):
                output = [output]            
        else:
            output = params
            
        return output
    except Exception as e:
        logger.error(f'Error adding columns to leap table: {e}')
        output = [] 

def add_engagement_columns(
    params, 
    cursor, 
    kind, 
    **kwargs):
    try:
        output = []
        if kwargs.get('information_level','minimal')=='minimal':
            try:
                job_reaction_manager = JobReactionManager()
                output = job_reaction_manager.prepare_engagement_table(
                    params, 
                    cursor, 
                    kind=kind)
            except Exception as e:
                logger.error(f'Error preparing leap table: {e}')
                output = []
                
            if isinstance(output, dict):
                output = [output]
            elif not isinstance(output, list):
                output = [output]            
        else:
            output = params
            
        return output
    except Exception as e:
        logger.error(f'Error adding columns to leap table: {e}')
        output = [] 

def add_template_columns(
    params, 
    cursor, 
    kind, 
    **kwargs):
    try:
        output = []
        if kwargs.get('information_level','minimal')=='minimal':
            try:
                job_reaction_manager = JobReactionManager()
                output = job_reaction_manager.prepare_template_table(
                    params, 
                    cursor, 
                    kind=kind)
            except Exception as e:
                logger.error(f'Error preparing leap table: {e}')
                output = []
                
            if isinstance(output, dict):
                output = [output]
            elif not isinstance(output, list):
                output = [output]            
        else:
            output = params
            
        return output
    except Exception as e:
        logger.error(f'Error adding columns to leap table: {e}')
        output = [] 

#-------------------------------------------- user engagment jobs --------------------------------------------
from typing import Any, Dict, List, Optional

def simplify_templates(templates: Any) -> List[Dict[str, Optional[str]]]:
    if not isinstance(templates, list):
        return []

    simplified: List[Dict[str, Optional[str]]] = []
    for item in templates:
        try:
            if not isinstance(item, dict):
                continue

            template_id = item.get("id")
            attrs = item.get("attributes") if isinstance(item.get("attributes"), dict) else {}

            simplified.append({
                "template_id": str(template_id) if template_id is not None else None,
                "name": attrs.get("name") if isinstance(attrs.get("name"), (str, type(None))) else None,
                "tag": attrs.get("tag") if isinstance(attrs.get("tag"), (str, type(None))) else None,
                "description": attrs.get("description") if isinstance(attrs.get("description"), (str, type(None))) else None,
            })
        except Exception:
            continue

    return simplified

def summarize_interviews(
    run_stage,
    user_profile_id, 
    filter,
    cursor,
    since, 
    limit,
    information_level,
    return_skip
):  
    try:
        ipersona_session = IpersonaSessionSchema(run_stage=run_stage)
        query_filter = filter or {}
        kwargs = {**query_filter}

        data, cursors = ipersona_session.filter_by_tinder_user_profile_id(
            user_profile_id=user_profile_id, 
            cursor=cursor, 
            since=since, 
            limit=limit, 
            nopp=True, 
            dataframe=False,
            **kwargs
        )
        #return data, cursors
        if not data:
            output = add_engagement_columns([], cursor, kind='jobs', **kwargs)
            return output, cursors

        data = extracted_needed_metrics(data)
        # return data, cursors
        if not data:
            logger.info("The given trainee has no observer data after metric extraction.")
            return add_engagement_columns([], cursor, kind='jobs', **kwargs), cursors

        # Step 1: Filter for valid job_profile_id
        valid_records = [d for d in data if d.get("job_profile_id") not in (None, 0)]

        if not valid_records:
            logger.info("No valid job_profile_id found.")
            return add_engagement_columns([], cursor, kind='jobs', **kwargs), cursors

        # Step 2: Group by job_profile_id
        job_summary = defaultdict(list)
        for record in valid_records:
            job_summary[record["job_profile_id"]].append(record)

        summary_response = []

        # Step 3: Loop through valid job_profile_id groups
        for job_profile_id, records in job_summary.items():
            complete_count = sum(1 for r in records if r.get("complete_status"))
            incomplete_count = len(records) - complete_count

            total_score = sum(
                r.get("overall_performance_score", 0)
                for r in records if r.get("overall_performance_score") is not None
            )
            average_score = (
                round(total_score / complete_count, 2)
                if complete_count > 0 else "N/A"
            )

            # Fetch job title
            ipersona_job = IpersonaJobSchema(run_stage=run_stage)
            job_title_data = ipersona_job.filter_by_job_id(
                job_profile_id=job_profile_id, nopp=True, dataframe=False
            )

            job_title = (
                job_title_data[0]["attributes"]["attributes"].get("title", "Unknown Job Title")
                if job_title_data else "Unknown Job Title"
            )

            # Fetch match and reaction data
            ipersona_match = IpersonaSessionTinderUserJobMatchSchema(run_stage=run_stage)
            job_match_data = ipersona_match.filter_by_with_user_and_job_id(
                user_profile_id=user_profile_id, job_profile_id=job_profile_id,
                nopp=True, dataframe=False
            )

            ipersona_reaction = IpersonaSessionTinderUserReactionSchema(run_stage=run_stage)
            reaction_id = ipersona_reaction.filter_by_with_user_and_job_id(
                user_profile_id=user_profile_id, 
                job_profile_id=job_profile_id,
                nopp=True, dataframe=False
            )

            match_score = (
                job_match_data[0]["attributes"].get("match_score", "Unknown")
                if job_match_data else "Unknown"
            )
            job_match = (
                job_match_data[0]["attributes"].get("match_level", "Unknown")
                if job_match_data else "Unknown"
            )

            summary_response.append({
                "job_profile_id": job_profile_id,
                "reaction_id": reaction_id,
                "job_title": job_title,
                "job_match_score": match_score,
                "job_match": job_match,
                "complete_interviews_count": complete_count,
                "incomplete_interviews_count": incomplete_count,
                "total_interviews_count": complete_count + incomplete_count,
                "score": average_score,
            })

        cursor["total"] = len(summary_response)
        output = add_engagement_columns(summary_response, cursor, kind="jobs", **kwargs)
        return output, cursors

    except Exception as e:
        logger.error(f"Error processing files: {e}")
        return str(e), str(e)

def summarize_challenge_interviews(
    run_stage,
    user_profile_id, 
    filter,
    cursor,
    since, 
    limit,
    information_level,
    return_skip
):
    try:
        ipersona_session = IpersonaSessionSchema(run_stage=run_stage)
        query_filter = filter or {}
        kwargs = {**query_filter}

        data, cursors = ipersona_session.filter_by_tinder_user_profile_id(
            user_profile_id=user_profile_id, 
            cursor=cursor, 
            since=since, 
            limit=limit, 
            nopp=True, 
            dataframe=False,
            **kwargs
        )

        if not data:
            logger.info("No session data found.")
            return add_engagement_columns([], cursor, kind='challenge', **kwargs), cursors

        # Step 1: Extract metrics
        data = extracted_needed_metrics(data)

        if not data:
            logger.info("No data found after metric extraction.")
            return add_engagement_columns([], cursor, kind='challenge', **kwargs), cursors

        # Step 2: Filter for valid challenge_id only
        valid_records = [d for d in data if d.get("challenge_id") not in (None, 0)]

        if not valid_records:
            logger.info("No valid challenge_id found.")
            return add_engagement_columns([], cursor, kind='challenge', **kwargs), cursors

        # Step 3: Group by challenge_id
        challenge_summary = defaultdict(list)
        for record in valid_records:
            challenge_summary[record["challenge_id"]].append(record)

        summary_response = []

        # Step 4: Process each valid challenge group
        for challenge_id, records in challenge_summary.items():
            complete_count = sum(1 for r in records if r.get("complete_status"))
            incomplete_count = len(records) - complete_count

            total_score = sum(
                r.get("overall_performance_score", 0) for r in records if r.get("overall_performance_score") is not None
            )

            average_score = (
                round(total_score / complete_count, 2)
                if complete_count > 0 else "N/A"
            )

            try:
                ipersona_job = IpersonaChallengeDocumentSchema(run_stage=run_stage)
                challenge_data = ipersona_job.get_challenge_by_id(
                    challengeId=challenge_id,
                    nopp=True,
                    dataframe=False
                )

                if not challenge_data or not isinstance(challenge_data, dict):
                    logger.warning(f"Challenge data not found or invalid for challenge_id {challenge_id}")
                    continue

                challenge_title = challenge_data.get("attributes", {}).get("Title", "")

            except Exception as e:
                logger.error(f"Failed to fetch challenge data for challenge_id {challenge_id}: {e}")
                continue

            summary_response.append({
                "challenge_id": challenge_id,
                "challenge_title": challenge_title,
                "complete_interviews_count": complete_count,
                "incomplete_interviews_count": incomplete_count,
                "total_interviews_count": complete_count + incomplete_count,
                "score": average_score
            })

        cursor["total"] = len(summary_response)
        output = add_engagement_columns(summary_response, cursor, kind='challenge', **kwargs)

        return output, cursors

    except Exception as e:
        logger.error(f"Error processing challenge interviews: {e}")
        return str(e), str(e)

def summarize_template_interviews(
    run_stage,
    user_profile_id,
    filter,
    cursor,
    since,
    limit,
    information_level,
    return_skip
):
    try:
        ipersona_session = IpersonaSessionSchema(run_stage=run_stage)
        query_filter = filter or {}
        kwargs = {**query_filter}

        data, cursors = ipersona_session.filter_by_tinder_user_profile_id(
            user_profile_id=user_profile_id,
            cursor=cursor,
            since=since,
            limit=limit,
            nopp=True,
            dataframe=False,
            **kwargs
        )
        # return data, cursors
        if not data:
            logger.info("No session data found.")
            return add_engagement_columns([], cursor, kind='template', **kwargs), cursors

        # Step 1: Extract metrics
        data = extracted_needed_metrics(data)

        if not data:
            logger.info("No data found after metric extraction.")
            return add_engagement_columns([], cursor, kind='template', **kwargs), cursors

        # Step 2: Filter for valid template_id only
        valid_records = [d for d in data if d.get("template_id") not in (None, 0)]

        if not valid_records:
            logger.info("No valid template_id found.")
            return add_engagement_columns([], cursor, kind='template', **kwargs), cursors

        # Step 3: Group by template_id
        template_summary = defaultdict(list)
        for record in valid_records:
            template_summary[record["template_id"]].append(record)

        summary_response = []

        # Step 4: Process each valid template group
        for template_id, records in template_summary.items():
            complete_count = sum(1 for r in records if r.get("complete_status"))
            incomplete_count = len(records) - complete_count

            total_score = sum(
                r.get("overall_performance_score", 0) for r in records if r.get("overall_performance_score") is not None
            )

            average_score = (
                round(total_score / complete_count, 2)
                if complete_count > 0 else "N/A"
            )

            template_title = "Unknown Template"
            try:
                ipersona_template = None
                try:
                    ipersona_template = IpersonaTinderTemplateSchema(run_stage=run_stage)
                except Exception:
                    ipersona_template = IpersonaTinderTemplateSchema()

                template_data = ipersona_template.get_tinder_template_id(
                    templateId=template_id,
                    nopp=True,
                    dataframe=False
                )

                if isinstance(template_data, list) and len(template_data) > 0 and isinstance(template_data[0], dict):
                    template_title = template_data[0].get("attributes", {}).get("name", "Unknown Template")
                elif isinstance(template_data, dict):
                    template_title = template_data.get("attributes", {}).get("name", "Unknown Template")
            except Exception as e:
                logger.error(f"Failed to fetch template data for template_id {template_id}: {e}")

            summary_response.append({
                "template_id": template_id,
                "template_title": template_title,
                "complete_interviews_count": complete_count,
                "incomplete_interviews_count": incomplete_count,
                "total_interviews_count": complete_count + incomplete_count,
                "score": average_score
            })

        cursor["total"] = len(summary_response)
        output = add_engagement_columns(summary_response, cursor, kind='template', **kwargs)

        return output, cursors

    except Exception as e:
        logger.error(f"Error processing template interviews: {e}")
        return str(e), str(e)

def summarize(
    run_stage,
    user_profile_id,
    filter,
    cursor,
    since,
    limit,
    information_level,
    return_skip
):
    try:
        ipersona_session = IpersonaSessionSchema(run_stage=run_stage)
        query_filter = filter or {}
        kwargs = {**query_filter}

        data, cursors = ipersona_session.filter_by_tinder_user_profile_id(
            user_profile_id=user_profile_id,
            cursor=cursor,
            since=since,
            limit=limit,
            nopp=True,
            dataframe=False,
            **kwargs
        )

        if not data:
            return [], cursors

        data = extracted_needed_metrics(data)
        
        if not data:
            logger.info("No session data found.")
            return add_engagement_columns([], cursor, kind='engagment-all', **kwargs), cursors


        summary_map = defaultdict(list)

        # Step 1: Group by either job_profile_id, challenge_id, or template_id
        for record in data:
            if record.get("job_profile_id") not in (None, 0):
                key = ("job", record["job_profile_id"])
            elif record.get("challenge_id") not in (None, 0):
                key = ("challenge", record["challenge_id"])
            elif record.get("template_id") not in (None, 0):  # NEW: Template-only sessions
                key = ("template", record["template_id"])
            else:
                continue  # skip invalid record
            summary_map[key].append(record)

        summary_response = []
        ipersona_job = IpersonaJobSchema(run_stage=run_stage)
        ipersona_challenge = IpersonaChallengeDocumentSchema(run_stage=run_stage)

        # Step 2: Process each group
        for (interview_type, profile_id), records in summary_map.items():
            complete_count = sum(1 for r in records if r.get("complete_status"))
            total_score = sum(
                r.get("overall_performance_score", 0)
                for r in records
                if r.get("overall_performance_score") is not None
            )
            average_score = round(total_score / complete_count, 2) if complete_count > 0 else 0

            if interview_type == "job":
                job_title_data = ipersona_job.filter_by_job_id(profile_id, nopp=True, dataframe=False)
                title = job_title_data[0]["attributes"]["attributes"].get("title", "Unknown Job Title") if job_title_data else "Unknown Job Title"
                ipersona_reaction = IpersonaSessionTinderUserReactionSchema(run_stage=run_stage)
                reaction_id = ipersona_reaction.filter_by_with_user_and_job_id(
                    user_profile_id=user_profile_id, 
                    job_profile_id=profile_id,
                    nopp=True, dataframe=False
                )
                summary_response.append({
                    "type": "job",
                    "title": title,
                    "interview_count": len(records),
                    "score": average_score,
                    "job_profile_id": profile_id,
                    "challenge_id": None,
                    "template_id": None,
                    "user_profile_id": user_profile_id,
                    "reaction_id": reaction_id
                })

            elif interview_type == "challenge":
                challenge_data = ipersona_challenge.get_challenge_by_id(challengeId=profile_id, nopp=True, dataframe=False)
                title = challenge_data.get("attributes", {}).get("Title", "Unknown Challenge Title") if isinstance(challenge_data, dict) else "Unknown Challenge Title"
                summary_response.append({
                    "type": "challenge",
                    "title": title,
                    "interview_count": len(records),
                    "score": average_score,
                    "job_profile_id": None,
                    "challenge_id": profile_id,
                    "template_id": None,
                    "user_profile_id": user_profile_id,
                    "reaction_id": ''
                })

            elif interview_type == "template":
                # Fetch template title/name
                ipersona_template = IpersonaTinderTemplateSchema(run_stage=run_stage)
                template_data = ipersona_template.get_tinder_template_id(templateId=profile_id, nopp=True, dataframe=False)
                
                # Safety check for template_data
                if template_data:
                    if isinstance(template_data, list) and len(template_data) > 0:
                        title = template_data[0]["attributes"].get("name", "Unknown Template")
                    elif isinstance(template_data, dict) and "attributes" in template_data:
                        title = template_data["attributes"].get("name", "Unknown Template")
                    else:
                        title = "Unknown Template"
                        print(f"Warning: Unexpected template data format for template_id: {profile_id}")
                else:
                    title = "Unknown Template"
                    print(f"Warning: No template data found for template_id: {profile_id}")
                
                summary_response.append({
                    "type": "template",
                    "title": title,
                    "interview_count": len(records),
                    "score": average_score,
                    "job_profile_id": None,
                    "challenge_id": None,
                    "template_id": profile_id,
                    "user_profile_id": user_profile_id,
                    "reaction_id": ''
                })

        cursor["total"] = len(summary_response)
        output = add_engagement_columns(summary_response, cursor, kind='engagment-all', **kwargs)

        return output, cursors

    except Exception as e:
        logger.error(f"Error summarizing all interviews: {e}")
        return str(e), str(e)

def extracted_needed_metrics(data):
    try:
        extracted_observers = []  
        
        for session in data:
            if not isinstance(session, dict):
                continue
            extracted_session = {}
            
            # Extract session id safely
            extracted_session['session_id'] = session.get('id')
            
            # Get attributes safely
            attributes = session.get('attributes') or {}
            
            # Get observer data and session status
            observer_data = attributes.get('i_persona_observer', {}).get('data')
            session_status = attributes.get('status', 'Incomplete')
            metadata = attributes.get('metadata') or {}
            
            if session_status == 'Deleted':
                extracted_session['complete_status'] = 'deleted'
            elif session_status == 'Incomplete':
                extracted_session['complete_status'] = False
            else:
                # Completed, Closed, External, etc. - all complete
                extracted_session['complete_status'] = True

            if observer_data:
                # Extract observer attributes
                observer_attributes = observer_data.get('attributes', {}).get('attributes', {}).get('interview_evaluation_metrics', {})
                
                # Overall performance score
                extracted_session['overall_performance_score'] = observer_attributes.get('overall_performance_score', None)
                
                # Extract performance levels (confidence)
                performance = observer_attributes.get('performance', [])
                for item in performance:
                    if isinstance(item, dict):  
                        extracted_session['confidence'] = item.get('level', None)
                        
                # Extract communication skills (clarity and engagement)
                communication_skills = observer_attributes.get('communication_skills', [])
                for skill_data in communication_skills:
                    if isinstance(skill_data, dict):
                        if skill_data.get('skill') == 'clarity':
                            extracted_session['clarity'] = skill_data.get('level', None)
                        elif skill_data.get('skill') == 'engagement':
                            extracted_session['engagement'] = skill_data.get('level', None)        
            else:
                # Handle case where observer data is missing
                extracted_session['overall_performance_score'] = None
                extracted_session['confidence'] = None
                extracted_session['clarity'] = None
                extracted_session['engagement'] = None

            # Extract additional session details
            # attributes already defined
            extracted_session['createdAt'] = attributes.get('createdAt')

            extracted_session['job_profile_id'] = (
                attributes.get('tinder_job_profile', {}).get('data', {}) or {}
            ).get('id')

            extracted_session['template_id'] = (
                attributes.get('tinder_template', {}).get('data', {}) or {}
            ).get('id')

            extracted_session['challenge_id'] = (
                attributes.get('challenge_document', {}).get('data', {}) or {}
            ).get('id')

            extracted_session['user_profile_id'] = (
                attributes.get('tinder_user_profile', {}).get('data', {}) or {}
            ).get('id')
            extracted_session['mode'] = metadata.get('mode', {})
            
            # Append extracted session data
            extracted_observers.append(extracted_session)
        
        return extracted_observers  
    
    except Exception as e:
        logger.error(f"Error processing files: {e}")
        return {'error': str(e)}

def extracted_needed_metrics_temp(data):
    try:
        extracted_observers = []  
        
        for session in data:
            extracted_session = {}              
            # Extract session id
            extracted_session['session_id'] = session['id']
            
            # Get observer data
            observer_data = session['attributes'].get('i_persona_observer', {}).get('data')
            # slug = session['attributes'].get('slug', None)
      
            # Determine if the session is complete
            complete_status = observer_data is not None
            extracted_session['complete_status'] = complete_status  

            if observer_data:
                # Extract observer attributes
                observer_attributes = observer_data.get('attributes', {}).get('attributes', {}).get('interview_evaluation_metrics', {}).get('evaluation_metrics', {})
                
                # Overall performance score
                extracted_session['overall_performance_score'] = observer_attributes.get('overall_performance_score', None)
                
                # Extract performance levels (confidence)
                performance = observer_attributes.get('performance', [])
                for item in performance:
                    if isinstance(item, dict):  
                        extracted_session['confidence'] = item.get('level', None)
                        
                # Extract communication skills (clarity and engagement)
                communication_skills = observer_attributes.get('communication_skills', [])
                for skill_data in communication_skills:
                    if isinstance(skill_data, dict):
                        if skill_data.get('skill') == 'clarity':
                            extracted_session['clarity'] = skill_data.get('level', None)
                        elif skill_data.get('skill') == 'engagement':
                            extracted_session['engagement'] = skill_data.get('level', None)        
            else:
                # Handle case where observer data is missing
                extracted_session['overall_performance_score'] = None
                extracted_session['confidence'] = None
                extracted_session['clarity'] = None
                extracted_session['engagement'] = None

            # Extract additional session details
            attributes = session.get('attributes', {})

            extracted_session['createdAt'] = attributes.get('createdAt')

            extracted_session['job_profile_id'] = (
                attributes.get('tinder_job_profile', {}).get('data', {}) or {}
            ).get('id')

            extracted_session['template_id'] = (
                attributes.get('tinder_template', {}).get('data', {}) or {}
            ).get('id')

            extracted_session['challenge_id'] = (
                attributes.get('challenge_document', {}).get('data', {}) or {}
            ).get('id')

            extracted_session['user_profile_id'] = (
                attributes.get('tinder_user_profile', {}).get('data', {}) or {}
            ).get('id')

            # extracted_session['slug'] = slug
            # Append extracted session data
            extracted_observers.append(extracted_session)
        
        return extracted_observers  
    
    except Exception as e:
        logger.error(f"Error processing files: {e}")
        return {'error': str(e)}

def summarize_interviews_engagement(
    run_stage,
    user_profile_id, 
    cursors,
    data):  
    try:  
        # Fetch a particular user sessions
        
        summary_response = []
        if len(data) != 0:
            data = extracted_needed_metrics(data)
            if len(data) == 0:
                logger.info("The given trainee has no observer data")
                return []

            job_summary = defaultdict(list)

            for record in data:
                job_profile_id = record['job_profile_id']
                job_summary[job_profile_id].append(record)

                summary_response = []
                complete_sessions_count = 0
                incomplete_sessions_count = 0

            for job_profile_id, records in job_summary.items():
            
                for session in records:
                    complete_status = session.get('complete_status', {})
                
                    if complete_status:
                        complete_sessions_count += 1
                    else:
                        incomplete_sessions_count += 1
                                
                total_score = sum(
                    record.get('overall_performance_score', 0) for record in records if record.get('overall_performance_score') is not None
                )
                
                if total_score >= 0:
                    average_score = round(total_score / complete_sessions_count, 2) if complete_sessions_count > 0 else "N/A"
                else:
                    average_score = 'Not Available'
                
                ipersona_job = IpersonaJobSchema(run_stage=run_stage)
                job_title_data = ipersona_job.filter_by_job_id(job_profile_id=job_profile_id, nopp=True, dataframe=False)
                
                if job_title_data and len(job_title_data) > 0:
                    job_title = job_title_data[0]['attributes']['attributes'].get('title', 'Unknown Job Title')
                else:
                    job_title = 'Unknown Job Title'

                tinder_user_profile_id = user_profile_id
                tinder_job_profile_id = job_profile_id

                ipersona_match = IpersonaSessionTinderUserJobMatchSchema(run_stage=run_stage)
                job_match_data = ipersona_match.filter_by_with_user_and_job_id(user_profile_id=tinder_user_profile_id, job_profile_id=tinder_job_profile_id, nopp=True, dataframe=False)
                
                ipersona_reaction = IpersonaSessionTinderUserReactionSchema(run_stage=run_stage)
                reaction_id = ipersona_reaction.filter_by_with_user_and_job_id(user_profile_id=tinder_user_profile_id, job_profile_id=tinder_job_profile_id, nopp=True, dataframe=False)

                if job_match_data and len(job_match_data) > 0:
                    match_score = job_match_data[0]['attributes'].get('match_score', 'Unknown')
                    job_match = job_match_data[0]['attributes'].get('match_level', 'Unknown')
                else:
                    match_score = 'Unknown'
                    job_match = 'Unknown'
                            
                total_session_count = complete_sessions_count + incomplete_sessions_count

                summary_response.append({
                    "job_profile_id": job_profile_id,
                    "reaction_id": reaction_id,
                    "job_title": job_title,
                    "job_match_score": match_score,
                    "job_match": job_match,
                    'complete_interviews_count': complete_sessions_count,
                    'incomplete_interviews_count': incomplete_sessions_count,
                    'total_interviews_count': total_session_count,
                    "score": average_score
                })
            cursors['total'] = len(summary_response)   
        
            return summary_response, cursors
        else:
            cursors['total'] = len(summary_response)  
            return data, cursors
        
    except Exception as e:
        logger.error(f"Error processing files: {e}")
        error_msg = str(e)
        return error_msg, error_msg
 
def extract_observers_metrics(session_chatobserver):
    try:
        if isinstance(session_chatobserver, dict):
            session_list = [session_chatobserver]
        elif isinstance(session_chatobserver, list):
            session_list = session_chatobserver
        else:
            session_list = []

        extracted_observers = []

        for session in session_list:
            observer_data = (
                session.get("attributes", {})
                .get("i_persona_observer", {})
                .get("data", {})
            )

            if observer_data:
                attributes = observer_data.get("attributes", {})
                evaluation_metrics = attributes.get("attributes", {}).get("interview_evaluation_metrics", {})

                if evaluation_metrics:
                    evaluation_metrics["createdAt"] = session.get("attributes", {}).get("createdAt")
                    evaluation_metrics["obs_id"] = observer_data.get("id")
                    extracted_observers.append(evaluation_metrics)

        return extracted_observers
    except Exception as e:
        logger.error(f"Error processing files: {e}")
        return {'error': str(e)}

def calculate_session_metrics(sessions):
    try:
        session_count = 0
        job_profile_count = 0
        user_profile_count = 0
        complete_sessions = 0
        incomplete_sessions = 0 
        daily_sessions = defaultdict(int)
        weekly_sessions = defaultdict(int)
        monthly_sessions = defaultdict(int)
        yearly_sessions = defaultdict(int)
        daily_sessions_by_month = defaultdict(lambda: defaultdict(int))
        current_week_sessions = 0  
        
        # Getting the current UTC time and today's date (UTC)
        now = datetime.now(timezone.utc)
        today_date = now.date()
        current_month = now.month
        current_year = now.year
        
        # Getting the start of the current week (Monday)
        start_of_week = today_date - timedelta(days=today_date.weekday()) 

        unique_job_profiles = set()
        unique_user_profiles = set()
        today_sessions_count = 0  
        current_month_sessions = 0  
        current_year_sessions = 0  

        for session in sessions:
            session_count += 1

            attributes = session.get('attributes', {})
            if not isinstance(attributes, dict):
                logger.warn(f"Skipping session due to invalid 'attributes': {session}")
                continue

            job_profile = attributes.get('tinder_job_profile', {}).get('data', {})
            user_profile = attributes.get('tinder_user_profile', {}).get('data', {})

            if not isinstance(job_profile, dict):
                logger.warn(f"Skipping session due to invalid 'tinder_job_profile': {session}")
                continue

            if not isinstance(user_profile, dict):
                logger.warn(f"Skipping session due to invalid 'tinder_user_profile': {session}")
                continue

            job_profile_id = job_profile.get('id')
            user_profile_id = user_profile.get('id')

            if not job_profile_id or not user_profile_id:
                logger.warn(f"Skipping session due to missing job/user profile: {session}")
                continue

            if job_profile_id not in unique_job_profiles:
                unique_job_profiles.add(job_profile_id)
                job_profile_count += 1

            if user_profile_id not in unique_user_profiles:
                unique_user_profiles.add(user_profile_id)
                user_profile_count += 1

            i_persona_observer = attributes.get('i_persona_observer', {}).get('data')
            if i_persona_observer is None:
                incomplete_sessions += 1
            else:
                complete_sessions += 1
            
            created_at_str = attributes.get('createdAt', {})
            if created_at_str:
                # Converting the strapi createdAt string to a datetime object (in UTC)
                session_datetime = parse_iso_format_with_z(created_at_str)
                
                # Checking if the session is from today (UTC date comparison)
                if session_datetime.date() == today_date:
                    today_sessions_count += 1

                # Checking if the session is from the current month
                if session_datetime.month == current_month and session_datetime.year == current_year:
                    current_month_sessions += 1

                # Checking if the session is from the current week
                if start_of_week <= session_datetime.date() <= today_date:
                    current_week_sessions += 1
                    
                  # Checking if the session is from the current year
                if session_datetime.year == current_year:
                    current_year_sessions += 1

                # Group by day
                session_date = session_datetime.date()
                daily_sessions[session_date] += 1

                # Group by week (ISO calendar week number, which starts on Monday)
                year, week_num, _ = session_datetime.isocalendar() 
                weekly_sessions[f"{year}-W{week_num}"] += 1 

                # Group by month (year and month)
                year = session_datetime.year
                month = session_datetime.month
                monthly_sessions[f"{year}-{month}"] += 1  

                # Sessions grouped by day within each month (for plotting daily changes within the month)
                daily_sessions_by_month[f"{year}-{month:02d}"][session_date.day] += 1
                
                # Group by year
                yearly_sessions[year] += 1 

       
        result = {
            'interviews_count': session_count,
            'job_profile_count': job_profile_count,
            'user_profile_count': user_profile_count,
            'complete_sessions': complete_sessions,
            'incomplete_sessions': incomplete_sessions,
            'total_interview_sessions': complete_sessions + incomplete_sessions,
            'day_sessions': daily_sessions,
            'week_sessions': weekly_sessions,
            'month_sessions': monthly_sessions,
            'year_sessions': yearly_sessions,                    # Add yearly sessions to the result
            'today_sessions': today_sessions_count,              # Total sessions today
            'current_week_sessions': current_week_sessions,      # Total sessions in the current week
            'current_month_sessions': current_month_sessions,    # Total session in the current month
            'current_year_sessions': current_year_sessions,      # Total session in the current year
            'daily_sessions_by_month': daily_sessions_by_month   # Sessions per day within each month
        }

        return result
    
    except Exception as e:
        logger.error(f"Error processing files: {e}")
        return {'error': str(e)}

def summarize_allusers_data(run_stage, data):
    try:
        # Extract required metrics from the raw data
        data = extracted_needed_metrics(data)  
        user_summary = defaultdict(list)  # Dictionary to group records by user_profile_id

        # Group records by user_profile_id
        for record in data:
            user_profile_id = record.get('user_profile_id')
            if user_profile_id is not None:
                user_summary[user_profile_id].append(record)

        trainees_detailed_data = []

        # Process each user_profile_id group
        for user_profile_id, records in user_summary.items():
            job_profile_ids = set()
            challenge_ids = set()
            template_ids = set()
            complete_sessions_count = 0
            incomplete_sessions_count = 0
            total_interview_score = 0
            total_interviews_count = 0

            # Aggregating data for each user
            for record in records:
                job_profile_id = record.get('job_profile_id')
                challenge_id = record.get('challenge_id')
                if job_profile_id:
                    job_profile_ids.add(job_profile_id)

                if challenge_id:
                    challenge_ids.add(challenge_id)

                template_id = record.get('template_id')
                if template_id:
                    template_ids.add(template_id)

                if record.get('complete_status') is True:
                    complete_sessions_count += 1
                else:
                    incomplete_sessions_count += 1

                # Uncomment this line if 'overall_performance_score' exists and is used
                # if record.get('overall_performance_score') is not None:
                #     total_interview_score += record['overall_performance_score']

                total_interviews_count += 1

            # Fetch user details from other services
            ipersona_user = IpersonaTraineeSchema(run_stage=run_stage)
            all_user_data = ipersona_user.get_trainee_by_id(user_profile_id=user_profile_id, nopp=True, dataframe=False, return_object=True)
            all_user_id = all_user_data.get('attributes', {}).get('all_users', {}).get('data', [{}])[0].get('id')

            # Fetching data from other services using all_user_id
            ipersona_alluser = IpersonaAllUserSchema(run_stage=run_stage)
            ipersona_alluser_data = ipersona_alluser.get_alluser_by_id(all_user_id=all_user_id, nopp=True, dataframe=False, return_object=True)

            ipersona_profile = IpersonaProfileInformationSchema()
            ipersona_profile_data = ipersona_profile.filter_by_all_user_id(all_user_id=all_user_id, nopp=True, dataframe=False, return_object=True)

            # Merge all user data if available
            userdata = {**(ipersona_alluser_data or {}), **(ipersona_profile_data or {})}

            # Prepare the result for this user
            trainees_detailed_data.append({
                "user_profile_id": user_profile_id,
                "all_user_id": all_user_id,
                "name": userdata.get('name', 'Unknown'),
                "role": userdata.get('role', 'Unknown'),
                "batch": userdata.get('Batch', 'Unknown'),
                "gender": userdata.get('gender', 'Unknown'),
                "nationality": userdata.get('nationality', 'Unknown'),
                "job_count": len(job_profile_ids),
                "challenge_count": len(challenge_ids),
                "template_count": len(template_ids),
                "total_interviews_count": total_interviews_count,
                "complete_sessions_count": complete_sessions_count,
                "incomplete_sessions_count": incomplete_sessions_count,
            })

        # Sort the data by 'total_interviews_count' and return top 10
        top_10 = sorted(trainees_detailed_data, key=lambda x: x['total_interviews_count'], reverse=True)[:10]

        result = {
            "alldata": trainees_detailed_data,  # All processed user data
            "top10": top_10  # Top 10 users by total interviews count
        }
        return result

    except Exception as e:
        logger.error(f"Error processing files: {e}")
        return {'error': str(e)}

def summarize_alljobs_data(run_stage, data):
    try:
        data = extracted_needed_metrics(data) 
        # Only keep records with a valid job_profile_id
        valid_records = [record for record in data if record.get('job_profile_id') not in (None, 0)]
        job_summary = defaultdict(list)  # Group records by job_profile_id

        for record in valid_records:
            job_profile_id = record['job_profile_id']
            job_summary[job_profile_id].append(record)

        trainees_detailed_data = []
        processed_jobs = set()  # Keep track of processed job_profile_ids to avoid duplication

        for job_profile_id, records in job_summary.items():
            # Skip if this job profile_id has already been processed
            if job_profile_id in processed_jobs:
                continue

            complete_sessions_count = 0
            incomplete_sessions_count = 0
            total_interviews_count = len(records)  # Total number of interviews for this job

            # Aggregate session counts for the job
            for record in records:
                if record.get('complete_status') is True:
                    complete_sessions_count += 1
                else:
                    incomplete_sessions_count += 1

            # Fetch job-related data (title, company, location, URL)
            ipersona_job = IpersonaJobSchema(run_stage=run_stage)
            job_title_data = ipersona_job.filter_by_job_id(job_profile_id=job_profile_id, nopp=True, dataframe=False)

            # Gather job info (title, company, location, URL)
            job_title = job_title_data[0]['attributes']['attributes'].get('title', 'Unknown Job Title') if job_title_data else 'Unknown Job Title'
            company_name = job_title_data[0]['attributes']['attributes'].get('company_name', '') if job_title_data else ''
            location = job_title_data[0]['attributes']['attributes'].get('location', '') if job_title_data else ''
            url = job_title_data[0]['attributes']['attributes'].get('url', '') if job_title_data else ''

            # Add the aggregated job data to the result (only once per job profile)
            trainees_detailed_data.append({
                "job_profile_id": job_profile_id,
                "job_title": job_title,
                "total_interviews_count": total_interviews_count,
                "complete_sessions_count": complete_sessions_count,
                "incomplete_sessions_count": incomplete_sessions_count,
                "company_name": company_name,
                "location": location,
                "url": url
            })

            # Mark this job profile as processed
            processed_jobs.add(job_profile_id)

        # Sorting jobs by total number of interviews in descending order and selecting top 10
        top_10_jobs = sorted(trainees_detailed_data, key=lambda x: x['total_interviews_count'], reverse=True)[:10]

        result = {
            "alldata": trainees_detailed_data,  # All processed job data
            "top10": top_10_jobs  # Top 10 jobs by total interviews
        }
        return result

    except Exception as e:
        logger.error(f"Error processing files: {e}")
        return {'error': str(e)}

def summarize_allchallenges_data(run_stage, data):
    try:
        data = extracted_needed_metrics(data)
        # Only keep records with a valid challenge_id
        valid_records = [record for record in data if record.get('challenge_id') not in (None, 0)]
        challenge_summary = defaultdict(list)  # Group records by challenge_id

        for record in valid_records:
            challenge_id = record['challenge_id']
            challenge_summary[challenge_id].append(record)

        challenges_detailed_data = []
        processed_challenges = set()  # Keep track of processed challenge_ids to avoid duplication

        for challenge_id, records in challenge_summary.items():
            # Skip if this challenge_id has already been processed
            if challenge_id in processed_challenges:
                continue

            complete_sessions_count = 0
            incomplete_sessions_count = 0
            total_interviews_count = len(records)  # Total number of interviews for this challenge

            # Aggregate session counts for the challenge
            for record in records:
                if record.get('complete_status') is True:
                    complete_sessions_count += 1
                else:
                    incomplete_sessions_count += 1

            # Fetch challenge-related data (title, etc.)
            ipersona_challenge = IpersonaChallengeDocumentSchema(run_stage=run_stage)
            challenge_data = ipersona_challenge.get_challenge_by_id(
                challengeId=challenge_id, nopp=True, dataframe=False
            )

            challenge_title = challenge_data.get('attributes', {}).get('Title', 'Unknown Challenge Title') if challenge_data else 'Unknown Challenge Title'

            # Add the aggregated challenge data to the result (only once per challenge_id)
            challenges_detailed_data.append({
                "challenge_id": challenge_id,
                "challenge_title": challenge_title,
                "total_interviews_count": total_interviews_count,
                "complete_sessions_count": complete_sessions_count,
                "incomplete_sessions_count": incomplete_sessions_count,
            })

            # Mark this challenge_id as processed
            processed_challenges.add(challenge_id)

        # Sorting challenges by total number of interviews in descending order and selecting top 10
        top_10_challenges = sorted(challenges_detailed_data, key=lambda x: x['total_interviews_count'], reverse=True)[:10]

        result = {
            "alldata": challenges_detailed_data,  # All processed challenge data
            "top10": top_10_challenges  # Top 10 challenges by total interviews
        }
        return result

    except Exception as e:
        logger.error(f"Error processing files: {e}")
        return {'error': str(e)}
    
def summarize_eacholdjob_data(run_stage, data):
    try:
        data = extracted_needed_metrics(data)  
        job_summary = defaultdict(list)

        for record in data:
            job_profile_id = record['job_profile_id']
            job_summary[job_profile_id].append(record)
        
        trainees_detailed_data = []
        processed_users = {}  # Dictionary to store user_profile_id and trainee_name mapping

        for job_profile_id, records in job_summary.items():
            complete_sessions_count = 0
            incomplete_sessions_count = 0
            total_interviews_count = len(records)
            trainee_name = ''
            user_profile_id = records[0].get('user_profile_id')

            # Fetch trainee info if not already processed
            if user_profile_id not in processed_users:
                ipersona_user = IpersonaTraineeSchema(run_stage=run_stage)
                all_user_data = ipersona_user.get_trainee_by_id(user_profile_id=user_profile_id, nopp=True, dataframe=False, return_object=True)
                all_user_id = all_user_data.get('attributes', {}).get('all_users', {}).get('data', [{}])[0].get('id')

                # Fetch additional data about the trainee
                ipersona_alluser = IpersonaAllUserSchema(run_stage=run_stage)
                ipersona_alluser_data = ipersona_alluser.get_alluser_by_id(all_user_id=all_user_id, nopp=True, dataframe=False, return_object=True)
                trainee_name = ipersona_alluser_data.get('name', 'Unknown')

                # Store trainee_name to avoid fetching again for the same user
                processed_users[user_profile_id] = trainee_name
            else:
                trainee_name = processed_users[user_profile_id]

            # Aggregate session counts for the job
            for record in records:
                if record.get('complete_status') is True:
                    complete_sessions_count += 1
                else:
                    incomplete_sessions_count += 1

            # Fetch job-related data (title, company, location, URL)
            ipersona_job = IpersonaJobSchema(run_stage=run_stage)
            job_title_data = ipersona_job.filter_by_job_id(job_profile_id=job_profile_id, nopp=True, dataframe=False)

            # Gather job info (title, company, location, URL)
            job_title = job_title_data[0]['attributes']['attributes'].get('title', 'Unknown Job Title') if job_title_data else 'Unknown Job Title'
            company_name = job_title_data[0]['attributes']['attributes'].get('company_name', '') if job_title_data else ''
            location = job_title_data[0]['attributes']['attributes'].get('location', '') if job_title_data else ''
            url = job_title_data[0]['attributes']['attributes'].get('url', '') if job_title_data else ''
            
            # Append the summarized data
            trainees_detailed_data.append({
                'trainee_name': trainee_name,
                'total_interview_count': total_interviews_count,
                'complete_sessions_count': complete_sessions_count,
                'incomplete_sessions_count': incomplete_sessions_count,
                'job_title': job_title,
                'company_name': company_name,
                'location': location,
                'url': url,
                'user_profile_id': user_profile_id,
                'job_profile_id': job_profile_id
            })
        
        return trainees_detailed_data
    
    except Exception as e:
        logger.error(f"Error processing files: {e}")
        return {'error': str(e)}

def summarize_eachjob_data(run_stage, data):
    try:
        data = extracted_needed_metrics(data)
        # Only keep records with a valid job_profile_id
        valid_records = [record for record in data if record.get('job_profile_id') not in (None, 0)]
        job_summary = defaultdict(list)

        # Group records by job_profile_id
        for record in valid_records:
            job_profile_id = record['job_profile_id']
            job_summary[job_profile_id].append(record)
        
        jobs_detailed_data = {}
        processed_users = {}  # Dictionary to store user_profile_id and trainee_name mapping

        for job_profile_id, records in job_summary.items():
            job_trainees = []  # List to hold unique trainee details for the current job
            seen_trainees = set()  # Keep track of user_profile_id's already processed for this job

            for record in records:
                user_profile_id = record.get('user_profile_id')

                # Only process if the trainee hasn't already been added for this job
                if user_profile_id not in seen_trainees:
                    complete_sessions_count = 0
                    incomplete_sessions_count = 0
                    total_interviews_count = 0
                    total_score = 0
                    score_count = 0
                    trainee_name = ''
                    individual_scores = []  # List to store all individual scores

                    # Fetch trainee info if not already processed globally
                    if user_profile_id not in processed_users:
                        ipersona_user = IpersonaTraineeSchema(run_stage=run_stage)
                        all_user_data = ipersona_user.get_trainee_by_id(
                            user_profile_id=user_profile_id, nopp=True, dataframe=False, return_object=True)
                        all_user_id = all_user_data.get('attributes', {}).get('all_users', {}).get('data', [{}])[0].get('id')
                        
                        # Fetch additional data about the trainee
                        ipersona_alluser = IpersonaAllUserSchema(run_stage=run_stage)
                        ipersona_alluser_data = ipersona_alluser.get_alluser_by_id(
                            all_user_id=all_user_id, nopp=True, dataframe=False, return_object=True)
                        trainee_name = ipersona_alluser_data.get('name', 'Unknown')

                        # Store trainee_name to avoid fetching again for the same user
                        processed_users[user_profile_id] = trainee_name
                    else:
                        trainee_name = processed_users[user_profile_id]

                    # Calculate session counts, score, and gather individual scores for the current job and user
                    for session in records:
                        if session.get('user_profile_id') == user_profile_id:
                            total_interviews_count += 1
                            if session.get('complete_status') is True:
                                complete_sessions_count += 1
                            else:
                                incomplete_sessions_count += 1
                            
                            # Accumulate performance score if available and store individual score
                            score = session.get('overall_performance_score')
                            if score is not None:
                                total_score += score
                                score_count += 1
                                individual_scores.append(score)  # Add the score to the list

                    # Calculate average score for the trainee
                    if score_count > 0:
                        average_score = round(total_score / score_count, 2)
                    else:
                        average_score = "N/A"

                    # Add the trainee details to the list for this job
                    job_trainees.append({
                        'trainee_name': trainee_name,
                        'total_interview_count': total_interviews_count,
                        'complete_sessions_count': complete_sessions_count,
                        'incomplete_sessions_count': incomplete_sessions_count,
                        'individual_scores': individual_scores,  # Include list of individual scores
                        'average_score': average_score,  # Include average score
                        'user_profile_id': user_profile_id
                    })

                    # Mark this user_profile_id as processed for this job
                    seen_trainees.add(user_profile_id)

            # Fetch job-related data (title, company, location, URL)
            ipersona_job = IpersonaJobSchema(run_stage=run_stage)
            job_title_data = ipersona_job.filter_by_job_id(
                job_profile_id=job_profile_id, nopp=True, dataframe=False)

            # Gather job info (title, company, location, URL)
            job_title = job_title_data[0]['attributes']['attributes'].get('title', 'Unknown Job Title') if job_title_data else 'Unknown Job Title'
            company_name = job_title_data[0]['attributes']['attributes'].get('company_name', '') if job_title_data else ''
            location = job_title_data[0]['attributes']['attributes'].get('location', '') if job_title_data else ''
            url = job_title_data[0]['attributes']['attributes'].get('url', '') if job_title_data else ''

            # Store the job data with unique trainees
            jobs_detailed_data = {
                'job_profile_id':  job_profile_id,
                'job_title': job_title,
                'company_name': company_name,
                'location': location,
                'url': url,
                'trainees': job_trainees  # Attach list of unique trainees under the job
            }
        total = len(job_trainees)
        return jobs_detailed_data, total
    
    except Exception as e:
        logger.error(f"Error processing files: {e}")
        return {'error': str(e)}

def summarize_eachchallenge_data(run_stage, data):
    try:
        data = extracted_needed_metrics(data)
        # Only keep records with a valid challenge_id
        valid_records = [record for record in data if record.get('challenge_id') not in (None, 0)]
        challenge_summary = defaultdict(list)

        # Group records by challenge_id
        for record in valid_records:
            challenge_id = record['challenge_id']
            challenge_summary[challenge_id].append(record)
        
        challenges_detailed_data = {}
        processed_users = {}  # Dictionary to store user_profile_id and trainee_name mapping

        for challenge_id, records in challenge_summary.items():
            challenge_trainees = []  # List to hold unique trainee details for the current challenge
            seen_trainees = set()  # Keep track of user_profile_id's already processed for this challenge

            for record in records:
                user_profile_id = record.get('user_profile_id')

                # Only process if the trainee hasn't already been added for this challenge
                if user_profile_id not in seen_trainees:
                    complete_sessions_count = 0
                    incomplete_sessions_count = 0
                    total_interviews_count = 0
                    total_score = 0
                    score_count = 0
                    trainee_name = ''
                    individual_scores = []  # List to store all individual scores

                    # Fetch trainee info if not already processed globally
                    if user_profile_id not in processed_users:
                        ipersona_user = IpersonaTraineeSchema(run_stage=run_stage)
                        all_user_data = ipersona_user.get_trainee_by_id(
                            user_profile_id=user_profile_id, nopp=True, dataframe=False, return_object=True)
                        all_user_id = all_user_data.get('attributes', {}).get('all_users', {}).get('data', [{}])[0].get('id')
                        
                        # Fetch additional data about the trainee
                        ipersona_alluser = IpersonaAllUserSchema(run_stage=run_stage)
                        ipersona_alluser_data = ipersona_alluser.get_alluser_by_id(
                            all_user_id=all_user_id, nopp=True, dataframe=False, return_object=True)
                        trainee_name = ipersona_alluser_data.get('name', 'Unknown')

                        # Store trainee_name to avoid fetching again for the same user
                        processed_users[user_profile_id] = trainee_name
                    else:
                        trainee_name = processed_users[user_profile_id]

                    # Calculate session counts, score, and gather individual scores for the current challenge and user
                    for session in records:
                        if session.get('user_profile_id') == user_profile_id:
                            total_interviews_count += 1
                            if session.get('complete_status') is True:
                                complete_sessions_count += 1
                            else:
                                incomplete_sessions_count += 1
                            
                            # Accumulate performance score if available and store individual score
                            score = session.get('overall_performance_score')
                            if score is not None:
                                total_score += score
                                score_count += 1
                                individual_scores.append(score)  # Add the score to the list

                    # Calculate average score for the trainee
                    if score_count > 0:
                        average_score = round(total_score / score_count, 2)
                    else:
                        average_score = "N/A"

                    # Add the trainee details to the list for this challenge
                    challenge_trainees.append({
                        'trainee_name': trainee_name,
                        'total_interview_count': total_interviews_count,
                        'complete_sessions_count': complete_sessions_count,
                        'incomplete_sessions_count': incomplete_sessions_count,
                        'individual_scores': individual_scores,  # Include list of individual scores
                        'average_score': average_score,  # Include average score
                        'user_profile_id': user_profile_id
                    })

                    # Mark this user_profile_id as processed for this challenge
                    seen_trainees.add(user_profile_id)

            # Fetch challenge-related data (title, etc.)
            ipersona_challenge = IpersonaChallengeDocumentSchema(run_stage=run_stage)
            challenge_data = ipersona_challenge.get_challenge_by_id(
                challengeId=challenge_id, nopp=True, dataframe=False)

            challenge_title = challenge_data.get('attributes', {}).get('Title', 'Unknown Challenge Title') if challenge_data else 'Unknown Challenge Title'

            # Store the challenge data with unique trainees
            challenges_detailed_data = {
                'challenge_id':  challenge_id,
                'challenge_title': challenge_title,
                'trainees': challenge_trainees  # Attach list of unique trainees under the challenge
            }
        total = len(challenge_trainees)
        return challenges_detailed_data, total
    
    except Exception as e:
        logger.error(f"Error processing files: {e}")
        return {'error': str(e)}
    
def summarize_allusers_performance_data(run_stage, data):
    """
    Summarize performance data for all users with comprehensive error handling.
    """
    try:
        if not isinstance(data, list):
            logger.error("Input data is not a list")
            return {'error': "Invalid data format: expected a list"}
            
        if not data:
            logger.warn("Empty data list provided")
            return []
        
        try:
            data = extracted_needed_metrics(data)  # Extract necessary metrics

        except Exception as extract_error:
            logger.error(f"Error extracting metrics: {extract_error}")
            return {'error': f"Failed to extract metrics: {str(extract_error)}"}
        
        user_summary = defaultdict(list)
        user_metrics = []
        
        # Step 1: Group records by user_profile_id
        for record in data:
            if not isinstance(record, dict):
                logger.warn(f"Skipping non-dictionary record: {record}")
                continue
            user_profile_id = record.get('user_profile_id')
            if not user_profile_id:
                logger.warn(f"Skipping record with missing user_profile_id: {record}")
                continue
            user_summary[user_profile_id].append(record)

        # Step 2: Iterate over each user and calculate the average of metrics
        for user_profile_id, records in user_summary.items():
            try:
                # Fetch user details from external data sources (Strapi)
                try:
                    ipersona_user = IpersonaTraineeSchema()
                    all_user_data = ipersona_user.get_trainee_by_id(
                        user_profile_id=user_profile_id, 
                        nopp=True, 
                        dataframe=False, 
                        return_object=True
                    )
                    if not all_user_data:
                        logger.warn(f"No trainee data found for user_profile_id: {user_profile_id}")
                        all_user_data = {}
                    all_users_data = all_user_data.get('attributes', {}).get('all_users', {}).get('data', [{}])
                    if not all_users_data:
                        logger.warn(f"No all_users data found for user_profile_id: {user_profile_id}")
                        continue
                    all_user_id = all_users_data[0].get('id')
                    if not all_user_id:
                        logger.warn(f"Missing all_user_id for user_profile_id: {user_profile_id}")
                        continue
                except Exception as trainee_error:
                    logger.error(f"Error fetching trainee data for user {user_profile_id}: {trainee_error}")
                    continue
                
                # Get all user data
                try:
                    ipersona_alluser = IpersonaAllUserSchema(run_stage=run_stage)
                    ipersona_alluser_data = ipersona_alluser.get_alluser_by_id(
                        all_user_id=all_user_id, 
                        nopp=True, 
                        dataframe=False, 
                        return_object=True
                    )
                    if not ipersona_alluser_data:
                        logger.warn(f"No all user data found for all_user_id: {all_user_id}")
                        ipersona_alluser_data = {}
                except Exception as alluser_error:
                    logger.error(f"Error fetching all user data for all_user_id {all_user_id}: {alluser_error}")
                    ipersona_alluser_data = {}
                
                # Get profile information
                try:
                    ipersona_profile = IpersonaProfileInformationSchema(run_stage=run_stage)
                    ipersona_profile_data = ipersona_profile.filter_by_all_user_id(
                        all_user_id=all_user_id, 
                        nopp=True, 
                        dataframe=False, 
                        return_object=True
                    )
                    if not ipersona_profile_data:
                        logger.warn(f"No profile data found for all_user_id: {all_user_id}")
                        ipersona_profile_data = {}
                except Exception as profile_error:
                    logger.error(f"Error fetching profile data for all_user_id {all_user_id}: {profile_error}")
                    ipersona_profile_data = {}
                
                # Merge user data
                userdata = {**ipersona_alluser_data, **ipersona_profile_data}

                # Step 3: Calculate metrics with error handling
                confidence_values = []
                clarity_values = []
                engagement_values = []

                confidence_mapping = {'poor': 1, 'good': 2, 'excellent': 3}
                clarity_mapping = {'poor': 1, 'good': 2, 'excellent': 3}
                engagement_mapping = {'poor': 1, 'good': 2, 'excellent': 3}

                for item in records:
                    # Confidence
                    conf = item.get('confidence')
                    if conf and conf.lower() in confidence_mapping:
                        confidence_values.append(confidence_mapping[conf.lower()])
                    # Clarity
                    clar = item.get('clarity')
                    if clar and clar.lower() in clarity_mapping:
                        clarity_values.append(clarity_mapping[clar.lower()])
                    # Engagement
                    eng = item.get('engagement')
                    if eng and eng.lower() in engagement_mapping:
                        engagement_values.append(engagement_mapping[eng.lower()])

                avg_confidence = round(sum(confidence_values) / len(confidence_values), 2) if confidence_values else None
                avg_clarity = round(sum(clarity_values) / len(clarity_values), 2) if clarity_values else None
                avg_engagement = round(sum(engagement_values) / len(engagement_values), 2) if engagement_values else None

                user_data = {
                    "user_profile_id": user_profile_id,
                    "all_user_id": all_user_id,
                    "name": userdata.get('name', 'Unknown'),
                    "role": userdata.get('role', 'Unknown'),
                    "batch": userdata.get('Batch', 'Unknown'),
                    "gender": userdata.get('gender', 'Unknown'),
                    "nationality": userdata.get('nationality', 'Unknown'),
                    'metrics': {
                        'average_confidence_level': avg_confidence,
                        'average_clarity_level': avg_clarity,
                        'average_engagement_level': avg_engagement,
                    }
                }
                user_metrics.append(user_data)
            except Exception as user_error:
                logger.error(f"Error processing user {user_profile_id}: {user_error}")
                user_metrics.append({
                    "user_profile_id": user_profile_id,
                    "error": str(user_error),
                    "metrics": {
                        'average_confidence_level': None,
                        'average_clarity_level': None,
                        'average_engagement_level': None,
                    }
                })

        if not user_metrics:
            logger.warn("No valid user metrics were generated")
        return user_metrics

    except Exception as e:
        logger.error(f"Critical error in summarize_allusers_performance_data: {e}")
        return {'error': str(e)}
    
def summarize_interview_by_template_data(run_stage, data, cursor, filter_by_status):
    try:
        data = extracted_needed_metrics(data)
        template_summary = defaultdict(list)

        # Group records by template_id
        for record in data:
            template_id = record['template_id']
            template_summary[template_id].append(record)

        all_trainee_data = []
        processed_users = {}
        # return template_summary, {}
        for template_id, records in template_summary.items():
            ipersona_template = IpersonaTinderTemplateSchema()
            fetched_template = ipersona_template.get_tinder_template_id(
                templateId=template_id,
                return_object=True,
                nopp=True,
                dataframe=False
            )
            template_type = fetched_template.get('attributes', {}).get('type', '')

            # Group records by (tuser_profile_id, job_profile_id, challenge_id)
            user_job_challenge_map = defaultdict(list)
            for record in records:
                key = (
                    record.get('user_profile_id'),
                    record.get('job_profile_id'),
                    record.get('challenge_id')
                )
                user_job_challenge_map[key].append(record)

            for (user_profile_id, job_profile_id, challenge_id), user_records in user_job_challenge_map.items():
                complete_sessions_count = 0
                incomplete_sessions_count = 0
                total_interviews_count = 0
                total_score = 0
                score_count = 0
                individual_scores = []

                # Filter sessions based on completion status
                for session in user_records:
                    is_complete = session.get('complete_status') is True
                    if filter_by_status == "complete" and not is_complete:
                        continue
                    elif filter_by_status == "incomplete" and is_complete:
                        continue

                    total_interviews_count += 1
                    if is_complete:
                        complete_sessions_count += 1
                    else:
                        incomplete_sessions_count += 1

                    score = session.get('overall_performance_score')
                    if score is not None:
                        total_score += score
                        score_count += 1
                        individual_scores.append(score)

                if total_interviews_count == 0:
                    continue  # Skip if nothing matched the filter

                average_score = round(total_score / score_count, 2) if score_count > 0 else "N/A"

                # Fetch trainee info
                if user_profile_id not in processed_users:
                    ipersona_user = IpersonaTraineeSchema(run_stage=run_stage)
                    all_user_data = ipersona_user.get_trainee_by_id(
                        user_profile_id=user_profile_id,
                        nopp=True,
                        dataframe=False,
                        return_object=True
                    )
                    all_user_id = all_user_data.get('attributes', {}).get('all_users', {}).get('data', [{}])[0].get('id')

                    ipersona_alluser = IpersonaAllUserSchema(run_stage=run_stage)
                    ipersona_alluser_data = ipersona_alluser.get_alluser_by_id(
                        all_user_id=all_user_id,
                        nopp=True,
                        dataframe=False,
                        return_object=True
                    )
                    trainee_name = ipersona_alluser_data.get('name', 'Unknown')
                    trainee_email = ipersona_alluser_data.get('email', 'Unknown')

                    processed_users[user_profile_id] = (trainee_name, trainee_email)
                else:
                    trainee_name, trainee_email = processed_users[user_profile_id]

                # Fetch job or challenge title
                extracted_title = 'Unknown Job Title'
                company_name = ''
                if job_profile_id:
                    template_tag = 'job'
                    ipersona_job = IpersonaJobSchema(run_stage=run_stage)
                    job_title_data = ipersona_job.filter_by_job_id(
                        job_profile_id=job_profile_id,
                        nopp=True,
                        dataframe=False
                    )
                    if job_title_data:
                        job_attrs = job_title_data[0]['attributes']['attributes']
                        extracted_title = job_attrs.get('title', 'Unknown Job Title')
                        company_name = job_attrs.get('company_name', '')

                elif challenge_id:
                    template_tag = 'challenge'
                    ipersona_challenge = IpersonaChallengeDocumentSchema()
                    challenge_data = ipersona_challenge.get_challenge_by_id(
                        challengeId=challenge_id,
                        nopp=True,
                        dataframe=False
                    )
                    if challenge_data:
                        extracted_title = challenge_data['attributes'].get('Title', 'Unknown Job Title')

                all_trainee_data.append({
                    'trainee_name': trainee_name,
                    'email': trainee_email,
                    'title': extracted_title,
                    'company_name': company_name,
                    'average_score': average_score,
                    'total_interview_count': total_interviews_count,
                    'complete_sessions_count': complete_sessions_count,
                    'incomplete_sessions_count': incomplete_sessions_count,
                    'tag': template_tag,
                    'template_id': template_id,
                    'user_profile_id': user_profile_id,
                    'job_profile_id': job_profile_id,
                    'challenge_id': challenge_id
                })

        cursor['total'] = len(all_trainee_data)
        return all_trainee_data, cursor

    except Exception as e:
        logger.error(f"Error processing files: {e}")
        return {'error': str(e)}


#-------------------------------------------- FIle reader --------------------------------------------
def parse_iso_format_with_z(iso_str):
    # Gracefully handle missing/empty timestamps
    if not iso_str or (isinstance(iso_str, str) and iso_str.strip() == ""):
        return None
    return datetime.strptime(iso_str, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)

def convert_iso_to_readable_format(iso_time):
    # If time is not provided, return a friendly placeholder instead of raising
    if not iso_time or (isinstance(iso_time, str) and iso_time.strip() == ""):
        return "time not provided"
    try:
        dt = datetime.strptime(iso_time, '%Y-%m-%dT%H:%M:%S.%fZ')    
        readable_time = dt.strftime('%d %b %Y %I:%M %p')
        return readable_time
    except Exception as e:
        logger.warning(f"Time parse failed, returning placeholder: {e}")
        return "time not provided"

def file_reader(path: str) -> str:
    """ File Reader """
    try:       
        fname = os.path.join(path)
        with open(fname, 'r') as f:
            system_message = f.read()
        return system_message
    
    except Exception as e:
        logger.error(f"File reading process failed: {str(e)}")
        return f'Error: {str(e)}'  

def remove_key(data, key_to_remove):
    if isinstance(data, dict):
        if key_to_remove in data and isinstance(data[key_to_remove], dict):
            del data[key_to_remove]
        for key, value in data.items():
            remove_key(value, key_to_remove)
    elif isinstance(data, list):
        for item in data:
            remove_key(item, key_to_remove)
    return data   

#------------------------------------- Json Extraction --------------------------------------------
def extract_json(response, quite=False):
    try:   
        """ Json Extraction """ 
        if isinstance(response, (dict, list)):
            # return as it is 
            # if not quite: print("extract_json", "response is already in json format")
            return response       
        elif isinstance(response, str):
            # Method 1
            try:
                # try simple to load it as jsonfrom collections import defaultdict

                res = json.loads(response)
                # if not quite: print("extract_json", "response is already in jsons format")
                return res
            except:
                pass
                # if not quite: print("extract_json: simple json load failed. Trying to fix json string ...")
            
            # Method 2 
            try:
                # if not quite: print("extract_json", "response is not in json format. Trying to extract json from response")
                if '```json' in text:                
                    out = text.split('```json')[1].split('```')[0].replace('\n','')
                elif '```' in text:
                    out = text.split('```')[1].split('```')[0].replace('\n','')
                else:
                    out = text

                res = json.loads(out)
                return res        
            except Exception as e:
                # if not quite: print(f"extract_json: unable to fix json string. Trying with json_repair ...")
                pass         
                # it is not in json string format
                
                # Method 3
                text = response
                try:                
                    res = json_repair.loads(text)
                    if isinstance(res, (dict, list)):
                        # if not quite: print("extract_json: result obtained using repair json")
                        return res
                except:
                    if not quite: print("extract_json: unable to repair json string using json_repair. Raise exception")
                    raise
        else:
            # if not quite: print("extract_json", "response is not a string or a dictionary")
            return {}
        
    except Exception as e:
        logger.error(f"Error processing files: {e}")
        return {'error': str(e)}
    
#------------------------------------------- Create Session -------------------------------------------------
async def create_session_logics(
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
        tinder_user_profile_data):
    try:
        upload_metadata = None
        if template:
            message = ''
            saved_session = create_session(
                run_stage, 
                mode,
                template, 
                external, 
                challenge, 
                all_user_id,
                tinder_user_profile_id, 
                job_profile_id,
                template_id, 
                challenge_id, 
                message,
                upload_metadata
            )

            saved_session = {
                'id': saved_session.get('id'),
                "status": saved_session.get('attributes', {}).get('status'),
                "user_profile_id": safe_get_id(saved_session, 'attributes', 'tinder_user_profile', 'data'),
                "job_profile_id": safe_get_id(saved_session, 'attributes', 'tinder_job_profile', 'data'),
                "template_id": safe_get_id(saved_session, 'attributes', 'tinder_template', 'data'),
                "challenge_id": safe_get_id(saved_session, 'attributes', 'challenge_document', 'data')
            }

            session_id = [saved_session.get('id')]
            attach_session_id_to_a_template(template_id, session_id)

            return saved_session

        elif challenge:
            type = 'challenge_interview_config'
            response_obj = fetch_the_structure(type)
            challenge_data = await analysis_challenge(challenge_id)

            if response_obj is False:
                tag = 'parrot_challenge_question_generation_default'
                challenge_prompt = read_prompt_data_for_challenge_default(
                    challenge_data, type, tag
                )
            else:
                tag = 'parrot_challenge_question_generation'
                section_count = response_obj.get('section_count', {})
                json_format = response_obj.get('json_format', {})
                challenge_prompt = read_prompt_data_for_challenge(
                    json_format, 
                    section_count, 
                    challenge_data, 
                    type, 
                    tag
                )

            saved_session = create_session(
                run_stage, 
                mode,
                template, 
                external, 
                challenge, 
                all_user_id,
                tinder_user_profile_id, 
                job_profile_id,
                template_id, 
                challenge_id, 
                challenge_prompt,
                upload_metadata
            )

            saved_session = {
                'id': saved_session.get('id'),
                "status": saved_session.get('attributes', {}).get('status'),
                "user_profile_id": safe_get_id(saved_session, 'attributes', 'tinder_user_profile', 'data'),
                "job_profile_id": safe_get_id(saved_session, 'attributes', 'tinder_job_profile', 'data'),
                "template_id": safe_get_id(saved_session, 'attributes', 'tinder_template', 'data'),
                "challenge_id": safe_get_id(saved_session, 'attributes', 'challenge_document', 'data')
            }

            return saved_session

        else:
            type = 'job_interview_config'
            response_obj = fetch_the_structure(type)

            if response_obj is False:
                tag = 'parrot_question_generator_default'
                persona_tag = 'parrot_persona'
                generated_persona = read_prompt_persona(
                    tinder_job_data, 
                    tinder_user_profile_data, 
                    type, 
                    persona_tag
                )
                msg = read_prompt_data_for_default(type, tag)
            else:
                section_count = response_obj.get('section_count', {})
                json_format = response_obj.get('json_format', {})
                tag = 'parrot_generate_question'
                persona_tag = 'parrot_persona'
                generated_persona = read_prompt_persona(
                    tinder_job_data, 
                    tinder_user_profile_data, 
                    type,
                    persona_tag
                )
                msg = read_generate_question_prompt(
                    json_format, 
                    section_count, 
                    context='', 
                    tag=tag, 
                    type=type
                )

            content = generated_persona + msg
            response = gpt.openai_gpt_assistant_without_streaming(content)

            if not response:
                logger.error("Failed to generate questions: Empty AI response")
                return JSONResponse(
                    status_code=500,
                    content={"error": "Failed to generate interview questions"}
                )

            generated_question_json = extract_json(response, quite=False)
            generated_question_json = add_question_number(generated_question_json)
            logger.info("Persona and questions generated successfully")

            # Convert all ID fields to integers if they're valid numbers
            job_profile_id_value = convert_id_to_int(job_profile_id)
            user_profile_id_value = convert_id_to_int(tinder_user_profile_id)
            template_id_value = convert_id_to_int(template_id)
            challenge_id_value = convert_id_to_int(challenge_id)
            
            session_data = {
                "slug": f"all_user_id: {all_user_id}",
                "status": "Incomplete",
                "attributes": {
                    "persona": generated_persona,
                    "generated_questions": generated_question_json
                },
                "metadata": {
                    "mode": mode,
                    "template": False,
                    "generate": True,
                    "external": False,
                    "challenge": False,
                }
            }
            
            # Only include ID fields if they're valid
            if user_profile_id_value is not None:
                session_data["tinder_user_profile_id"] = user_profile_id_value
            if job_profile_id_value is not None:
                session_data["tinder_job_profile_id"] = job_profile_id_value
            if template_id_value is not None:
                session_data["tinder_template"] = template_id_value
            if challenge_id_value is not None:
                session_data["challenge_document"] = challenge_id_value

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

            saved_session = {
                'id': saved_session.get('id'),
                "status": saved_session.get('attributes', {}).get('status'),
                "user_profile_id": safe_get_id(saved_session, 'attributes', 'tinder_user_profile', 'data'),
                "job_profile_id": safe_get_id(saved_session, 'attributes', 'tinder_job_profile', 'data'),
                "template_id": safe_get_id(saved_session, 'attributes', 'tinder_template', 'data'),
                "challenge_id": safe_get_id(saved_session, 'attributes', 'challenge_document', 'data')
            }

            return saved_session

    except Exception as e:
        logger.error(f"Error processing files: {e}")
        return {'error': str(e)}

def convert_id_to_int(id_value):
    """Convert ID value to integer if it's a valid number, otherwise return None"""
    if id_value is not None and str(id_value).strip():
        try:
            return int(id_value)
        except (ValueError, TypeError):
            return None
    return None

def create_session(
        run_stage, 
        mode,
        template, 
        external, 
        challenge, 
        all_user_id, 
        user_profile_id, 
        job_profile_id, 
        template_id, 
        challenge_id,
        message,
        upload_metadata):
    try:  
        challenge_generated_questions = None
        if template:
            metadata =  {
                "mode": mode,
                "template": True,
                "generate": False,
                "external": False,
                "challenge": False
            }
            status = "Incomplete"
        elif external:
            metadata =  {
                "mode": mode,
                "template": False,
                "generate": False,
                "external": True,
                "challenge": False,
                "upload_metadata": upload_metadata
            }
            status = "External"
        elif challenge:
            metadata =  {
                "mode": mode,
                "template": False,
                "generate": False,
                "external": False,
                "challenge": True
            }
            status = "Incomplete"
            
            response = gpt.openai_gpt_assistant_without_streaming(message)

            if not response:
                logger.error("Failed to generate questions: Empty AI response")
                return {
                    "status_code": 500,
                    "error": "Failed to generate interview questions"
                }
                
            challenge_generated_questions = extract_json(response, quite=False)
            logger.info("Persona and questions generated successfully")
            

            # Step 4: Add question numbers
            challenge_generated_questions = add_question_number(challenge_generated_questions)
            
        if challenge: 
            print(f"🎯 [DEBUG] Taking CHALLENGE code path - challenge_id: {challenge_id}")
            # Step 5: Save session data
            # Convert all ID fields to integers if they're valid numbers
            job_profile_id_value = convert_id_to_int(job_profile_id)
            user_profile_id_value = convert_id_to_int(user_profile_id)
            template_id_value = convert_id_to_int(template_id)
            challenge_id_value = convert_id_to_int(challenge_id)
            
            session_data = {
                "slug": str(f"all_user_id: {all_user_id}"),
                "status": "Incomplete",
                "attributes": {
                    "challenge_questions": challenge_generated_questions
                },
                "metadata": {
                    "mode": mode,
                    "template": False,
                    "generate": False,
                    "external": False,
                    "challenge": True
                }
            }
            
            # Only include ID fields if they're valid
            if user_profile_id_value is not None:
                session_data["tinder_user_profile_id"] = user_profile_id_value
            if job_profile_id_value is not None:
                session_data["tinder_job_profile_id"] = job_profile_id_value
            if template_id_value is not None:
                session_data["tinder_template"] = template_id_value
            if challenge_id_value is not None:
                session_data["challenge_document"] = challenge_id_value
            
        else:
            # Convert all ID fields to integers if they're valid numbers
            job_profile_id_value = convert_id_to_int(job_profile_id)
            user_profile_id_value = convert_id_to_int(user_profile_id)
            template_id_value = convert_id_to_int(template_id)
            challenge_id_value = convert_id_to_int(challenge_id)
            attr = {}
            if external == True:
                attr = {
                        "external": external
                      }
            else:
                attr = {
                        "template_id": template_id,
                        "asked_question_numbers": []
                      }
            session_data = {
                    "slug": str(f"all_user_id: {all_user_id}"),
                    "status": status,
                    "attributes": attr,
                    "metadata": metadata
                }
            
            # Only include ID fields if they're valid
            if user_profile_id_value is not None:
                session_data["tinder_user_profile_id"] = user_profile_id_value
            if job_profile_id_value is not None:
                session_data["tinder_job_profile_id"] = job_profile_id_value
            if template_id_value is not None:
                session_data["tinder_template"] = template_id_value
            if challenge_id_value is not None:
                session_data["challenge_document"] = challenge_id_value
            
            print(f"📋 [DEBUG] Final session data: {session_data}")

         
        ipersona_session = IpersonaSessionSchema(run_stage=run_stage)
        saved_session = ipersona_session.save_session(
            params=session_data, 
            return_object=True, 
            nopp=True, 
            dataframe=False
        )

        if not saved_session:
            logger.error("Failed to save session")
            return {
                "status_code": 500,
                "content": {"error": "Failed to save session data"}
            }
            
        logger.info(f"Session created successfully with ID: {saved_session.get('id', 'unknown')}")
        
        # Remove large questions data before returning
        return saved_session
    
    except Exception as e:
        logger.error(f"Error processing files: {e}")
        return {'error': str(e)}  


def safe_get_id(data, *keys):
    """Safely traverse nested dicts and return the final 'id' if available, else None."""
    for key in keys:
        if not isinstance(data, dict):
            return None
        data = data.get(key)
    return data.get('id') if isinstance(data, dict) else None


async def analysis_challenge(challenge_id):
    try:
        ipersona_challenge = AsyncTaskAnalyzer()
        content = ipersona_challenge.get_task_document(challenge_id)
        if content:
            content = ipersona_challenge.clean_content(content)
            result = await ipersona_challenge.analyze_sections(content)
            return result
        else:
            return False
    
    except Exception as e:
        logger.error(f"Error processing files: {e}")
        return {'error': str(e)}  
    

def get_session_data(session_json):
    try:
        all_sessions = []

        # Case 1: session_json is a list (like your example)
        if isinstance(session_json, list):
            for item in session_json:
                if isinstance(item, dict) and 'data' in item:
                    all_sessions.append(item['data'])

        # Case 2: session_json is a single dict with 'data' key
        elif isinstance(session_json, dict) and 'data' in session_json:
            all_sessions = [session_json['data']]

        if all_sessions:
            return all_sessions[0]

        logger.warning("No session data found in the session JSON.")
        return None

    except Exception as e:
        logger.error(f"Error extracting session data from session JSON: {str(e)}")
        return {'error': f"Error extracting session data from session JSON: {str(e)}"}

#------------------------------------------- Extraction Function --------------------------------------------
def extract_trainee_neccessary_values(data):
    try:
        extracted_values = {
            "basics.attributes": [],
            "projects.attributes": [],
            "education.attributes": [],
            "work_experience.attributes": []
        }

        if isinstance(data, list):
            for item in data:  
                attributes = item.get('attributes', {}).get('attributes', {})

                if 'basics' in attributes:
                    lists = attributes['basics'].get('attributes', [])
                    if isinstance(lists, list): 
                        for x in lists:
                            extracted_values["basics.attributes"].append({
                                "role": x.get("role", ""),
                                "personal_statement": x.get("personal_statement", "")
                            })
                
                if 'projects' in attributes:
                    lists = attributes['projects'].get('attributes', [])
                    if isinstance(lists, list): 
                        for x in lists:
                            extracted_values["projects.attributes"].append({
                                "title": x.get("title", ""),
                                "summary": x.get("summary", "")
                            })
                
                if 'education' in attributes:
                    lists = attributes['education'].get('attributes', [])
                    if isinstance(lists, list): 
                        for x in lists:
                            extracted_values["education.attributes"].append({
                                "study_area": x.get("study_area", ""),
                                "study_type": x.get("study_type", ""),
                                "institution_name": x.get("institution_name", ""),
                                "start_date": x.get("start_date", ""),
                                "end_date": x.get("end_date", "")
                            })
                
                if 'work_experience' in attributes:
                    lists = attributes['work_experience'].get('attributes', [])
                    if isinstance(lists, list):  
                        for x in lists:
                            extracted_values["work_experience.attributes"].append({
                                "role": x.get("role", ""),
                                "company": x.get("company", ""),
                                "summary": x.get("summary", ""),
                                "start_date": x.get("start_date", ""),
                                "end_date": x.get("end_date", "")
                            })
   
        return extracted_values  
    
    except Exception as e:
        logger.error(f"Error processing files: {e}")
        return {'error': str(e)}  

def extract_job_neccessary_values(data):
    try:
        extracted_values = {
            "role": "",  
            "purpose": "", 
            "required_qualifications": "",  
            "duties_responsibilities": "",  
            "attributes.apply_link": "",  
            "competencies": []  
        }

        if isinstance(data, list):
            for item in data:  
                attributes = item.get('attributes', {}).get('attributes', {})
                
                extracted_values["role"] = attributes.get("title", "")

                extracted_values["purpose"] = attributes.get("purpose", "")

                extracted_values["required_qualifications"] = ", ".join(attributes.get("required_qualifications", []))

                extracted_values["duties_responsibilities"] = ", ".join(attributes.get("duties_responsibilities", []))

                competencies = attributes.get("competencies", [])
                for competency in competencies:
                    extracted_values["competencies"].append({
                        "name": competency.get("name", ""),
                        "skills": competency.get("skills", []),
                        "summary": competency.get("summary", "")
                    })

        return extracted_values

    except Exception as e:
        logger.error(f"Error processing files: {e}")
        return {'error': str(e)}

def updating_session_mode(sessionId, mode, run_stage):
    try:
        ipersona_session = IpersonaSessionSchema(run_stage=run_stage)
        session_metadata = ipersona_session.get_by_id(
            sessionId=sessionId, 
            nopp=True, 
            dataframe=False
        )
        session_metadata = session_metadata.get("metadata", {})
        session_metadata["mode"] = mode
        session_data = {
            "i_persona_session_id": sessionId, 
            "metadata": session_metadata,
        }
        updated_session = ipersona_session.update_session(
            params=session_data, 
            nopp=True, 
            dataframe=False, 
            return_object=True)
     
        if updated_session:
            logger.info("session mode updated to closed")

        data = get_session_data(updated_session)  

        response = {
            "id": data.get('id', {}),
            "metadata": data.get('attributes', {}).get('metadata', {}),        
        }

        return response
    
    except Exception as e:
        logger.error(f"Error processing files: {e}")
        return {'error': str(e)}  


def check_if_session_exists(
        run_stage, 
        user_profile_id, 
        job_profile_id, 
        challenge_id, 
        template_id,
        template, 
        external, 
        challenge, 
        generate):
    try:
        ipersona_session = IpersonaSessionSchema(run_stage=run_stage)
        if job_profile_id:
            session_data = ipersona_session.filter_by_with_user_job_id_by_filtering( 
                user_profile_id=user_profile_id,
                job_profile_id=job_profile_id,
                since=10, 
                nopp=True,
                dataframe=False
            )
        elif challenge_id:
            session_data = ipersona_session.filter_by_with_user_challenge_id( 
                user_profile_id=user_profile_id,
                challenge_id=challenge_id,
                since=10, 
                nopp=True,
                dataframe=False
            )
         
        elif template_id:
            session_data = ipersona_session.filter_by_with_user_template_id_by_filtering( 
                user_profile_id=user_profile_id,
                template_id=template_id,
                since=10, 
                nopp=True,
                dataframe=False
            )
        data = extracted_needed_metrics(session_data)
        def extract_session_summary(item):
            return {
                "id": item.get('session_id'),
                "mode": item.get('mode'),
                "status": item.get('complete_status'),
                "job_profile_id": item.get('job_profile_id'),
                "user_profile_id": item.get('user_profile_id'),
                "template_id": item.get('template_id'),
                "challenge_id": item.get('challenge_id'),
                "message": "Session already exists"
            }

        def get_latest_incomplete_session(data):
            for item in data: 
                # Only consider sessions that are truly incomplete (not completed or deleted)
                if item.get("complete_status") == False:  # Explicitly check for False
                    user_id = item.get("user_profile_id")
                    template_id = item.get("template_id")
                    challenge_id = item.get("challenge_id")
                    job_id = item.get("job_profile_id")

                    # Convert to int if stored as strings
                    template_id = int(template_id) if template_id not in [None, "null"] else 0
                    challenge_id = int(challenge_id) if challenge_id not in [None, "null"] else 0
                    job_id = int(job_id) if job_id not in [None, "null"] else 0
                    user_id = int(user_id) if user_id not in [None, "null"] else 0

                    if template:
                        if template_id and user_id and (
                            (challenge_id and challenge_id != 0) or (job_id and job_id != 0)
                        ):
                            return extract_session_summary(item)
                            
                        elif template_id and user_id and job_id == 0 and challenge_id == 0:
                            return extract_session_summary(item)
                    elif generate:
                        if template_id == 0 and user_id and job_id != 0:
                            return extract_session_summary(item)

                    elif challenge:
                        if template_id == 0 and user_id and challenge_id != 0:
                            return extract_session_summary(item)

            return None
    
        return get_latest_incomplete_session(data)  

    except Exception as e:
        logger.error(f"Error processing files: {e}")
        return {'error': str(e)}
  
  
# --------------------------------------------- Helper Functions -------------------------------------------- #
def fetch_the_structure(type):
    try:
        since = 7
        limit = 10
        ipersona_template = IpersonaTinderTemplateSchema()
        templates = ipersona_template.filter_by_type_without_cursor(
                        type=type, 
                        # since=since, 
                        # limit=limit, 
                        nopp=True, 
                        dataframe=False,
                        # **kwargs
                    )
        if templates:
            data = templates[0].get('attributes', {}).get('attributes', {})
            if data:
                section_count = count_section_questions(data)
                json_format = interview_questions_generator_json(data)
                return {
                    "section_count": section_count,
                    "json_format": json_format
                }
            else:
                return False
        else:
            return False
        
    except Exception as e:
        logger.error(f"Error processing files: {e}")
        return {'error': str(e)}
    
def count_section_questions(structure_data):
    try:
        structure = structure_data.get('structure', [])
        section_counts = {}
        
        for section in structure:
            section_type = section.get('sectionType', '')
            num_questions = section.get('numberofquestions', 0)
            section_counts[section_type] = num_questions
        
        return section_counts
    
    except Exception as e:
        logger.error(f"Error processing files: {e}")
        return {'error': str(e)}

def interview_questions_generator_json(structure_data):
    """
    Generate a JSON template for interview questions based on the given structure.
    
    :param structure_data: A dictionary containing the interview section structure
    :return: A list of dictionaries representing interview question sections
    """
    try:
        structure = structure_data.get('structure', [])
        
        interview_questions = []
        
        for section in structure:
            section_type = section.get('sectionType', '')
            num_questions = section.get('numberofquestions', 0)
            
            questions = []
            for i in range(num_questions):
                questions.append({
                    "question": "here you need to put the interview question",
                    "ideal_answer": "Here you put an ideal great answer for the question"
                })
            
            questions.append(f"// add more questions based on the provided count only for {section_type.lower()} interview questions, not more or less the count provided in the structure")
            
            section_dict = {
                "sectionType": section_type,
                "questions": questions
            }
            
            interview_questions.append(section_dict)
        
        return interview_questions

    except Exception as e:
        logger.error(f"Error processing files: {e}")
        return {'error': str(e)}

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

def get_job_data_template_for_multiple_ids(job_profile_ids, run_stage):
    jobs_data = {}
    for job_profile_id in job_profile_ids:
        ipersona_job = IpersonaJobSchema(run_stage=run_stage)
        tinder_job_data = ipersona_job.filter_by_job_id(
            job_profile_id=job_profile_id, nopp=True, dataframe=False
        )

        if not tinder_job_data:
            logger.warn(f"No job data found for job_profile_id: {job_profile_id}")
            jobs_data[f"job_{job_profile_id}"] = {"error": "No job data found for this job_profile_id"}
        else:
            extracted_data = extract_job_neccessary_values(tinder_job_data)
            logger.info(f"Job data extracted for job_profile_id: {job_profile_id}")
            jobs_data[f"job_{job_profile_id}"] = extracted_data

    return jobs_data

async def analyze_multiple_challenges(challenge_ids):
    challenges_data = {}

    for challenge_id in challenge_ids:
        try:
            ipersona_challenge = AsyncTaskAnalyzer()
            content = ipersona_challenge.get_task_document(challenge_id)
            content = ipersona_challenge.clean_content(content)
            result = await ipersona_challenge.analyze_sections(content)

            logger.info(f"Challenge analysis completed for challenge_id: {challenge_id}")
            challenges_data[f"challenge_{challenge_id}"] = result

        except Exception as e:
            logger.error(f"Error processing challenge_id {challenge_id}: {e}")
            challenges_data[f"challenge_{challenge_id}"] = {"error": str(e)}

    return challenges_data

def get_job_data(job_profile_id, run_stage):
    # Step 2: Fetch job profile data
    ipersona_job = IpersonaJobSchema(run_stage=run_stage)
    tinder_job_data = ipersona_job.filter_by_job_id(
        job_profile_id=job_profile_id, nopp=True, dataframe=False
    )

    if not tinder_job_data:
        logger.warn(f"No job data found for job_profile_id: {job_profile_id}")
        return {
            "status_code": 404,
            "content": {"error": "No job data found for the job_profile_id"}
        }

    tinder_job_data = extract_job_neccessary_values(tinder_job_data)
    logger.info(f"Job data extracted for job_profile_id: {job_profile_id}")
    return tinder_job_data

def get_user_data(all_user_id, run_stage):
    # Step 2: Fetch user profile data
    ipersona_user = IpersonaTraineeSchema(run_stage=run_stage)
    trainee_profile_data = ipersona_user.filter_by_alluser_id(
        all_user_id=all_user_id, nopp=True, dataframe=False
    )
    if not trainee_profile_data:
        logger.warn(f"No trainee user profiles found for all_user_id: {all_user_id}")
        return {
            "status_code": 404,
            "content":{"error": "No trainee user profiles found for the given all_user_id"}
        }

    tinder_user_profile_id = trainee_profile_data.get('id')
    if not tinder_user_profile_id:
        return {
            "status_code": 500,
            "content": {"error": "Invalid trainee profile: missing ID"}
        }
    
    tinder_user_profile_data = extract_trainee_neccessary_values(trainee_profile_data)
    logger.info(f"User profile data extracted for user ID: {tinder_user_profile_id}")
    return tinder_user_profile_data, tinder_user_profile_id

def read_prompt_data_for_challenge_default(contents, type, tag):
    if contents:
        content = fetch_config_template(type, tag)
        if content:
            message = content.get('content', '')
            message = message.replace("{challenge_document}", str(contents)) 
            message = message.replace("{count}", str(5))
            challenge_prompt = message

            return challenge_prompt
        else:   
            # Fallback to default challenge generation
            challenge_prompt = fallback.read_prompt_data_for_challenge_default(contents)
            return challenge_prompt
    else:
        return 'Challenge content not found, or challenge ID is invalid'

def read_prompt_data_for_multiple_challenge_default(challenges_data, type, tag):
    content = fetch_config_template(type, tag)
    if content:
        message = content.get('content', '')
        message = message.replace("{challenge_document}", str(challenges_data)) 
        message = message.replace("{count}", str(5))
        challenge_prompt = message
        return challenge_prompt
    
    else:
        # Fallback to default challenge generation
        challenge_prompt = fallback.read_prompt_data_for_challenge_default(challenges_data)
        return challenge_prompt

def read_prompt_data_for_multiple_challenge(
        json_format, 
        count, 
        challenges_data, 
        type, 
        tag):
    content = fetch_config_template(type, tag)
    if content:
        message = content.get('content', '')
        message = message.replace("{challenge_document}", str(challenges_data))
        message = message.replace("{count}", str(count))
        message = message.replace("{json}", str(json_format))
        challenge_prompt = message

        return challenge_prompt
    else:
        # Fallback to default challenge generation
        challenge_prompt = fallback.read_prompt_data_for_challenge(json_format, count)
        return challenge_prompt

async def read_prompt_data_for_challenge(
        json_format, 
        count, 
        contents, 
        type, 
        tag):

    # contents = await analysis_challenge(challenge_id)
    if contents:
        content = fetch_config_template(type, tag)
        if content:
            message = content.get('content', '')
            message = message.replace("{challenge_document}", str(contents))
            message = message.replace("{count}", str(count))
            message = message.replace("{json}", str(json_format))
            challenge_prompt = message

            return challenge_prompt
        else:
            # Fallback to default challenge generation
            # challenge_data = await analysis_challenge(challenge_id)

            challenge_prompt = fallback.read_prompt_data_for_challenge(
                json_format, count, contents
            )
            return challenge_prompt
    else:
        return 'Challenge content not found, or challenge ID is invalid'

def read_prompt_persona(tinder_job_data, tinder_user_profile_data, type, tag):
    content = fetch_config_template(type, tag)
    if content:
        message = content.get('content', '')
        created_persona = create_persona(str(tinder_job_data))
        message = message.replace("{hr_persona}", created_persona) 
        message = message.replace("{job_description}", str(tinder_job_data)) 
        message = message.replace("{profile}", str(tinder_user_profile_data))
        generated_persona = message
        return generated_persona
    else:
        # Fallback to default persona generation
        generated_persona = fallback.read_prompt_persona(tinder_job_data, tinder_user_profile_data)
        return generated_persona

def read_prompt_data_for_default(type, tag):
    content = fetch_config_template(type, tag)
    if content:
        message = content.get('content', '')
        message = message.replace("{introduction_count}", str(1))
        message = message.replace("{background_count}", str(1))
        message = message.replace("{technical_count}", str(1))
        message = message.replace("{behavioral_count}", str(1))
        message = message.replace("{ability_count}", str(1))
        message = message.replace("{closing_count}", str(1))
        msg = message

        return  msg
    else:
        msg = fallback.read_prompt_data_for_default()
        return msg

def read_generate_question_prompt(json_format, context, section_count, tag, type):
    content = fetch_config_template(type, tag)
    if content:
        message = content.get('content', '')
        message = message.replace("{section_count}", str(section_count))
        message = message.replace("{json}", str(json_format))
        message = message.replace("{context}", str(context))
        return message
    else:
        # Fallback to default question generation
        message = fallback.read_generate_question_prompt(json_format, context, section_count)
        return message

def read_prompt_interview_closing(type):
    tag = 'parrot_interview_closing'
    content = fetch_config_template(type, tag)
    if content:
        message = content.get('content', '')  
        return message
    else:
        # Fallback to default interview closing
        message = fallback.read_prompt_interview_closing()
        return message

def read_prompt_pick_interview_question(type):
    tag = 'parrot_pick_interview_question'
    content = fetch_config_template(type, tag)
    if content:
        message = content.get('content', '')  
        return message
    else:
        # Fallback to default pick interview question
        message = fallback.read_prompt_pick_interview_question()
        return message
  
def read_prompt_followup_checker(type, candidate_response):
    tag = 'parrot_followup_checker'
    content = fetch_config_template(type, tag)
    if content:
        message = content.get('content', '')
        message = message.replace("{candidate_response}", candidate_response) 
        return message
    else:
        # Fallback to default follow-up question generation
        message = fallback.read_prompt_followup_checker(candidate_response)
        return message

def read_prompt_followup_question_generator(type, candidate_response):
    tag = 'parrot_followup_question_generator'
    content = fetch_config_template(type, tag)
    if content:
        message = content.get('content', '')
        message = message.replace("{candidate_response}", candidate_response)
        return message
    else:
        # Fallback to default follow-up question generation
        message = fallback.read_prompt_followup_question_generator(candidate_response)
        return message
    
def read_realtime_evaluation():
    tag = 'parrot_realtime_evaluation'
    type = 'job_interview_config'
    content = fetch_config_template(type, tag)
    if content:
        realtime_msg = content.get('content', '')
        return realtime_msg
    else:
        # Fallback to default realtime evaluation
        realtime_prompt = file_reader(prompts_path('realtime_evaluation.txt'))
        return realtime_prompt
    
def read_prompt_realtime_evaluation(type, data, last_assistant_response):
    tag = 'parrot_realtime_evaluation'
    content = fetch_config_template(type, tag)
    if content:
        message = content.get('content', '')
        message = message.replace("{question}", last_assistant_response)
        message = message.replace("{candidate_response}", data['response'])
        return message
    else:
        # Fallback to default realtime evaluation
        realtime_prompt = fallback.read_prompt_realtime_evaluation(data, last_assistant_response)
        return realtime_prompt
    
def read_prompt_closing_question_realtime_evaluation(type, last_assistant_response, candidate_response):
    tag = 'parrot_closing_question_realtime_evaluation'
    content = fetch_config_template(type, tag)
    if content:
        data_content = content.get('content', '')
        closing_content = data_content.replace("{closing_question}", str(last_assistant_response))
        closing_content = data_content.replace("{candidate_response}" , str(candidate_response))
        return closing_content
    else:
        # Fallback to default closing question realtime evaluation
        closing_prompt = fallback.read_prompt_closing_question_realtime_evaluation(
            last_assistant_response, candidate_response
        )
        return closing_prompt
    
def read_prompt_clarify(question):
    tag = 'parrot_clarify_question'
    type = 'job_interview_config'
    content = fetch_config_template(type, tag)
    if content:
        message = content.get('content', '')
        message = message.replace("{question}", question) 
        return message
    else:
        # Fallback to default clarification prompt
        message = fallback.read_prompt_clarify(question)
        return message
    
def read_prompt_time_limit_generator(type, question):
    tag = 'parrot_interview_question_time_limit_generatorg'
    type = 'job_interview_config'
    content = fetch_config_template(type, tag)
    if content:
        message = content.get('content', '')
        message = message.replace("{question}", question)
        return message
    else:
        # Fallback to default time limit generator
        message = fallback.read_prompt_time_limit_generator(question)
        return message

def read_prompt_overall_evaluation(type, history_str):
    tag = 'parrot_overall_evaluation'
    content = fetch_config_template(type, tag)
    if content:
        message = content.get('content', '')
        message = message.replace("{history}", history_str)  
        return message  
    else:
        # Fallback to default overall evaluation
        message = fallback.read_prompt_overall_evaluation(history_str)
        return message

def read_prompt_interview_evaluation_metrics(type, history_str):
    tag = 'parrot_interview_evaluation_metrics'
    content = fetch_config_template(type, tag)
    if content:
        message = content.get('content', '')
        message = message.replace("{history}", history_str)  
        return message 
    else:
        # Fallback to default interview evaluation metrics
        message = fallback.read_prompt_interview_evaluation_metrics(history_str)
        return message

def read_external_audio_analysis(transcript, type, tag):
    content = fetch_config_template(type, tag)
    realtime_prompt = read_realtime_evaluation()
    if content:
        message = content.get('content', '')
        message = message.replace("{transcription}", str(transcript))
        message = message.replace("{realtime}", str(realtime_prompt)) 

        return message
    else:
       message = fallback.read_external_audio_analysis(transcript)

def add_question_number(generated_question_json):
    # Iterate over the list of sections and add question numbers
    question_number = 1

    for section_dict in generated_question_json:
        # Check if 'questions' exists and is a list
        if 'questions' in section_dict and isinstance(section_dict['questions'], list):
            # Iterate over the questions in the section
            for question in section_dict['questions']:
                # Ensure the question is a dictionary before adding the question_number
                if isinstance(question, dict):
                    question["question_number"] = str(question_number)  # Add question number
                    question_number += 1
                else:
                    logger.warn(f"Unexpected question format: {question}")  # Debug unexpected format
        else:
            logger.warn(f"Unexpected section format or missing questions: {section_dict}")  # Debug unexpected format

    return generated_question_json

def fetch_config_template(type, tag):
    try:
        ipersona_template = IpersonaTinderTemplateSchema()
        templates = ipersona_template.filter_by_type_without_cursor(
                        type=type, 
                        nopp=True, 
                        dataframe=False
                    )
        if templates:
            content = filter_smg_criterion_metrics_by_tag(templates, tag)
            return content
        else:
            return False
    
    except Exception as e:
        logger.error(f"Error processing files: {e}")
        return {'error': str(e)}
    
def filter_smg_criterion_metrics_by_tag(data, tag):
    """
    Filters the 'smg_criterion_metrics' inside the given data based on the specified tag.
    
    :param data: List of dictionaries containing 'smg_criterion_metrics'.
    :param tag: The tag to filter by.
    :return: A single dictionary matching the tag with only id, tag, and content.
    """
    for item in data:
        attributes = item.get("attributes", {})
        smg_metrics = attributes.get("smg_criterion_metrics", {}).get("data", [])
        
        for metric in smg_metrics:
            metric_attributes = metric.get("attributes", {})
            if metric_attributes.get("tag") == tag:
                return {
                    "id": metric["id"],
                    "tag": metric_attributes["tag"],
                    "content": metric_attributes["content"]
                }
    
    return {} 

def attach_session_id_to_a_template(template_id, session_id):
    try:
        job_profile_ids = [] 
        prompt_ids = []
        challenge_ids = []
        ipersona_template =  IpersonaTinderTemplateSchema()
        attach_template = ipersona_template.add_job_profiles_to_template(
            template_id, 
            job_profile_ids, 
            prompt_ids, 
            challenge_ids,
            session_id)
        
        logger.info(f"Session attached to a template with session ID: {session_id}")
        return attach_template
    
    except Exception as e:  
        logger.error(f"Error processing files: {e}")
        return {'error': str(e)}

# ---------------------------------------- AUDIO PATH ----------------------------------------
def get_project_root() -> str:
    """Get the project root directory.
    
    Returns:
        Absolute path to project root
    """
    # Get the directory containing this file (utils/)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up one level to get project root
    return os.path.dirname(current_dir) 

def audio_path(relative_path: str) -> str:
    """Get absolute path to prompt file.
    
    Args:
        relative_path: Relative path from prompts directory
        
    Returns:
        Absolute path to prompt file
    """
    return os.path.join(get_project_root(), "audio", relative_path)

def prompt_path(relative_path: str) -> str:
    """Get absolute path to prompt file.
    
    Args:
        relative_path: Relative path from prompts directory
        
    Returns:
        Absolute path to prompt file
    """
    # get_project_root() currently points to the 'api' directory, so do NOT prepend another 'api'
    return os.path.join(get_project_root(), "pages", "ipersona", "routers", "data", "prompts", relative_path)

def get_data_audio_path(filename: str = "") -> str:
    """
    Return the absolute path to the data/audio directory in the project root.
    If filename is provided, return the path to that file inside data/audio.
    """
    base = os.path.join(get_project_root(), 'audio')
    return os.path.join(base, filename) if filename else base
    
def convert_to_mp3(input_bytes: bytes, original_format: str) -> bytes:
    logger.info(f"Starting conversion of format: {original_format}")
    try:
        from pydub import AudioSegment
        import io
        audio = AudioSegment.from_file(io.BytesIO(input_bytes), format=original_format)
        mp3_io = io.BytesIO()
        audio.export(mp3_io, format="mp3")
        mp3_bytes = mp3_io.getvalue()
        logger.info(f"Conversion successful. Original size: {len(input_bytes) / 1024 / 1024:.2f} MB | MP3 size: {len(mp3_bytes) / 1024 / 1024:.2f} MB")
        return mp3_bytes
    except Exception as e:
        logger.error(f"Error during mp3 conversion: {e}")
        raise

