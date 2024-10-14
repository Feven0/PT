
from openai import OpenAI
import json, os, re, ast
import os
import json_repair
from collections import defaultdict
from api.llm.ipersona.ipersona_agent import agents
import api.llm.ipersona.ipersona_db as database
import api.llm.ipersona.ipersona_schema as db
from api.config import get_openapi_token
from api.utils.logger import LLPackerLogger, logme

logger = LLPackerLogger(os.path.basename(__file__))

keys_json  = get_openapi_token(ssmkey="tenx/env/vars", envvar="OPENAI_API_KEY", fconfig=".env/openai_apikey.json")
OPENAI_API_KEY = keys_json['OPENAI_PARROT_API_KEY']

openai_client = OpenAI(api_key = OPENAI_API_KEY)


module_dir= os.path.dirname(__file__)
prompt_path = lambda x: os.path.join(module_dir, "prompts", x)
data_path = lambda x: os.path.join(module_dir, "data", x)



hr_agent = agents()

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
async def generate_interview_question(data: dict) -> dict:
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
        hr_agent.assistant.update_system_message(data['user_session']['persona'])   
        response = await choose_interview_question(data['user_session']['generated_questions'], data)
        
        return response
    
    except Exception as e:
        logger.error(f"Persona Creation Error: ${str(e)}")
        return {'error': str(e)}
    
    
#-------------------------------------------- Choose Question from Generated ----------------------------------
async def choose_interview_question(collection: dict, data: dict) -> dict:
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
        section = None
        question_type = None
        if data['question_counter'] < 3:
            section = collection["Background"]
            question_type = "Background"
            count = None
            response = await helper_func(count, question_type, section, data)

            return response
        
        elif data['question_counter'] < 5:
            section = collection["Technical"]
            question_type = "Technical"
            count = None
            if data['question_counter'] == 3:
                count = data['question_counter']
            response = await helper_func(count, question_type, section, data)
            
            return response
            
        elif data['question_counter'] < 7:
            section = collection["Behavioral"]
            question_type = "Behavioral"
            count = None
            if data['question_counter'] == 5:
                count = data['question_counter']
            response = await helper_func(count, question_type, section, data)
            
            return response
        
        elif data['question_counter'] < 10: 
            section = collection["Ability"]
            question_type = "Ability"
            count = None
            if data['question_counter'] == 7:
                count = data['question_counter']
            response = await helper_func(count, question_type, section, data)
            
            return response

    except Exception as e:
        logger.error(f"Choosing question process failed: ${str(e)}")
        return {'error': str(e)}


#----------------------------------------- Helper Functions for Choosing Question ---------------------------------
async def helper_func(count: int, question_type: str, section: list, data: dict) -> dict:
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
        realtime_evaluation_response_json = None
        overall_evaluation_response_json = None  
        interview_question_json = None
        overall_interview_metrics_json = None   
        
        if data['question_counter'] < 9:
            if data['response']:
                if count is not None:
                    realtime_evaluation_response_json = await realtime_response_evaluation(data)
                    interview_question_json = await fetch_interview_question(section, data) 
                else:
                    realtime_evaluation_response_json = await realtime_response_evaluation(data)
                    response = await check_if_followup(data['response'])
                    if not response:
                        interview_question_json = await fetch_interview_question(section, data) 
                    else:
                        interview_question_json = await generate_followup(data['response'])
            else:
                interview_question_json = await fetch_interview_question(section, data) 
            
            if 'question_number' in interview_question_json.get('interview_question', {}):
                for item in section:
                    if item["question_number"] == interview_question_json['interview_question']['question_number']:
                        time_limit = item["time_limit"]
                        end_message = item["end_message"]
                        interview_question_json['interview_question']['question_type'] = question_type
                        interview_question_json['interview_question']['time_limit'] = time_limit
                        interview_question_json['interview_question']['end_message'] = end_message
                        break    
        else:  
            realtime_evaluation_response_json = await realtime_response_evaluation(data)
            overall_evaluation_values = await overall_interview_evaluations(data, realtime_evaluation_response_json)
            overall_interview_metrics_json = overall_evaluation_values["overall_interview_metrics"]
            overall_evaluation_response_json = overall_evaluation_values["overall_evaluation_response"]
                
        response = {
            "interview": interview_question_json,
            "realtime": realtime_evaluation_response_json,          
            "overall": overall_evaluation_response_json,
            "metrics": overall_interview_metrics_json
        }
        return response
    
    except Exception as e:
        logger.error(f"Choosing question helper process failed: ${str(e)}")
        return {'error': str(e)}
   
   
#----------------------------------------- picking the right Question ----------------------------------------- 
async def fetch_interview_question(section: list, data: dict) -> dict:
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

        response = await hr_agent.generate_question(msg)
        response_json = extract_json(response, quite=False)
        
        return response_json     

    except Exception as e:
        logger.error(f"Choosing the right question process failed: ${str(e)}")
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
             
        response = await hr_agent.generate_question(msg)
        response_json = extract_json(response, quite=False)

        return response_json["follow-up"]
    
    except Exception as e:
        logger.error(f"Checking follow up process failed: ${str(e)}")
        return {'error': str(e)}
    
    
#-------------------------------------------- Generate Follow up Question -----------------------------------
async def generate_followup(candidate_response: str) -> dict:
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
        msg = context.replace("{candidate_response}", candidate_response)
        response = await hr_agent.generate_question(msg)
        response_json = extract_json(response, quite=False)
        response_json['interview_question']['end_message'] = "Please take your time to provide a detailed response"
        
        return response_json
    
    except Exception as e:
        logger.error(f"Generating follow up failed: ${str(e)}")
        return {'error': str(e)}


#---------------------------------------- Realtime Chat Evaluation Function -------------------------------
async def realtime_response_evaluation(data: dict) -> dict:
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
        evaluation_prompt = file_reader(prompt_path('ipersona/realtime_evaluation.txt'))
        evaluation_context = str(evaluation_prompt)
        evaluation_msg = evaluation_context\
            .replace("{question}", data["previous_question"])\
            .replace("{candidate_response}", data['response'])
                
        # Evaluate the real-time chat response for the last response
        realtime_evaluation_response = await hr_agent.evaluate_candidate_response(evaluation_msg)
        realtime_evaluation_response = extract_json(realtime_evaluation_response, quite=False)
        
        return realtime_evaluation_response
        
    except Exception as e:
        logger.error(f"Real time evaluation process failed: ${str(e)}")
        return {'error': str(e)} 
    
    
#----------------------------------------- Overall Interview Evaluation -------------------------------
async def overall_interview_evaluations(data: dict, realtime_evaluation_response_json: dict) -> dict:
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
        overall_evaluation_prompt = file_reader(prompt_path('ipersona/overall_evaluation.txt'))
        overall_metrics_prompt = file_reader(prompt_path("ipersona/interview_metrics_rubrics.txt"))
        overall_evaluation_context = str(overall_evaluation_prompt)
        overall_metrics_context = str(overall_metrics_prompt)
        history_str = '\n'.join(str(item) for item in data['history'])

        overall_evaluation_msg = overall_evaluation_context\
            .replace("{history}", history_str)  
                
        overall_metrics_msg = overall_metrics_context\
            .replace("{history}", history_str)  
                
        # Overall interview evaluation once the interview ended        
        overall_evaluation_response = await hr_agent.evaluate_overall_interview(overall_evaluation_msg)
        overall_evaluation_response_json = extract_json(overall_evaluation_response, quite=False)
        
        # Generate the Metrics for an interview
        overall_interview_metrics_response = await hr_agent.overall_interview_metrics(overall_metrics_msg)
        overall_interview_metrics_json = extract_json(overall_interview_metrics_response, quite=False)
        
        # Adding necessary data to the final response json
        message = [{ "candidate": {"response": data['response'], "time_taken": data['time_taken']}},
                   {"assistant": {"response": "null", 
                                  "realtime_evaluation": realtime_evaluation_response_json["realtime_evaluation"], 
                                  "overall_evaluation": overall_evaluation_response_json["overall_evaluation"], 
                                  "metrics": "null"}}]        
        data['history'].extend(message)
        
        time_array = calculate_time(data['history'])
        relevancy = filter_the_relevancies(data['history'])
        percent_term = percentage_term(relevancy["average"])
        
        overall_interview_metrics_json["evaluation_metrics"]["time_management"] = time_array
        overall_interview_metrics_json["evaluation_metrics"]["relevancy"] = relevancy["relevancy"]
        overall_evaluation_response_json["overall_evaluation"]["overall_performance"] = relevancy["average"]
        overall_evaluation_response_json["overall_evaluation"]["message"] = percent_term["term"]
        overall_interview_metrics_json["evaluation_metrics"]["message"] = percent_term["term"]
        overall_interview_metrics_json["evaluation_metrics"]["rating"] = percent_term["rating"]
        
        ############################## Save final chat history to weaviate ##########################################
        temp = data['history'][-1]
        temp["assistant"]["realtime_evaluation"] = realtime_evaluation_response_json["realtime_evaluation"]
        temp["assistant"]["overall_evaluation"] = overall_evaluation_response_json["overall_evaluation"]
        temp["assistant"]["metrics"] = overall_interview_metrics_json["evaluation_metrics"]
        await database.save_chathistory_to_db(data)
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
        response = await hr_agent.interview_question_clarification(msg)
        response = extract_json(response, quite=False)
    
        return response
    
    except Exception as e:
        logger.error(f"Overall evaluation process failed: ${str(e)}")

        return {'error': str(e)}


#-------------------------------------------- Job Description Class Identifier -----------------------------------
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
def time_to_seconds(time_str):
    """Convert time in 'HH:MM' format to seconds."""
    if time_str == "00:00":
        return 0
    h, m = map(int, time_str.split(':'))
    return h * 3600 + m * 60


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
        
        for i in range(len(interview)):
            if 'assistant' in interview[i]:
                assistant_response = interview[i]['assistant']['response']
                if assistant_response and 'time_limit' in assistant_response:
                    time_limit = assistant_response['time_limit']
                    time_limit_seconds = time_to_seconds(time_limit)
                    
                    if i + 1 < len(interview) and 'candidate' in interview[i + 1]:
                        time_taken = interview[i + 1]['candidate']['time_taken']
                        time_taken_seconds = time_to_seconds(time_taken)

                        if time_taken_seconds > time_limit_seconds:
                            exceeded_count += 1
                        else:
                            not_exceeded_count += 1
        
        time_data = {
            "fail": exceeded_count,
            "pass": not_exceeded_count
        }
        return time_data
    
    except Exception as e:
        logger.error(f"Calculating overall time failed: ${str(e)}")

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
            if 'assistant' in entry and 'realtime_evaluation' in entry['assistant']:
                evaluation = entry['assistant']['realtime_evaluation']
                if 'answer_relevancy' in evaluation:
                    for relevance in evaluation['answer_relevancy']:
                        relevance_with_index = {
                            "index": index_counter,  
                            "level": relevance['level'],
                            "reason": relevance['reason']
                        }
                        relevancy.append(relevance_with_index)
                        index_counter += 1 
                        
        levels = [int(item["level"]) for item in relevancy]
        average_relevancy = sum(levels) / len(levels) if levels else 0
        
        data = {
            "relevancy": relevancy,
            "average": average_relevancy
        }
        return data
    
    except Exception as e:
        logger.error(f"Filtering overall relevance process failed: ${str(e)}")
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
def calculate_overall_progress(data: list) -> dict:
    """
    Calculates the overall progress metrics from interview data.

    This function processes the interview data to assess and summarize 
    metrics related to confidence, clarity, and engagement over time. 
    It aggregates the metrics from the chat history and restructures them 
    for visualization.

    Parameters:
    ----------
    data : list
        A list of dictionaries representing the interview sessions, where 
        each dictionary contains chat history and evaluation metrics.

    Returns:
    -------
    dict
        A JSON object containing overall metrics for confidence, clarity, 
        engagement, time management, competency, and performance, or an 
        error message if an exception occurs during processing.
    """
    try:
        confidence_overtime = []  
        clarity_overtime = []     
        engagement_overtime = []   

        for dataset in data:  
            confidence_count = {}
            clarity_count = {
                "excellent": 0,
                "good": 0,
                "poor": 0
            }
            engagement_count = {
                "excellent": 0,
                "good": 0,
                "poor": 0
            }
            
            for entry in dataset['chathistory']:  
                if "assistant" in entry:
                    assistant_eval = entry["assistant"]
                    # Answer relevance overall metrics
                    if "metrics" in assistant_eval:
                        metrics = assistant_eval["metrics"]
                        if isinstance(metrics, dict):
                            for performance in metrics.get("performance", []):
                                if isinstance(performance, dict):
                                    # Check for confidence level
                                    performance_name = performance.get('name')
                                    confidence_level = performance.get('level', '').lower() 

                                    if confidence_level:
                                        confidence_count[confidence_level] = 1

                    # Communication overall metrics
                    if "realtime_evaluation" in assistant_eval:
                        realtime = assistant_eval["realtime_evaluation"]
                        
                        if isinstance(realtime, dict):
                            for communication in realtime.get("communication_skills", []):                            
                                if isinstance(communication, dict):
                                    # Count overall clarity
                                    if communication.get('skill') == "clarity":  
                                        clarity_level = communication['level'].lower()  
                                        if clarity_level in clarity_count:
                                            clarity_count[clarity_level] += 1

                                    # Count overall engagement
                                    if communication.get('skill') == "engagement":  
                                        engagement_level = communication['level'].lower()  
                                        if engagement_level in engagement_count:
                                            engagement_count[engagement_level] += 1

            confidence_overtime.append(confidence_count)
            clarity_overtime.append(clarity_count)
            engagement_overtime.append(engagement_count)
            
            # Restructure communication skills
            clarity = restructure_communication_skills_for_vis(clarity_overtime)
            engagement = restructure_communication_skills_for_vis(engagement_overtime)
        
        result = extract_necessary_metrics(data)   
        response = {
            "overall_confidence": confidence_overtime,
            "overall_clarity": clarity,
            "overall_engagement": engagement,
            "overall_time_management": result["overall_time_management"],
            "overall_competency": result["overall_competency"],
            "overall_performance": result["overall_performance"]
        }
        return response
        
    except Exception as e:
        logger.error(f"Calculating overall progress process failed: ${str(e)}")

        return {'error': str(e)}
        

#------------------------------------ Entire Data Progress Metrics Extraction --------------------------------------
def extract_necessary_metrics(data: list) -> dict:
    try:
        """
        Extracts and restructures necessary metrics from interview data.

        This function processes the interview data to gather metrics related to 
        time management, competency, and overall performance. It compiles these 
        metrics into a structured format for further analysis.

        Parameters:
        ----------
        data : list
            A list of dictionaries representing the interview sessions, where 
            each dictionary contains chat history and evaluation metrics.

        Returns:
        -------
        dict
            A JSON object containing overall metrics for time management, 
            competency, and performance, structured for visualization.
        """
        overall_time_management = []
        overall_competency = []
        overall_performance = []
        
        for index, dataset in enumerate(data): 
            for entry in dataset['chathistory']: 
                if "assistant" in entry:
                    assistant_eval = entry["assistant"]                
                    if "metrics" in assistant_eval:
                        metrics = assistant_eval["metrics"]
                        if isinstance(metrics, dict):
                            time = metrics.get("time_management", [])
                            overall_time_management.append(time)
                            
                    if "overall_evaluation" in assistant_eval:
                        overall_evaluation = assistant_eval["overall_evaluation"]
                        if "competency" in overall_evaluation:
                            competency = overall_evaluation["competency"]
                            overall_competency.append(competency)
                        if isinstance(overall_evaluation, dict):                            
                            overall_eval_performance = overall_evaluation.get("overall_performance")
                            performance = {
                                "interview": index,
                                "performance": overall_eval_performance
                            }
                            overall_performance.append(performance)
        
        # Restructuring time management data
        time_management = restructure_communication_skills_for_vis(overall_time_management)

        response = {
            "overall_time_management": time_management,
            "overall_competency": overall_competency,
            "overall_performance": overall_performance
        }    
        
        return response  

    except Exception as e:
        logger.error(f"Neccessary metrics extraction process failed: ${str(e)}")

        return {'error': str(e)}


#------------------------------ Restructuring Communication skills format For Visualization ------------------------
def restructure_communication_skills_for_vis(data: list) -> list:
    """
    Restructures communication skills data for visualization.

    This function transforms the communication skills data into a format 
    suitable for visualization by creating a list of dictionaries that 
    represent relationships between interview names and their corresponding 
    skill levels.

    Parameters:
    ----------
    data : list
        A list of dictionaries containing communication skills metrics from 
        multiple interviews.

    Returns:
    -------
    list
        A list of dictionaries where each dictionary contains the interview 
        name, skill type (capitalized), and corresponding value, or an error 
        message if an exception occurs during processing.
    """
    try:
        transformed_data = []
        for i, interview in enumerate(data, start=1):
            interview_name = f"Interview {i}"
            for target, value in interview.items():
                transformed_data.append({
                    "source": interview_name,
                    "target": target.capitalize(), 
                    "value": value
                })
                
        return transformed_data
    except Exception as e:
        logger.error(f"Response restructring process failed: ${str(e)}")

        return {'error': str(e)}




#-------------------------------------------- FIle reader --------------------------------------------
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
            # try simple to load it as json
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