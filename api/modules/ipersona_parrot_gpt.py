from openai import OpenAI
import json, os
import os
import json_repair
from collections import defaultdict
import api.llm.ipersona.ipersona_strapi as strapi
from datetime import datetime
from api.utils.logger import LLPackerLogger
import api.llm.ipersona.ipersona_gpt as gpt
from api.llm.ipersona.ipersona_strapi_schemas import IpersonaSessionTinderUserJobMatchSchema, IpersonaSessionTinderUserReactionSchema, IpersonaSessionSchema, IpersonaTraineeSchema, IpersonaJobSchema, IpersonaSessionOverallObserverSchema, IpersonaSessionMessageSchema, IpersonaSessionObserverSchema, IpersonaAllUserSchema, IpersonaProfileInformationSchema
  
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
        ipersona_message = IpersonaSessionMessageSchema()
        session_chathistory = ipersona_message.filter_by_session_id(
            sessionId=data['user_session']['id'], 
            nopp=True, 
            dataframe=False,
            sort='asc')
  
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
        
        section = None
        question_type = None
        if chat_count < 2: 
            section = collection["Introduction"]
            question_type = "Introduction"
            count = None
            response = await helper_func(chat_count, count, question_type, section, data)

            return response
        
        elif chat_count < 5: 
            section = collection["Background"]
            question_type = "Background"
            count = None
            if chat_count == 3: 
                count = chat_count
            response = await helper_func(chat_count, count, question_type, section, data)

            return response
        
        elif chat_count < 7: 
            section = collection["Technical"]
            question_type = "Technical"
            count = None
            if chat_count == 5: 
                count = chat_count
            response = await helper_func(chat_count, count, question_type, section, data)
            
            return response
            
        elif chat_count < 9: 
            section = collection["Behavioral"]
            question_type = "Behavioral"
            count = None
            if chat_count == 7: 
                count = chat_count
            response = await helper_func(chat_count, count, question_type, section, data)
            
            return response
        
        elif chat_count < 11: 
            section = collection["Ability"]
            question_type = "Ability"
            count = None
            if chat_count == 9: 
                count = chat_count
            response = await helper_func(chat_count, count, question_type, section, data)
            
            return response
        
        elif chat_count < 13:
            section = collection["Closing"]
            question_type = "Closing"
            count = None
            if chat_count == 11: 
                count = chat_count
            response = await helper_func(chat_count, count, question_type, section, data)
            
            return response

    except Exception as e:
        logger.error(f"Choosing question process failed: ${str(e)}")
        return {'error': str(e)}


#----------------------------------------- Helper Functions for Choosing Question ---------------------------------
async def helper_func(chat_count, count: int, question_type: str, section: list, data: dict):
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
                
        if chat_count < 12:
            if data['response']:
                if count is not None:
                    interview_question_json = await fetch_interview_question(section, question_type, data) 
                else:
                    response = await check_if_followup(data['response'])
         
                    if not response:
                        interview_question_json = await fetch_interview_question(section, question_type, data) 
                    else:
                        interview_question_json = await generate_followup(data)
                       
            else:
                interview_question_json = await fetch_interview_question(section, question_type, data) 
   
        else:  
            realtime_evaluation_response_json = realtime_response_evaluation(data)
            realtime_evaluation = "null" if realtime_evaluation_response_json is None else realtime_evaluation_response_json.get("realtime_evaluation")
            logger.info(f"Realtime evaluation is: {realtime_evaluation}")
            if realtime_evaluation != "null":
                status = "final"
                strapi.step3_insert_message(data, realtime_evaluation)

            await overall_interview_evaluations(data, status = "Completed")
            logger.info("Calculate the overall and save to database done.")            
                
        response = {
            "interview": interview_question_json,
            "status": status,
            "realtime": realtime_evaluation
        }
        
        return response
    
    except Exception as e:
        logger.error(f"Choosing question helper process failed: ${str(e)}")
        return {'error': str(e)}
   
   
#----------------------------------------- picking the right Question ----------------------------------------- 
async def fetch_interview_question(section: list, question_type: str, data: dict):
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
        if chat_count == 12:
            message = file_reader(prompt_path('ipersona/closing_question.txt'))
        else:
            message = file_reader(prompt_path('ipersona/pick_question.txt'))
       
        context = str(message)
        questions = []
        msg = context\
            .replace("{collection}", str(section))\
            .replace("{type}", str(question_type))\
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
        ipersona_message = IpersonaSessionMessageSchema()
        session_chathistory = ipersona_message.filter_by_session_id(
            sessionId=data['user_session']['id'], 
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
            
        if chat_count == 12:
            closing_evaluation_prompt = file_reader(prompt_path('ipersona/closing_question_realtime_evaluation.txt'))
            closing_question = "Before we wrap up the interview, do you have any questions you'd like to ask?"
            closing_content = closing_evaluation_prompt\
                .replace("{closing_question}", str(closing_question))\
                .replace("{candidate_response}" , str(data['response']))
                        
            realtime_evaluation_response = gpt.openai_gpt_assistant_without_streaming(closing_content)

            realtime_evaluation_response = extract_json(realtime_evaluation_response, quite=False) 
            return realtime_evaluation_response
        
        else:            
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
async def overall_interview_evaluations(data: dict, status) -> dict:
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
        ipersona_message = IpersonaSessionMessageSchema()
        all_chat_history = ipersona_message.filter_by_session_id(
            sessionId=data['user_session']['id'], 
            nopp=True, 
            dataframe=False,
            sort='asc')
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
                "i_persona_session": data['user_session']['id'],
                "status": status            
            }
        ipersona_observer = IpersonaSessionObserverSchema()
        save_observer = ipersona_observer.save_observer(params=overall_json, nopp=True, dataframe=False)
        ipersona_session = IpersonaSessionSchema()
        if save_observer:
            logger.info("session observer to database")

        session_data = {
            "i_persona_session_id": data['user_session']['id'], 
            "status": status,
        }
        
        updated_session = ipersona_session.update_session(params=session_data, nopp=True, dataframe=False, return_object=True)
        if updated_session:
            logger.info("session status updated to completed")
            
            #------------------------------------------------------------------------------------#
    
        ipersona_user = IpersonaTraineeSchema()

        trainee_profile_data = ipersona_user.filter_by_alluser_id(all_user_id=data['all_user_id'], nopp=True, dataframe=False)
        if not trainee_profile_data:
                logger.warn("No trainee user profiles found.")
                return []
        tinder_user_profile_id = trainee_profile_data['id'] 
                      
        session = ipersona_session.filter_by_with_user_job_id(user_profile_id=tinder_user_profile_id,job_profile_id=data['job_profile_id'], nopp=True, dataframe=False) 
        session_chatobserver = extract_observers_metrics(session)
        
        if status == 'Completed':         
            await calculate_overall_progress(data, session_chatobserver) 
      
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
async def calculate_overall_progress(userdata, data: list):
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
                            
        ipersona_overall = IpersonaSessionOverallObserverSchema()
        ipersona_user = IpersonaTraineeSchema()

        trainee_profile_data = ipersona_user.filter_by_alluser_id(all_user_id=userdata['all_user_id'], nopp=True, dataframe=False)
        if not trainee_profile_data:
                logger.warn("No trainee user profiles found.")
                return []
        tinder_user_profile_id = trainee_profile_data['id']    
            
        session_chatobserver = ipersona_overall.filter_by_with_user_and_job_id(user_profile_id=tinder_user_profile_id, job_profile_id=userdata['job_profile_id'], nopp=True, dataframe=False)

        if not session_chatobserver.get("error"): 
            logger.info(f"Session job overall observer data exists, so updating the data")          
      
            session_chatobserver_sessions = session_chatobserver['all_sessions']
            
            logger.info(f"Value of session_overall_observer_by_user_and_job: {len(session_chatobserver_sessions)}")
                
            if len(session_chatobserver_sessions) > 0:
                logger.info(f"Updating session job overall observer data")
                attributes = {
                    "overall_confidence": confidence_overtime,
                    "overall_clarity": clarity_overtime,
                    "overall_engagement": engagement_overtime,
                    "overall_time_management": overall_time_managements,
                    "overall_competency": overall_competencies,
                    "overall_performance": overall_performance_scores
                }
                            
                overall_data = {
                    "i_persona_session_overall_observer_id": session_chatobserver['id'], 
                    "attributes": attributes,
                }
                response = ipersona_overall.update_session(params=overall_data, nopp=True, dataframe=False, return_object=True)
                if response:
                    logger.success(f"session overall observer data update with new insert anlaysis")   
        else:  
            logger.info(f"Creating a new session job overall observer data")          
                    
            ipersona_overall = IpersonaSessionOverallObserverSchema()
            ipersona_user = IpersonaTraineeSchema()

            trainee_profile_data = ipersona_user.filter_by_alluser_id(all_user_id=userdata['all_user_id'], nopp=True, dataframe=False)
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
                "tinder_job_profile": userdata['job_profile_id']
            }
            
            response = ipersona_overall.save_Session_Overall_Observer(params=message_data, nopp=True, dataframe=False)
            logger.success(f"new entry make on session overall observer")
            return response
    
    except Exception as e:
        logger.error(f"Process failed: ${str(e)}")
        return f'Error: {str(e)}'  
    

#-------------- Entire User Session Progress Over All Types of Jobs ---------------
def all_session_jobs_average_metrics(data):
    try:
        if not isinstance(data, list) or len(data) == 0:
            raise ValueError("Data is empty or not in the expected list format")

        data = data[0]

        avg_confidence = calculate_average(data.get('overall_confidence', []))
        avg_clarity = calculate_average(data.get('overall_clarity', []))
        avg_engagment = calculate_average(data.get('overall_engagement', []))
        avg_time_management = calculate_average_time_management(data.get('overall_time_management', []))

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
def summarize_interviews(user_profile_id):  
    try:  
        # Fetch a particular user sessions
        ipersona_session = IpersonaSessionSchema()
        data = ipersona_session.filter_by_tinder_user_profile_id(user_profile_id=user_profile_id, nopp=True, dataframe=False)
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
                attributes = session.get('attributes', {})
                i_persona_observer = attributes.get('i_persona_observer', {}).get('data')
                if i_persona_observer is None:
                    incomplete_sessions_count += 1
                else:
                    complete_sessions_count += 1
                               
            total_score = sum(
                record.get('overall_performance_score', 0) for record in records if record.get('overall_performance_score') is not None
            )
            
            if total_score > 0:
                average_score = round(total_score / complete_sessions_count, 2) if complete_sessions_count > 0 else "N/A"
            else:
                average_score = 'Not Available'
            
            ipersona_job = IpersonaJobSchema()
            job_title_data = ipersona_job.filter_by_job_id(job_profile_id=job_profile_id, nopp=True, dataframe=False)
            
            if job_title_data and len(job_title_data) > 0:
                job_title = job_title_data[0]['attributes']['attributes'].get('title', 'Unknown Job Title')
            else:
                job_title = 'Unknown Job Title'

            tinder_user_profile_id = user_profile_id
            tinder_job_profile_id = job_profile_id

            ipersona_match = IpersonaSessionTinderUserJobMatchSchema()
            job_match_data = ipersona_match.filter_by_with_user_and_job_id(user_profile_id=tinder_user_profile_id, job_profile_id=tinder_job_profile_id, nopp=True, dataframe=False)
            
            ipersona_reaction = IpersonaSessionTinderUserReactionSchema()
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

        return summary_response
    except Exception as e:
        logger.error(f"Error processing files: {e}")
        return {'error': str(e)}
def extracted_needed_metrics(data):
    try:
        extracted_observers = []  
        
        for session in data:
            extracted_session = {}              
            # Extract session id
            extracted_session['session_id'] = session['id']
            
            # Get observer data
            observer_data = session['attributes'].get('i_persona_observer', {}).get('data')
     
            # Determine if the session is complete
            complete_status = observer_data is not None
            extracted_session['complete_status'] = complete_status  

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
            extracted_session['createdAt'] = session['attributes'].get('createdAt')
            extracted_session['job_profile_id'] = session['attributes']['tinder_job_profile']['data']['id']
            extracted_session['user_profile_id'] = session['attributes']['tinder_user_profile']['data']['id']
       
            # Append extracted session data
            extracted_observers.append(extracted_session)
        
        return extracted_observers  
    
    except Exception as e:
        logger.error(f"Error processing files: {e}")
        return {'error': str(e)}
# def extracted_needed_metrics(data):
#     try:
#         extracted_observers = []
        
#         for session in data:
#             observer_data = session['attributes'].get('i_persona_observer', {}).get('data')
#             # Extract necessary data if observer data exists
#             if observer_data:
#                 observer_attributes = observer_data.get('attributes', {}).get('attributes', {}).get('interview_evaluation_metrics', {})
#                 session['overall_performance_score'] = observer_attributes.get('overall_performance_score', None)
#             else:
#                 # Handle case where observer data does not exist
#                 session['not_found'] = True
#                 session['overall_performance_score'] = None

#             # Always assign job_profile_id and createdAt, even if observer data is missing
#             session['createdAt'] = session['attributes'].get('createdAt')
#             session['job_profile_id'] = session['attributes']['tinder_job_profile']['data']['id']
#             session['userprofileId'] = session['attributes']['tinder_user_profile']['data']['id']
#             extracted_observers.append(session)
        
#         return extracted_observers
#     except Exception as e:
#         logger.error(f"Error processing files: {e}")
#         return {'error': str(e)}

def extract_observers_metrics(data):
    try:
        extracted_observers = []
        for message in data:
            if message['attributes'].get('i_persona_observer') and message['attributes']['i_persona_observer'].get('data'):
                message_data = message['attributes']['i_persona_observer']['data']
                message_attributes = message_data['attributes']['attributes']['interview_evaluation_metrics']
                message_attributes['createdAt'] = message['attributes']['createdAt']
                message_attributes['obs_id'] = message['attributes']['i_persona_observer']['data']['id']
                extracted_observers.append(message_attributes)

        return extracted_observers
    except Exception as e:
        logger.error(f"Error processing files: {e}")
        return {'error': str(e)}
 
def extract_observers_metrics(data):
    try:
        extracted_observers = []
        for message in data:
            if message['attributes'].get('i_persona_observer') and message['attributes']['i_persona_observer'].get('data'):
                message_data = message['attributes']['i_persona_observer']['data']
                message_attributes = message_data['attributes']['attributes']['interview_evaluation_metrics']
                message_attributes['createdAt'] = message['attributes']['createdAt']
                message_attributes['obs_id'] = message['attributes']['i_persona_observer']['data']['id']
                extracted_observers.append(message_attributes)

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
        job_profile_frequency = []  
        user_profile_frequency = []  

        unique_job_profiles = set()
        unique_user_profiles = set()

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
            
            ipersona_job = IpersonaJobSchema()
            ipersona_user = IpersonaTraineeSchema()
            job_title_data = ipersona_job.filter_by_job_id(job_profile_id=job_profile_id, nopp=True, dataframe=False)

            alluserdata = ipersona_user.get_trainee_by_id(user_profile_id=user_profile_id, nopp=True, dataframe=False)

            all_user_id = alluserdata["attributes"]["all_users"]["data"][0]["id"]

            ipersona_alluser = IpersonaAllUserSchema()
            ipersona_alluser_data = ipersona_alluser.get_alluser_by_id(all_user_id = all_user_id, nopp=True, dataframe=False, return_object=True)

            ipersona_profile = IpersonaProfileInformationSchema()
            ipersona_profile_data = ipersona_profile.filter_by_all_user_id(all_user_id = all_user_id, nopp=True, dataframe=False, return_object=True)
            userdata = {**ipersona_alluser_data, **ipersona_profile_data}
      
            ipersona_reaction = IpersonaSessionTinderUserReactionSchema()
            reaction_id = ipersona_reaction.filter_by_with_user_and_job_id(user_profile_id=user_profile_id, job_profile_id=1533, nopp=True, dataframe=False)
          
            if job_title_data and len(job_title_data) > 0:
                job_title = job_title_data[0]['attributes']['attributes'].get('title', 'Unknown Job Title')
            else:
                job_title = 'Unknown Job Title'

            if not job_profile_id or not user_profile_id:
                logger.warn(f"Skipping session due to missing job/user profile: {session}")
                continue
            
            if job_profile_id not in unique_job_profiles:
                unique_job_profiles.add(job_profile_id)
                job_profile_count += 1
                job_profile_frequency.append({
                    'count': 1,
                    'job_title': job_title,
                    'job_profile_id': job_profile_id,
                    "reaction_id": reaction_id
                })
            else:
                for profile in job_profile_frequency:
                    if profile['job_profile_id'] == job_profile_id:
                        profile['count'] += 1
                        break

            if user_profile_id not in unique_user_profiles:
                unique_user_profiles.add(user_profile_id)
                user_profile_count += 1
                user_profile_frequency.append({
                    'count': 1,
                    'name': userdata['name'],
                    'user_profile_id': user_profile_id
                })
            else:
                for profile in user_profile_frequency:
                    if profile['user_profile_id'] == user_profile_id:
                        profile['count'] += 1
                        break

            i_persona_observer = attributes.get('i_persona_observer', {}).get('data')
            if i_persona_observer is None:
                incomplete_sessions += 1
            else:
                complete_sessions += 1

        job_profile_frequency = sorted(job_profile_frequency, key=lambda x: x['count'], reverse=True)
        user_profile_frequency = sorted(user_profile_frequency, key=lambda x: x['count'], reverse=True)
        total_session = complete_sessions + complete_sessions
        result = {
            'interviews_count': session_count,
            'job_profile_count': job_profile_count,
            'user_profile_count': user_profile_count,
            'complete_sessions': complete_sessions,
            'incomplete_sessions': complete_sessions,
            'total_interview_sessions': total_session
        }

        return result
    
    except Exception as e:
        logger.error(f"Error processing files: {e}")
        return {'error': str(e)}

def summarize_allusers_data(data):
    try:
        data = extracted_needed_metrics(data)  # Extract required metrics from the raw data
        user_summary = defaultdict(list)  # Dictionary to group records by user_profile_id

        for record in data:
            user_profile_id = record['user_profile_id']
            user_summary[user_profile_id].append(record)

        trainees_detailed_data = []

        for user_profile_id, records in user_summary.items():
            job_profile_ids = set()  
            complete_sessions_count = 0
            incomplete_sessions_count = 0
            total_interview_score = 0
            total_interviews_count = 0

            # Aggregating data for each user
            for record in records:
                job_profile_id = record['job_profile_id']
                job_profile_ids.add(job_profile_id)  
                
                if record.get('complete_status') is True:
                    complete_sessions_count += 1
                else:
                    incomplete_sessions_count += 1

                # if record.get('ovtrainees_detailed_dataerall_performance_score') is not None:
                # total_interview_score += record['overall_performance_score']
                
                total_interviews_count += 1 
                
                # average_score = round(total_interview_score / complete_sessions_count, 2) if complete_sessions_count > 0 else "N/A"
           
            # Fetching user details from strapi tables
            ipersona_user = IpersonaTraineeSchema()
            all_user_data = ipersona_user.get_trainee_by_id(user_profile_id=user_profile_id, nopp=True, dataframe=False, return_object=True)
            all_user_id = all_user_data.get('attributes', {}).get('all_users', {}).get('data', [{}])[0].get('id')

            ipersona_alluser = IpersonaAllUserSchema()
            ipersona_alluser_data = ipersona_alluser.get_alluser_by_id(all_user_id=all_user_id, nopp=True, dataframe=False, return_object=True)
            ipersona_profile = IpersonaProfileInformationSchema()
            ipersona_profile_data = ipersona_profile.filter_by_all_user_id(all_user_id=all_user_id, nopp=True, dataframe=False, return_object=True)

            userdata = {**ipersona_alluser_data, **ipersona_profile_data}

            # Appending aggregated data for each user
            trainees_detailed_data.append({
                "user_profile_id": user_profile_id,
                "all_user_id": all_user_id,
                "name": userdata.get('name', 'Unknown'),
                "role": userdata.get('role', 'Unknown'),
                "batch": userdata.get('Batch', 'Unknown'),
                "gender": userdata.get('gender', 'Unknown'),
                "nationality": userdata.get('nationality', 'Unknown'),
                "job_count": len(job_profile_ids),
                "total_interviews_count": total_interviews_count,
                "complete_sessions_count": complete_sessions_count,
                "incomplete_sessions_count": incomplete_sessions_count,
            })

        # Sorting the data by 'total_interviews_count' in descending order and taking top 10
        top_10 = sorted(trainees_detailed_data, key=lambda x: x['total_interviews_count'], reverse=True)[:10]

        result = {
            "alldata": trainees_detailed_data,  # All processed user data
            "top10": top_10  # Top 10 users by total interviews count
        }
        return result

    except Exception as e:
        logger.error(f"Error processing files: {e}")
        return {'error': str(e)}

def summarize_alljobs_data(data):
    try:
        data = extracted_needed_metrics(data)  # Extract necessary metrics from raw data
        job_summary = defaultdict(list)  # Group records by job_profile_id

        for record in data:
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
            ipersona_job = IpersonaJobSchema()
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

def summarize_allusers_performance_data(data):
    try: 
        data = extracted_needed_metrics(data)  # Assume this function extracts necessary metrics
        user_summary = defaultdict(list)  # Dictionary to group records by user_profile_id
        
        # Step 1: Group records by user_profile_id
        for record in data:
            user_profile_id = record['user_profile_id']
            user_summary[user_profile_id].append(record)

        user_metrics = []

        # Step 2: Iterate over each user and calculate the average of metrics
        for user_profile_id, records in user_summary.items():
            # Fetch user details from external data sources (Strapi)
            ipersona_user = IpersonaTraineeSchema()
            all_user_data = ipersona_user.get_trainee_by_id(user_profile_id=user_profile_id, nopp=True, dataframe=False, return_object=True)
            all_user_id = all_user_data.get('attributes', {}).get('all_users', {}).get('data', [{}])[0].get('id')

            ipersona_alluser = IpersonaAllUserSchema()
            ipersona_alluser_data = ipersona_alluser.get_alluser_by_id(all_user_id=all_user_id, nopp=True, dataframe=False, return_object=True)
            ipersona_profile = IpersonaProfileInformationSchema()
            ipersona_profile_data = ipersona_profile.filter_by_all_user_id(all_user_id=all_user_id, nopp=True, dataframe=False, return_object=True)
            userdata = {**ipersona_alluser_data, **ipersona_profile_data}

            # Step 3: Initialize sum variables
            total_confidence = 0
            total_clarity = 0
            total_engagement = 0
            record_count = len(records)

            # Step 4: Iterate over records and sum up the metrics
            for item in records:
                confidence = item.get('confidence', '').lower() if item.get('confidence') else ''
                clarity = item.get('clarity', '').lower() if item.get('clarity') else ''
                engagement = item.get('engagement', '').lower() if item.get('engagement') else ''
                
                confidence_level = 1 if confidence == 'poor' else 2 if confidence == 'good' else 3 if confidence == 'excellent' else 0
                clarity_level = 1 if clarity == 'poor' else 2 if clarity == 'good' else 3 if clarity == 'excellent' else 0
                engagement_level = 1 if engagement == 'poor' else 2 if engagement == 'good' else 3 if engagement == 'excellent' else 0

                # Sum the metrics
                total_confidence += confidence_level
                total_clarity += clarity_level
                total_engagement += engagement_level

            # Step 5: Calculate averages and handle record_count == 0 case
            avg_confidence = round(total_confidence / record_count, 2) if record_count else 0
            avg_clarity = round(total_clarity / record_count, 2) if record_count else 0
            avg_engagement = round(total_engagement / record_count, 2) if record_count else 0

            # Step 6: Prepare the summarized user data
            user_data = {
                "user_profile_id": user_profile_id,
                "all_user_id": all_user_id,
                "name": userdata.get('name', 'Unknown'),
                "role": userdata.get('role', 'Unknown'),
                "batch": userdata.get('Batch', 'Unknown'),
                "gender": userdata.get('gender', 'Unknown'),
                "nationality": userdata.get('nationality', 'Unknown'),
                'metrics': {
                    'average_confidence_level': avg_confidence if avg_confidence != 0 else None,
                    'average_clarity_level': avg_clarity if avg_clarity != 0 else None,
                    'average_engagement_level': avg_engagement if avg_engagement != 0 else None,
                }
            }

            user_metrics.append(user_data)

        return user_metrics

    except Exception as e:
        logger.error(f"Error processing files: {e}")
        return {'error': str(e)}

#-------------------------------------------- FIle reader --------------------------------------------
def convert_iso_to_readable_format(iso_time):
    try:
        dt = datetime.strptime(iso_time, '%Y-%m-%dT%H:%M:%S.%fZ')    
        readable_time = dt.strftime('%d %b %Y %I:%M %p')
        return readable_time
    except Exception as e:
        logger.error(f"Error processing files: {e}")
        return {'error': str(e)}

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