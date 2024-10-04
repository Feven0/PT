
from openai import OpenAI
import json, os, re, ast
import os
import json_repair
from collections import defaultdict
from api.llm.ipersona.ipersona_agent import agents
import api.llm.ipersona.ipersona_db as database

from api.config import get_openapi_token


########
keys_json  = get_openapi_token(ssmkey="tenx/env/vars", envvar="OPENAI_API_KEY", fconfig=".env/openai_apikey.json")
OPENAI_API_KEY = keys_json['OPENAI_PARROT_API_KEY']

openai_client = OpenAI(api_key = OPENAI_API_KEY)


module_dir= os.path.dirname(__file__)
prompt_path = lambda x: os.path.join(module_dir, "prompts", x)
data_path = lambda x: os.path.join(module_dir, "data", x)



hr_agent = agents()

################################################# create persona #############################################
def create_persona(sample_jd):
   
    try:

        persona_class_prompts = data_path("Geminigenerated.json") 
        classes = json.loads(file_reader(data_path("persona_class.txt")))       
        class_prompts = json.loads(file_reader(persona_class_prompts))       
        x = identify_class(classes, sample_jd)
        persona1 = ""
        for key in x:
            persona1 += key + ": "
            persona1 += class_prompts[key][x[key]] + "\n"
        
        return persona1

    except Exception as e:
            return f'Error: {str(e)}'             


###########################################  Generate Interview Questions ###################################
async def generate_interview_question(data):
   
    try:
        
        hr_agent.assistant.update_system_message(data['user_session']['persona'])   
        response = await choose_interview_question(data['user_session']['generated_questions'], data)
        return response
    
    except Exception as e:
        return f'Error: {str(e)}' 
    
    
###########################################  Choose Question from Generated ###################################
async def choose_interview_question(collection, data):
    try: 
        section = None
        question_type = None
        if(data['question_counter'] < 3):
            section = collection["Background"]
            question_type = "Background"
            count = None
            response = await helper_func(count, question_type, section, data)
            return response
        
        elif(data['question_counter'] < 5):
            print("skill assessment question")
            section = collection["Technical"]
            question_type = "Technical"
            count = None
            if(data['question_counter'] == 3):
                count = data['question_counter']
                response = await helper_func(count, question_type, section, data)
            else:
                response = await helper_func(count, question_type, section, data)
            return response
            
        elif(data['question_counter'] < 7):
            print("behavioral question")
            section = collection["Behavioral"]
            question_type = "Behavioral"
            count = None
            if(data['question_counter'] == 5):
                count = data['question_counter']
                response = await helper_func(count, question_type, section, data)
            else:
                response = await helper_func(count, question_type, section, data)
                
            return response
        
        elif(data['question_counter'] < 10): 
            print("ability question")
            section = collection["Ability"]
            question_type = "Ability"
            count = None
            if(data['question_counter'] == 7):
                count = data['question_counter']
                response = await helper_func(count, question_type, section, data)
            else:
                response = await helper_func(count, question_type, section, data)
                
            return response

    except Exception as e:
        return f'Error: {str(e)}' 


########################################### Helper Functions for Choosing Question ###################################
async def helper_func(count, question_type, section, data): 
    try:
        realtime_evaluation_response_json = None
        overall_evaluation_response_json = None  
        interview_question_json = None
        overall_interview_metrics_json = None   
        
        if(data['question_counter'] < 9):
            if data['response']:
                if(count != None):
                    realtime_evaluation_response_json = await realtime_response_evaluation(data)
                    interview_question_json = await fetch_interview_question(section, data) 
                else:
                    print("candidate response exists")  
                    # realtime evaluation here
                    realtime_evaluation_response_json = await realtime_response_evaluation(data)
                    response = await check_if_followup(data['response'])
                    if response == False:
                        interview_question_json = await fetch_interview_question(section, data) 
                    else:
                        interview_question_json = await generate_followup(data['response'])
            else:
                print("candidate response does not exists") 
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
            # overall evaluations here
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
        return f'Error: {str(e)}' 
    
    
########################################### picking the right Question ###################################
async def fetch_interview_question(section, data):
    try:
        message = file_reader(prompt_path('ipersona/prompt/pick_question.txt'))
        context = str(message)
        questions = []
        msg=context\
            .replace("{collection}", str(section))\
            .replace("{questions}", str(questions))\
            .replace("{candidate_response}", data['response'])        

        response = await hr_agent.generate_question(msg)
        response_json = extract_json(response, quite=False)
        
        return response_json     

    except Exception as e:
        return f'Error: {str(e)}' 
    
 
########################################### Follow up Question Checker ###################################
async def check_if_followup(candidate_response):
    try:
        message = file_reader(prompt_path('ipersona/prompt/follow_up_check.txt'))

        context = str(message)
        msg=context\
            .replace("{candidate_response}", candidate_response) 
             
        response = await hr_agent.generate_question(msg)
        response_json = extract_json(response, quite=False)

        return response_json["follow-up"]
    
    except Exception as e:
        return f'Error: {str(e)}' 
    
    
########################################### Generate Follow up Question ###################################
async def generate_followup(candidate_response):
    try:
        message = file_reader(prompt_path('ipersona/prompt/follow_up.txt'))
        context = str(message)
        msg=context\
            .replace("{candidate_response}", candidate_response)
        response = await hr_agent.generate_question(msg)
        response_json = extract_json(response, quite=False)
        response_json['interview_question']['end_message'] = "Please take your time to provide a detailed response"
        
        return response_json
    
    except Exception as e:
        return f'Error: {str(e)}'   


######################################### Realtime Chat Evaluation Function ###################################
async def realtime_response_evaluation(data):
    try:
        evaluation_prompt = file_reader(prompt_path('ipersona/prompt/evaluation.txt'))
        evaluation_context = str(evaluation_prompt)
        evaluation_msg = evaluation_context\
                .replace("{question}", data["previous_question"])\
                .replace("{candidate_response}", data['response'])
                
        # Evaluate the realtime chat response for the last response
        realtime_evaluation_response = await hr_agent.evaluate_candidate_response(evaluation_msg)
        realtime_evaluation_response = extract_json(realtime_evaluation_response, quite=False)
        print("real time evaluation response...", realtime_evaluation_response)  
        
        return realtime_evaluation_response
        
    except Exception as e:
        return f'Error: {str(e)}'   
    
    
######################################### Overall Interview Evaluation ###################################
async def overall_interview_evaluations(data, realtime_evaluation_response_json):
    try:
        overall_evaluation_prompt = file_reader(prompt_path('ipersona/prompt/overall.txt'))
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
        message = [{ "candidate": {"response": data['response'],"time_taken": data['time_taken']}},
                       {"assistant": {"response": "null", "realtime_evaluation": realtime_evaluation_response_json["realtime_evaluation"], "overall_evaluation": overall_evaluation_response_json["overall_evaluation"], "metrics": "null",
                      }}]        
        data['history'].extend(message)
        
        time_array = calculate_time(data['history'])
        relevancy= filter_the_relevancies(data['history'])
        percent_term = percentage_term(relevancy["average"])
        overall_interview_metrics_json ["evaluation_metrics"]["time_management"] = time_array
        overall_interview_metrics_json["evaluation_metrics"]["relevancy"] = relevancy["relevancy"]
        overall_evaluation_response_json["overall_evaluation"]["overall_performance"] = relevancy["average"]
        overall_evaluation_response_json["overall_evaluation"]["message"] = percent_term["term"]
        overall_interview_metrics_json["evaluation_metrics"]["message"] = percent_term["term"]
        overall_interview_metrics_json["evaluation_metrics"]["rating"] = percent_term["rating"]
        
        
        ############################## Save final chat history to weaviate ##########################################
        temp = data['history'][len(data['history'])-1]
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
        return f'Error: {str(e)}'   
                  

######################################## Interview Question Clarification ###################################
async def clarify_question(question):
    try:
        message = file_reader(prompt_path("ipersona/prompt/clarify_question.txt"))
        context = str(message)
        msg=context.replace("{question}", question)
        response = await hr_agent.interview_question_clarification(msg)
        response = extract_json(response, quite=False)
    
        return response
    
    except Exception as e:
        return f'Error: {str(e)}'    


########################################### FIle reader ###################################
def file_reader(path: str) -> str:
    
    try:
       
        fname = os.path.join(path)
        with open(fname, 'r') as f:
            system_message = f.read()
        return system_message
    
    except Exception as e:
        return f'Error: {str(e)}'  
      
def read_file(file_name):
  try:
   
    with open(file_name, 'r') as file:
      contents = file.read()

    return contents
  
  except Exception as e:
        return f'Error: {str(e)}'


########################################### Job Description Class Identifier ###################################
def identify_class(all_class, jd):
  
  try:
  
    result = openai_client.chat.completions.create(model="gpt-4o-mini", messages=[
            {
                "role": "user",
                "content": f"I need you to give to which class this JD belongs to classes. The types should be only be one for each class. If the JD holds more types then decide the one the can hold others {str(all_class)} JD: {jd} as json",
            }
        ],response_format={"type": "json_object"},
                                                    )
    return json.loads(result.choices[0].message.content)
  
  except Exception as e:
            return f'Error: {str(e)}' 
   

########################################### Json Extraction ###################################
def extract_json(response, quite=False):    
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
    

########################################### Helper function for Time Function ###################################
def time_to_seconds(time_str):
    """Convert time in 'HH:MM' format to seconds."""
    if time_str == "00:00":
        return 0
    h, m = map(int, time_str.split(':'))
    return h * 3600 + m * 60


########################################### Overall Time Data Calculator ###################################
def calculate_time(interview):
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
                            print(f"Candidate's time ({time_taken}) exceeds the time limit ({time_limit}).")
                            exceeded_count += 1
                        else:
                            print(f"Candidate's time ({time_taken}) is within the time limit ({time_limit}).")
                            not_exceeded_count += 1
        time_data = {
            "fail": exceeded_count,
            "pass": not_exceeded_count
        }
        return time_data
    
    except Exception as e:
            return f'Error: {str(e)}' 
    
    
################################# Overall Answer Relevancy Data Calculator ###############################
def filter_the_relevancies(data):
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
        average_relevancy = sum(levels) / len(levels) 
        data = {
            "relevancy": relevancy,
            "average": average_relevancy
        }
        return data
    
    except Exception as e:
            return f'Error: {str(e)}' 


######################################### Assigning Rating Metrics Value Range ###################################
def percentage_term(percent):
    try:
        if not isinstance(percent, (int, float)):
            return 'Invalid input'  

        if percent < 0 or percent > 100:
            return 'Invalid input'  

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
        return f'Error: {str(e)}'


######################################### Entire Data Progress Calculator ###################################
def calculate_overall_progress(data):
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
            
            # restructure communication skills
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
        return f'Error: {str(e)}' 
    

####################################### Entire Data Progress Metrics Extraction ###################################
def extract_necessary_metrics(data):
    overall_time_management= []
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
                                
                    if "assistant" in entry:
                        assistant_eval = entry["assistant"]                
                        if "overall_evaluation" in assistant_eval:
                            overall_evaluation = assistant_eval["overall_evaluation"]
                            if "competency" in overall_evaluation:
                                competency = overall_evaluation["competency"]
                                overall_competency.append(competency)
                            if isinstance(overall_evaluation, dict):                            
                                overall_eval_performance= overall_evaluation.get("overall_performance")
                                performance = {
                                    "interview": index,
                                    "performance": overall_eval_performance
                                }
                                overall_performance.append(performance)
    
    # restructuring time management data
    time_management = restructure_communication_skills_for_vis(overall_time_management)


    response ={
        "overall_time_management": time_management,
        "overall_competency": overall_competency,
        "overall_performance": overall_performance
    }    
    
    return response    


##################### Restructuring Communication skills format For Visualization ######################
def restructure_communication_skills_for_vis(data):
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
        return f'Error: {str(e)}' 
