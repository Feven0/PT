from openai import OpenAI
import json, os
import os
import json_repair
from collections import defaultdict
from api.services.strapi_ipersona import IpersonaManager
from datetime import datetime
from api.utils.logger import LLPackerLogger
import api.llm.ipersona.ipersona_gpt as gpt

logger = LLPackerLogger(os.path.basename(__file__))

from api.services.secret import get_auth

OPENAI_API_KEY  = get_auth(ssmkey='OPENAI_PARROT_API_KEY')
openai_client = OpenAI(api_key=OPENAI_API_KEY )

module_dir= os.path.dirname(__file__)
prompt_path = lambda x: os.path.join(module_dir, "prompts", x)
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
            logger.error(f"Persona Creation Error: {str(e)}")
            return f'Error: {str(e)}'             


#--------------------------------------------  Generate Interview Questions --------------------------------
async def generate_interview_question(data: dict):
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
        
        # hr_agent.assistant.update_system_message(data['user_session']['persona'])   
        response = await choose_interview_question(data['user_session']['attributes']['attributes']['generated_questions'], data)
        
        return response
    
    except Exception as e:
        logger.error(f"Persona Creation Error: ${str(e)}")
        return {'error': str(e)}
    
    
#-------------------------------------------- Choose Question from Generated ----------------------------------
async def choose_interview_question(collection: dict, data: dict):
    """
    Selects an interview question based on the current question counter.

    This asynchronous function determines the appropriate section of interview questions 
    (Background, Technical, Behavioral, or Ability) based on the `question_counter` value 
    in the provided data. It then calls a helper function to retrieve a question from 
    the selected section.

    Parameters:
    ----------
    collection : dict
        A dictionary containing different sections of interview questions, 
        organized by type.

    data : dict
        A dictionary containing session information, including the current 
        question counter.

    Returns:
    -------
    dict
        A JSON object containing the selected interview question, or an error message 
        if an exception occurs during processing.
    """
    try: 
        ipersona_manager = IpersonaManager(sessionId=data['user_session']['id'], run_stage="dev")
        session_chathistory = ipersona_manager.get_messages()
        chat = session_chathistory['count']
  
        global chat_count
        chat_count = 1
        
        if chat != 0:  
            chat = session_chathistory['total']
            assistant_count = sum(1 for entry in chat if entry["user_type"] == "assistant")
            chat_count += assistant_count 
            logger.info("Number of assistant entries:", chat_count)
        else:
            logger.error("Chat is empty.")
        
        section = None
        question_type = None
        if chat_count < 3: 
            section = collection["Background"]
            question_type = "Background"
            count = None
            response = await helper_func(count, question_type, section, data)

            return response
        
        elif chat_count < 5: 
            section = collection["Technical"]
            question_type = "Technical"
            count = None
            if chat_count == 3: 
                count = chat_count
            response = await helper_func(count, question_type, section, data)
            
            return response
            
        elif chat_count < 7: 
            section = collection["Behavioral"]
            question_type = "Behavioral"
            count = None
            if chat_count == 5: 
                count = chat_count
            response = await helper_func(count, question_type, section, data)
            
            return response
        
        elif chat_count < 10: 
            section = collection["Ability"]
            question_type = "Ability"
            count = None
            if chat_count == 7: 
                count = chat_count
            response = await helper_func(count, question_type, section, data)
            
            return response

    except Exception as e:
        logger.error(f"Choosing question process failed: ${str(e)}")
        return {'error': str(e)}


#----------------------------------------- Helper Functions for Choosing Question ---------------------------------
async def helper_func(count: int, question_type: str, section: list, data: dict):
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
                
        if chat_count < 9:
            if data['response']:
                if count is not None:
                    interview_question_json = await fetch_interview_question(section, data) 
                else:
                    response = await check_if_followup(data['response'])
         
                    if not response:
                        interview_question_json = await fetch_interview_question(section, data) 
                    else:
                        interview_question_json = await generate_followup(data)
                       
            else:
                interview_question_json = await fetch_interview_question(section, data) 
   
        else:  
            await overall_interview_evaluations(data)
            
                
        response = {
            "interview": interview_question_json
        }
        
        return response
    
    except Exception as e:
        logger.error(f"Choosing question helper process failed: ${str(e)}")
        return {'error': str(e)}
   
   
#----------------------------------------- picking the right Question ----------------------------------------- 
async def fetch_interview_question(section: list, data: dict):
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
        message = file_reader(prompt_path('ipersona/pick_question.txt'))
        context = str(message)
        questions = []
        msg = context\
            .replace("{collection}", str(section))\
            .replace("{questions}", str(questions))\
            .replace("{candidate_response}", data['response'])        

        content = data['user_session']['attributes']['attributes']['persona'] + msg
        response = gpt.openai_gpt_assistant_with_streaming(content)
        
        return response
    except Exception as e:
        logger.error(f"Choosing the right question process failed: ${str(e)}")
        return {'error': str(e)}
    
#-------------------------------- Interview question time limit generation ---------------------------- 
def interview_question_time_limit(question: str):
    try:
        message = file_reader(prompt_path('ipersona/time_limit_generator.txt'))
        context = str(message)
        msg = context\
            .replace("{question}", question)     

        response = gpt.openai_gpt_assistant_without_streaming(msg)
        response = extract_json(response, quite=False)
        return response
    except Exception as e:
        logger.error(f"generating time limit process failed: ${str(e)}")
        return {'error': str(e)}
    
    
#---------------------------------------- Follow up Question Checker -------------------------------
async def check_if_followup(candidate_response: str) -> bool:
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
        message = file_reader(prompt_path('ipersona/follow_up_check.txt'))

        context = str(message)
        msg = context.replace("{candidate_response}", candidate_response) 
             
        # response = await hr_agent.generate_question(msg)
        response = gpt.openai_gpt_assistant_without_streaming(msg)

        response_json = extract_json(response, quite=False)

        return response_json["follow-up"]
    
    except Exception as e:
        logger.error(f"Checking follow up process failed: ${str(e)}")
        return {'error': str(e)}
    
    
#-------------------------------------------- Generate Follow up Question -----------------------------------
async def generate_followup(data) -> dict:
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
        message = file_reader(prompt_path('ipersona/follow_up.txt'))
        context = str(message)
        msg = context.replace("{candidate_response}", data['response'])
        # response = await hr_agent.generate_question(msg)
        
        content = data['user_session']['attributes']['attributes']['persona'] + msg
        response = gpt.openai_gpt_assistant_with_streaming(content)
        
        # response_json = extract_json(response, quite=False)
        # response_json['interview_question']['end_message'] = "Please take your time to provide a detailed response"
        
        return response
    
    except Exception as e:
        logger.error(f"Generating follow up failed: ${str(e)}")
        return {'error': str(e)}


#---------------------------------------- Realtime Chat Evaluation Function -------------------------------
def realtime_response_evaluation(data: dict) -> dict:
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
        ipersona_manager = IpersonaManager(sessionId=data['user_session']['id'], run_stage="dev")
        session_chathistory = ipersona_manager.get_messages()
        history = session_chathistory['total']
        
        last_assistant_response = None
        for entry in reversed(history):
            message = entry            
            if message["user_type"] == "assistant":
                last_assistant_response = message["content"].get("full_response")  
                break  

        if last_assistant_response:
            logger.info("Last assistant response")
        else:
            logger.warn("No assistant response found in the chat history.")
            
        evaluation_prompt = file_reader(prompt_path('ipersona/realtime_evaluation.txt'))
        evaluation_context = str(evaluation_prompt)
        evaluation_msg = evaluation_context\
            .replace("{question}", last_assistant_response)\
            .replace("{candidate_response}", data['response'])
                
        
        content = data['user_session']['attributes']['attributes']['persona'] + evaluation_msg

        realtime_evaluation_response = gpt.openai_gpt_assistant_without_streaming(content)

        realtime_evaluation_response = extract_json(realtime_evaluation_response, quite=False)
        
        return realtime_evaluation_response
        
    except Exception as e:
        logger.error(f"Real time evaluation process failed: ${str(e)}")
        return {'error': str(e)} 
    
    
#----------------------------------------- Overall Interview Evaluation -------------------------------
async def overall_interview_evaluations(data: dict) -> dict:
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
        ipersona_manager = IpersonaManager(sessionId=data['user_session']['id'] , run_stage="dev")
        all_chat_history = ipersona_manager.get_messages()
        history = all_chat_history['total']
        
        overall_evaluation_prompt = file_reader(prompt_path('ipersona/overall_evaluation.txt'))
        overall_metrics_prompt = file_reader(prompt_path("ipersona/interview_metrics_rubrics.txt"))
        overall_evaluation_context = str(overall_evaluation_prompt)
        overall_metrics_context = str(overall_metrics_prompt)
        history_str = '\n'.join(str(item) for item in history)

        overall_evaluation_msg = overall_evaluation_context\
            .replace("{history}", history_str)  
                
        overall_metrics_msg = overall_metrics_context\
            .replace("{history}", history_str)  
                
     
        content = data['user_session']['attributes']['attributes']['persona'] + overall_evaluation_msg
        overall_evaluation_response = gpt.openai_gpt_assistant_without_streaming(content)

        overall_evaluation_response_json = extract_json(overall_evaluation_response, quite=False)
   
        content = data['user_session']['attributes']['attributes']['persona'] + overall_metrics_msg
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
                "metadata": {
                    "createdBy": "parrot"
                }                
            }
        ipersona_manager = IpersonaManager(sessionId=data['user_session']['id'], run_stage="dev")
        ipersona_manager.insert_observer(overall_json)
        ipersona_manager.update_session_status()
        
                        #-----------------------------------------------------------#
        ipersona_manager = IpersonaManager(sessionId=42, alluserId=1974, jobId=46, run_stage="dev")
        session = ipersona_manager.get_job_sessions()   
        session_chatobserver = extract_observers_metrics(session)
                    
        calculate_overall_progress(data, session_chatobserver) 
    
        #################################################################################################
      
        response = {
            "overall_interview_metrics": overall_interview_metrics_json,
            "overall_evaluation_response": overall_evaluation_response_json
        }
        
        return response
        
    except Exception as e:
        logger.error(f"Overall evaluation process failed: ${str(e)}")

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
        message = file_reader(prompt_path("ipersona/clarify_question.txt"))
        context = str(message)
        msg = context.replace("{question}", question)
        # response = await hr_agent.interview_question_clarification(msg)
        response = gpt.openai_gpt_assistant_without_streaming(msg)
        response = extract_json(response, quite=False)
    
        return response
    
    except Exception as e:
        logger.error(f"Overall evaluation process failed: ${str(e)}")

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
        logger.error(f"Persona class identification failed: ${str(e)}")
        return {'error': str(e)}
    

#-------------------------------------------- Helper function for Time Function -------------------------------------
# def time_to_seconds(time_str):
#     """Convert time in 'HH:MM' format to seconds."""
#     if time_str == "00:00":
#         return 0
#     h, m = map(int, time_str.split(':'))
#     return h * 3600 + m * 60

def time_to_seconds(time_str):
    """Convert time in 'HH:MM:SS' or 'MM:SS' format to seconds."""
    try:
        if not time_str or time_str == "00:00" or time_str == "00:00:00":
            return 0
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
        print(f"Error converting time: {e}")
        return 0

def seconds_to_time(seconds):
    """Convert seconds back to 'HH:MM:SS' format."""
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02}:{m:02}:{s:02}"


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
            if entry['user_type'] == 'assistant' and 'realtime_evaluation' in entry['content']:
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
        logger.error(f"Filtering overall relevance process failed: {str(e)}")
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
        logger.error(f"Percentage term assignation process failed: ${str(e)}")

        return {'error': str(e)}
    

#----------------------------------------- Entire Data Progress Calculator -----------------------------------------   
def calculate_overall_progress(userdata, data: list):
    try:
        confidence_overtime = []  
        clarity_overtime = []     
        engagement_overtime = [] 
        overall_time_managements = []
        overall_competencies = []
        overall_performance_scores = []
        session_ids = []         

        for entry in data:
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
                    if(confidence_level == 'poor'):
                            value = 1
                    elif(confidence_level == 'good'):
                        value = 2
                    elif(confidence_level == 'excellent'):
                        value = 3
                    confidence = {"time": created_time, "level": confidence_level, "value": value}
                    confidence_overtime.append(confidence)                        
           
            if isinstance(realtime, list):
                for communication in realtime:  
                    if communication.get('skill') == "clarity":  
                        clarity_level = communication['level'].lower() 
                        if(clarity_level == 'poor'):
                            value = 1
                        elif(clarity_level == 'good'):
                            value = 2
                        elif(clarity_level == 'excellent'):
                            value = 3
                        clarity = {"time": created_time, "level": clarity_level, "value": value}
                        clarity_overtime.append(clarity)

                    if communication.get('skill') == "engagement":  
                        engagement_level = communication['level'].lower()  
                        if(engagement_level == 'poor'):
                            value = 1
                        elif(engagement_level == 'good'):
                            value = 2
                        elif(engagement_level == 'excellent'):
                            value = 3
                        engagement = {"time": created_time, "level": engagement_level, "value": value}
                        engagement_overtime.append(engagement)
      
        
        alluserId=userdata['alluserId']
        jobId=userdata['jobId']
       
        ipersona_manager = IpersonaManager(alluserId=alluserId, jobId=jobId, run_stage="dev")
        session_chatobserver = ipersona_manager.session_overall_observer_by_user_and_job()
        session_chatobserver_sessions = session_chatobserver['all_sessions']

        if len(session_chatobserver_sessions) > 0:
            attributes = {
                "overall_confidence": confidence_overtime,
                "overall_clarity": clarity_overtime,
                "overall_engagement": engagement_overtime,
                "overall_time_management": overall_time_managements,
                "overall_competency": overall_competencies,
                "overall_performance": overall_performance_scores
            }
            
            ipersona_manager = IpersonaManager(sessionId=str(session_chatobserver['id']), run_stage="dev")
            response = ipersona_manager.update_session_job_observer(attributes)
            
        else:            
            message_data = {
                "attributes": {
                    "overall_confidence": confidence_overtime,
                    "overall_clarity": clarity_overtime,
                    "overall_engagement": engagement_overtime,
                    "overall_time_management": overall_time_managements,
                    "overall_competency": overall_competencies,
                    "overall_performance": overall_performance_scores
                },
                "metadata": {
                    "createdBy": "parrot"
                },
                "jobId": str(jobId),  
                "alluserId": str(alluserId),  
                "sessionIds": session_ids
            }
        
            ipersona_manager = IpersonaManager(run_stage="dev")
            response = ipersona_manager.create_session_overall_observer(message_data)    
    
        return response
    
    except Exception as e:
        logger.error(f"Process failed: ${str(e)}")
        return f'Error: {str(e)}'  
    

#----------------------------- Entire User Session Progress Over All Types of Jobs -----------------------------
def all_session_jobs_average_metrics(data):
    try:
        avg_confidence = calculate_average(data['overall_confidence'])
        avg_clarity = calculate_average(data['overall_clarity'])
        avg_engagment = calculate_average(data['overall_engagement'])
        avg_time_management = calculate_average_time_management(data['overall_time_management'])
 
        
        overall_data = {
                            "avg_confidence": avg_confidence,
                            "avg_clarity": avg_clarity,
                            "avg_engagment": avg_engagment,
                            "avg_time_management": avg_time_management
                        }
        
        return overall_data


        
    except Exception as e:
        logger.error(f"process failed: ${str(e)}")
    
    
def calculate_average(data):
    total_score = 0
    count = 0
    
    for entry in data:
        value = entry.get("value", 0)          
        total_score += value 
        count += 1 
    
    average_confidence = total_score / count if count > 0 else 0
    return round(average_confidence, 2)


def calculate_average_time_management(data):
    total_passes = 0
    total_fails = 0
    
    for entry in data:
        time_management = entry.get("time_management", {})
        passes = time_management.get("pass", 0)  
        fails = time_management.get("fail", 0)    
        
        total_passes += passes  
        total_fails += fails     
    
    total_questions = total_passes + total_fails
    
    average_pass_rate = round((total_passes / total_questions) * 100, 2) if total_questions > 0 else 0
    average_fail_rate = round((total_fails / total_questions) * 100, 2) if total_questions > 0 else 0

    return {
        "total_passes": total_passes,
        "total_fails": total_fails,
        "average_pass_rate": average_pass_rate,
        "average_fail_rate": average_fail_rate
    }

#-------------------------------------------- user engagment jobs --------------------------------------------
def summarize_interviews(alluserId):
    ipersona_manager = IpersonaManager(alluserId=alluserId, run_stage="dev")
    data = ipersona_manager.get_alluser_sessions()
    data = extracted_needed_metrics(data)

    job_summary = defaultdict(list)
    
    for record in data:
        jobId = record['jobId']
        job_summary[jobId].append(record)
    
    summary_response = []
    
    for jobId, records in job_summary.items():
        total_score = sum(record['overall_performance_score'] for record in records)
        interviews_count = len(records)
        average_score = total_score / interviews_count if interviews_count > 0 else 0
        
        ipersona_manager = IpersonaManager(alluser=alluserId, jobId=jobId, run_stage="dev")
        job_title_data = ipersona_manager.get_trainee_job_profile()
        if job_title_data and len(job_title_data) > 0:
            job_title = job_title_data[0]['attributes']['attributes'].get('title', 'Unknown Job Title')
        else:
            job_title = 'Unknown Job Title'  
        
        trainee_data = ipersona_manager.get_trainee_user_profile()
        if not trainee_data:
            logger.warn("No trainee user profiles found.")
            return []

        tinder_user_profile_id = trainee_data[0]['id']
        tinder_job_profile_id = jobId
      
        job_match_data = ipersona_manager.get_match(tinder_user_profile_id, tinder_job_profile_id)
        if job_match_data and len(job_match_data) > 0:
            match_score = job_match_data[0]['attributes'].get('match_score', 'Unknown')
            job_match = job_match_data[0]['attributes'].get('match_level', 'Unknown')
        else:
            match_score = 'Unknown'  
            job_match = 'Unknown'    
        
        summary_response.append({
            "jobId": jobId,
            "job_title": job_title,
            "job_match_score": match_score,
            "job_match": job_match,
            "interviews": interviews_count,
            "score": round(average_score, 2)
        })
    
    return summary_response

def extracted_needed_metrics(data):
    extracted_observers = []
    for session in data:
        observer_data = session['attributes'].get('i_persona_observer', {}).get('data')
        if observer_data:
            observer_attributes = observer_data.get('attributes', {}).get('attributes', {}).get('interview_evaluation_metrics', {})
            session['overall_performance_score'] = observer_attributes.get('overall_performance_score', None)
            session['createdAt'] = session['attributes']['createdAt']
            session['jobId'] = session['attributes']['tinder_job_profile']['data']['id']
            extracted_observers.append(session)

    return extracted_observers

def extract_observers_metrics(data):
    extracted_observers = []
    for message in data:
        if message['attributes'].get('i_persona_observer') and message['attributes']['i_persona_observer'].get('data'):
            message_data = message['attributes']['i_persona_observer']['data']
            message_attributes = message_data['attributes']['attributes']['interview_evaluation_metrics']
            message_attributes['createdAt'] = message['attributes']['createdAt']
            message_attributes['obs_id'] = message['attributes']['i_persona_observer']['data']['id']
            extracted_observers.append(message_attributes)

    return extracted_observers
#-------------------------------------------- FIle reader --------------------------------------------
def convert_iso_to_readable_format(iso_time):
    dt = datetime.strptime(iso_time, '%Y-%m-%dT%H:%M:%S.%fZ')    
    readable_time = dt.strftime('%d %b %Y %I:%M %p')
    return readable_time

def file_reader(path: str) -> str:
    """ File Reader """
    try:       
        fname = os.path.join(path)
        with open(fname, 'r') as f:
            system_message = f.read()
        return system_message
    
    except Exception as e:
        logger.error(f"File reading process failed: ${str(e)}")

        return f'Error: {str(e)}'  
      

#------------------------------------- Json Extraction --------------------------------------------
def extract_json(response, quite=False):   
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
    
    
#------------------------------------------- Extraction Function --------------------------------------------
def extract_trainee_neccessary_values(data):
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

def extract_job_neccessary_values(data):
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
