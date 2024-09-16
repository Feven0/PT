
import openai
import json, os, re, ast
import pdfplumber
import os
import json_repair
from collections import defaultdict
from api.llm.ipersona.ipersona_agent import agents

from dotenv import load_dotenv
load_dotenv(os.path.abspath("../.env"))
print("Not a thing girl")
print(os.getenv('OPENAI_API_KEY'))


OPENAI_API_KEY = "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"
# openai.api_key = os.environ.get('OPENAI_API_KEY')
openai_client = openai.OpenAI(api_key = OPENAI_API_KEY)


module_dir= os.path.dirname(__file__)
prompt_path = lambda x: os.path.join(module_dir, "prompts", x)
data_path = lambda x: os.path.join(module_dir, "data", x)


hr_agent = agents()

def give_agents_history(user_proxy, assistant, history):
   
    user_proxy_history_dict = defaultdict(list, {
    user_proxy: history
    })
    assistant_history_dict = defaultdict(list, {
        assistant: history
    })

   
    assistant._oai_messages = user_proxy_history_dict
    user_proxy._oai_messages = assistant_history_dict

def create_persona(sample_jd):
   
    try:

        persona_class_prompts = data_path("Geminigenerated.json") 
        classes = json.loads(read_file(data_path("persona_class.txt")))       
        class_prompts = json.loads(read_file(persona_class_prompts))       
        x = identify_class(classes, sample_jd)
        persona1 = ""
        for key in x:
            persona1 += key + ": "
            persona1 += class_prompts[key][x[key]] + "\n"
        
        return persona1

    except Exception as e:
            return f'Error: {str(e)}' 
        
        
async def analysing_vitae(recieved,  jbPath):
    try:
        created_persona = create_persona(jbPath)
        prompt_text = file_reader(prompt_path('ipersona/persona.txt'))
        generated_persona = prompt_text.replace("{hr_persona}", created_persona)   
        hr_agent.assistant.update_system_message(generated_persona)
        message = file_reader(prompt_path('ipersona/analysis.txt'))
        context = str(message)
        msg = context\
                .replace("{jd}", file_reader(jbPath))\
                .replace("{cv}", file_reader(recieved.cvPath))
                
        response = await hr_agent.send_message_analyser(msg)    
        response = extract_json(response, quite=False)
        data ={
            "generated_persona": generated_persona,
            "response": response
        }
        return data
    
    except Exception as e:
        return f'Error: {str(e)}' 
        
        
async def analysis_chat_response(data):
   
    try:
        
        hr_agent.assistant.update_system_message(data['user']['persona'])

        message = file_reader(prompt_path('ipersona/chat_analysis_prompt.txt'))
        context = str(message)
        msg=context\
            .replace("{jd}", file_reader(data['user']['jbPath']))\
            .replace("{cv}", file_reader(data['cvPath']))\
            .replace("{question}", data['message'])
        
        response = await hr_agent.send_message_analyser(msg)
        return response
  
    except Exception as e:
        return f'Error: {str(e)}' 
    

async def interview_chat_response(data):
  
    try:
        
        hr_agent.assistant.update_system_message(data['user']['persona'])
      
        message = file_reader(prompt_path("ipersona/interview.txt"))
        context = str(message)
        history_str = '\n'.join(str(item) for item in data['history'])
        msg=context\
            .replace("{jd}", file_reader(data['user']['jbPath']))\
            .replace("{cv}", file_reader(data['cvPath']))\
            .replace("{history}", history_str)\
            .replace("{candidate_response}", data['response'])\
            .replace("{counter}", str(data['question_counter']))
        
        # give_agents_history(hr_agent.interviewer_proxy, hr_agent.assistant, data['history'])

        response = await hr_agent.send_message_interview(msg)
        # response = extract_percentage(response)
        return response
    
    except Exception as e:
        return f'Error: {str(e)}' 
    

def file_reader(path: str) -> str:
    
    try:
       
        fname = os.path.join(path)
        with open(fname, 'r') as f:
            system_message = f.read()
        return system_message
    
    except Exception as e:
        return f'Error: {str(e)}'
    
    
def extract_percentage(data):
   
    try:
       
        start = data.find('"percentage":')
        if start == -1:
            start = data.find("percentage:")
        if start == -1:
            start = data.find("percentage is")
        if start == -1:
            start = data.find("Performance Percentage:")
        print("dd", start)
        if start != -1:
            percentage_match = re.search(r"\d+", data[start:])
            if percentage_match:
                percentage = int(percentage_match.group())
                analysis = data[:start].strip()
            else:
                analysis = data.strip()
                percentage = None
        else:
            analysis = data.strip()
            percentage = None
        output = {
            "percentage": f"{percentage}%",
            "analysis": analysis            
        }
        return output
    
    except Exception as e:
        return f'Error: {str(e)}'
    
      
def read_file(file_name):
  try:
   
    with open(file_name, 'r') as file:
      contents = file.read()

    return contents
  
  except Exception as e:
        return f'Error: {str(e)}'


def pdf_to_txt(pdf_file, output_file):
    try:
        with pdfplumber.open(pdf_file) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text()
        with open(output_file, "w", encoding="utf-8") as file:
            file.write(text)

        print(f"PDF file '{pdf_file}' converted to '{output_file}'.")
    except Exception as e:
        print(f"Error converting PDF file: {e}")


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
    
    
    
    
    
