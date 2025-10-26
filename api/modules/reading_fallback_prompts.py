import os
import api.modules.ipersona_parrot_gpt as util

module_dir= os.path.dirname(__file__)
prompt_path = lambda x: os.path.join(module_dir, "prompts", x)

def read_prompt_data_for_challenge_default(challenge_data):
    prompt_text = util.file_reader(prompt_path('ipersona/generate_challenge_question_default.txt'))
    # content = await util.analysis_challenge(challenge_id)
    challenge_prompt = prompt_text \
        .replace("{challenge_document}", str(challenge_data)) \
        .replace("{count}", str(5))
        
    return challenge_prompt

def read_prompt_data_for_challenge(json_format, count, challenge_data):
    prompt_text = util.file_reader(prompt_path('ipersona/generate_challenge_question.txt'))
    # content = await util.analysis_challenge(challenge_id)
    challenge_prompt = prompt_text \
        .replace("{challenge_document}", str(challenge_data)) \
        .replace("{count}", str(count)) \
        .replace("{json}", str(json_format))
        
    return challenge_prompt

def read_prompt_data_for_template(tinder_job_data):
    prompt_text = util.file_reader(prompt_path('ipersona/persona.txt'))
    created_persona = util.create_persona(str(tinder_job_data))

    generated_persona = prompt_text \
        .replace("{hr_persona}", created_persona) \
        .replace("{job_description}", str(tinder_job_data)) 
        
    return generated_persona

def read_prompt_persona(tinder_job_data, tinder_user_profile_data):
    prompt_text = util.file_reader(prompt_path('ipersona/persona.txt'))
    created_persona = util.create_persona(str(tinder_job_data))
    generated_persona = prompt_text \
        .replace("{hr_persona}", created_persona) \
        .replace("{job_description}", str(tinder_job_data))  \
        .replace("{profile}", str(tinder_user_profile_data))
    return generated_persona
    
def read_prompt_data_for_default():
    question_template = util.file_reader(prompt_path('ipersona/generate_question_default.txt'))
    msg = question_template \
        .replace("{introduction_count}", str(1)) \
        .replace("{background_count}", str(1)) \
        .replace("{technical_count}", str(1)) \
        .replace("{behavioral_count}", str(1)) \
        .replace("{ability_count}", str(1))\
        .replace("{closing_count}", str(1))
        
    return msg

def read_external_audio_analysis(transcript):
    external_audio_prompt = util.file_reader(prompt_path('external_audio_analysis.txt'))
    realtime_prompt = util.file_reader(prompt_path('realtime_evaluation.txt'))
    external_aud_prompt = external_audio_prompt \
                .replace("{transcription}", str(transcript)) \
                .replace("{realtime}", str(realtime_prompt))
     
    return external_aud_prompt

def read_prompt_clarify(question):
    message = util.file_reader(prompt_path("ipersona/clarify_question.txt"))
    context = str(message)
    clarify_prompt = context.replace("{question}", question)
        
    return clarify_prompt

def read_prompt_time_limit_generator(question):
    message = util.file_reader(prompt_path('ipersona/time_limit_generator.txt'))
    context = str(message)
    time_limit_prompt = context\
            .replace("{question}", question)     
        
    return time_limit_prompt

def read_prompt_realtime_evaluation(data, last_assistant_response):
    evaluation_prompt = util.file_reader(prompt_path('ipersona/realtime_evaluation.txt'))            
    evaluation_context = str(evaluation_prompt)
    realtime_evaluation_msg = evaluation_context\
        .replace("{question}", last_assistant_response)\
        .replace("{candidate_response}", str(data['response'] or ''))

    return realtime_evaluation_msg

def read_prompt_overall_evaluation(history_str):
    overall_evaluation_prompt = util.file_reader(prompt_path('ipersona/overall_evaluation.txt'))
    overall_evaluation_context = str(overall_evaluation_prompt)
    overall_evaluation_msg = overall_evaluation_context\
        .replace("{history}", history_str)  
    
    return overall_evaluation_msg

def read_prompt_interview_evaluation_metrics(history_str):
        overall_metrics_prompt = util.file_reader(prompt_path("ipersona/interview_metrics_rubrics.txt"))
        overall_metrics_context = str(overall_metrics_prompt)
                
        overall_metrics_msg = overall_metrics_context\
            .replace("{history}", history_str) 
        
        return overall_metrics_msg

def read_prompt_followup_checker(candidate_response):
    message = util.file_reader(prompt_path('ipersona/follow_up_check.txt'))
    context = str(message)
    msg = context.replace("{candidate_response}", candidate_response) 
    
    return msg

def read_prompt_followup_question_generator(candidate_response):
    message = util.file_reader(prompt_path('ipersona/follow_up.txt'))
    context = str(message)
    msg = context.replace("{candidate_response}", candidate_response)
    
    return msg

def read_prompt_interview_closing():
    message = util.file_reader(prompt_path('ipersona/closing_question.txt'))
    return message

def read_prompt_pick_interview_question():
    message = util.file_reader(prompt_path('ipersona/pick_question.txt'))
    return message

def read_prompt_closing_question_realtime_evaluation(data, last_assistant_response):
    closing_evaluation_prompt = util.file_reader(prompt_path('ipersona/closing_question_realtime_evaluation.txt'))          
    closing_evaluation_context = str(closing_evaluation_prompt)
    closing_realtime_evaluation_msg = closing_evaluation_context\
        .replace("{question}", last_assistant_response)\
        .replace("{candidate_response}", str(data['response'] or ''))

    return closing_realtime_evaluation_msg