'''
-----------------------------------------------------------------------
File: LLM.py
Creation Time: Nov 1st 2023 1:40 am
Author: Saurabh Zinjad
Developer Email: zinjadsaurabh1997@gmail.com
Copyright (c) 2023 Saurabh Zinjad. All rights reserved | GitHub: Ztrimus
-----------------------------------------------------------------------
'''
import os
import json
import textwrap
import pandas as pd
from autogen import AssistantAgent, UserProxyAgent
from openai import OpenAI
import google.generativeai as genai

#
from api import config
from api.llm.utils.llm_parse import extract_json
from api.llm.utils.token_counter import count_token
from api.utils.logger import LLPackerLogger

logger = LLPackerLogger(os.path.basename(__file__))

class ChatGPT:
    def __init__(self, api_key, system_prompt, 
                 chat_model="gpt-4o-mini", 
                 embedding_model='text-embedding-3-small'):
        self.chat_model = chat_model
        self.embedding_model = embedding_model
        if system_prompt.strip():
            self.system_prompt = {"role": "system", "content": system_prompt}
        else:
            self.system_prompt = ""
        self.client = OpenAI(api_key=api_key)
    
    def get_price(self, input=1, output=1, napi=1, chat=True, pmap={}):
        """Gets the price of a single OpenAI API call for a given model."""

        if not pmap:
            #Chat gpt-40
            #"Input/1k Tokens": "$0.005",
            #"Output/1k Tokens": "$0.015",
            #"Per Call": "$0.0080",
            #Text-Embedding-3-Small
            #"Model": "3 Small",
            #"Context": "$0.00002",
            #"Input/1k Tokens": "$0.0000",
            #"Output/1k Tokens": "$0.00"            
            pmap = {
                'gpt-4o-mini': lambda x, y, z: x*0.15/1000000 + y*0.6/1000000,
                'gpt-4o': lambda x, y, z: x*0.005/1000 + y*0.015/1000,
                'text-embedding-3-small': lambda x, y, z: x*0.00002 + y*0.0000/1000
            }
        
        if chat:
            model_name = self.chat_model
            price = pmap[model_name](input, output, napi)
        else:
            model_name = self.embedding_model
            price = pmap[model_name](input, output, napi)
            
        return price
    
    
    def get_response(self, prompt, expecting_longer_output=False, need_json_output=False, model=""):
        ntoken = count_token(prompt)
        
        print(f'-----------> Calling OpenAI Completion API with model={self.chat_model}: ')
        logger.info(f"----**----->  Input Token Count: {ntoken}")
        
        user_prompt = {"role": "user", "content": prompt}
        message = []
        if self.system_prompt:
            message.append(self.system_prompt)
            
        if prompt:
            message.append(user_prompt)
            
        if not message:
            logger.error("No message to send to OpenAI API")
            return None
        
        if model == "":
            model = self.chat_model
            
        try:
            # TODO: Decide value(temperature, top_p, max_tokens, stop) to get apt response
            completion = self.client.chat.completions.create(
                model=model,
                messages = message,
                temperature=0,
                max_tokens = 4000 if expecting_longer_output else None,
                response_format = { "type": "json_object" } if need_json_output else None
            )
            
            # "usage": {
            #     "prompt_tokens": 13,
            #     "completion_tokens": 7,
            #     "total_tokens": 20
            # },
            try:
                usage = completion.usage
                price = self.get_price(input=usage.prompt_tokens, 
                                    output=usage.completion_tokens, 
                                    napi=1)
                
                logger.info(f"-----******----> Token Usage: {usage.model_dump_json()}")
                logger.info(f"-----******----> Total Cost: ${price} USD")
            except:
                print("Error in getting usage and price")
                print(type(completion))
                print(dir(completion))
                print(completion)
                
            response = completion.choices[0].message
            
            content = response.content.strip()
            
            print('-----------------------> ')
            
            if need_json_output:
                return extract_json(content)
            else:
                return content
        
        except Exception as e:
            print(e)
            print(f"Error in OpenAI API, {e}")
            raise
    
    def get_embedding(self, text, model="", task_type="retrieval_document"):
        if model == "":
            model = self.embedding_model
            
        try:
            text = text.replace("\n", " ")
            return self.client.embeddings.create(input = [text], model=model).data[0].embedding
        except Exception as e:
            print(e)


class chatgpt_assistance:

    def __init__(self, api_key, system_prompt, name = "cv_assistant",
                 chat_model="gpt-4o", 
                 embedding_model='text-embedding-3-small'):
        self.chat_model = chat_model
        self.embedding_model = embedding_model
        if system_prompt.strip():
            self.system_prompt = {"role": "system", "content": system_prompt}
        else:
            self.system_prompt = ""
        self.client = OpenAI(api_key=api_key)
    
    def get_price(self, input=1, output=1, napi=1, chat=True, pmap={}):
        """Gets the price of a single OpenAI API call for a given model."""

        if not pmap:
            #Chat gpt-40
            #"Input/1k Tokens": "$0.005",
            #"Output/1k Tokens": "$0.015",
            #"Per Call": "$0.0080",
            #Text-Embedding-3-Small
            #"Model": "3 Small",
            #"Context": "$0.00002",
            #"Input/1k Tokens": "$0.0000",
            #"Output/1k Tokens": "$0.00"            
            pmap = {
                'gpt-4o': lambda x, y, z: x*0.005/1000 + y*0.015/1000,
                'text-embedding-3-small': lambda x, y, z: x*0.00002 + y*0.0000/1000
            }
        
        if chat:
            model_name = self.chat_model
            price = pmap[model_name](input, output, napi)
        else:
            model_name = self.embedding_model
            price = pmap[model_name](input, output, napi)
            
        return price
    
    
    def get_response(self, prompt, expecting_longer_output=False, need_json_output=False, model=""):
        ntoken = count_token(prompt)
        
        print('-----------------------> Calling OpenAI Assistant API: ')
        logger.info(f"----**----->  Input Token Count: {ntoken}")
        
        user_prompt = {"role": "user", "content": prompt}
        message = []
        if self.system_prompt:
            message.append(self.system_prompt)
            
        if prompt:
            message.append(user_prompt)
            
        if not message:
            logger.error("No message to send to OpenAI API")
            return None
        
        if model == "":
            model = self.chat_model
            
        try:
            # TODO: Decide value(temperature, top_p, max_tokens, stop) to get apt response
            assistant = self.client.beta.assistants.create(
                name = "cv_assistant",
                tools = [{"type": "code_interpreter"}],
                model=model,
                messages = message,
                temperature=0,
                max_tokens = 4000 if expecting_longer_output else None,
                response_format = { "type": "json_object" } if need_json_output else None
            )

            #TODO create thread and vector store

            # "usage": {
            #     "prompt_tokens": 13,
            #     "completion_tokens": 7,
            #     "total_tokens": 20
            # },
            try:
                usage = assistant.usage
                price = self.get_price(input=usage.prompt_tokens, 
                                    output=usage.completion_tokens, 
                                    napi=1)
                
                logger.info(f"-----******----> Token Usage: {usage.model_dump_json()}")
                logger.info(f"-----******----> Total Cost: ${price} USD")
            except:
                print("Error in getting usage and price")
                print(type(assistant))
                print(dir(assistant))
                print(assistant)
                
            response = assistant.choices[0].message
            
            content = response.content.strip()
            
            print('-----------------------> ')
            
            if need_json_output:
                return extract_json(content)
            else:
                return content
        
        except Exception as e:
            print(e)
            print(f"Error in OpenAI API, {e}")
            raise
    
    def get_embedding(self, text, model="", task_type="retrieval_document"):
        if model == "":
            model = self.embedding_model
            
        try:
            text = text.replace("\n", " ")
            return self.client.embeddings.create(input = [text], model=model).data[0].embedding
        except Exception as e:
            print(e)


class Gemini:
    # TODO: Test and Improve support for Gemini API
    def __init__(self, api_key, system_prompt):
        genai.configure(api_key=api_key)
        self.system_prompt = "System Prompt\n======\n" + system_prompt if system_prompt.strip() else ""
    
    def get_response(self, prompt, expecting_longer_output=False, need_json_output=False):
        try:
            user_prompt = "\n\nUser Prompt\n======\n" + prompt
            entire_prompt = self.system_prompt + user_prompt
            
            model = genai.GenerativeModel('gemini-pro')
            content = model.generate_content(
                entire_prompt,
                generation_config={
                    "temperature": 0.7,
                    "max_output_tokens": 4000 if expecting_longer_output else None,
                    }
                )

            if need_json_output:
                result = extract_json(content.text)
            else:
                result = content.text
            

            return result
        
        except Exception as e:
            print(e)
            print(f"Error in Gemini API, {e}")
            return None
    
    def get_embedding(self, content, model="models/embedding-001", task_type="retrieval_document"):
        try:
            def embed_fn(data):
                result = genai.embed_content(
                    model=model,
                    content=data,
                    task_type=task_type,
                    title="Embedding of json text" if task_type in ["retrieval_document", "document"] else None)
                
                return result['embedding']
            
            df = pd.DataFrame(content)
            df.columns = ['chunk']
            df['embedding'] = df.apply(lambda row: embed_fn(row['chunk']), axis=1)
            
            return df
        
        except Exception as e:
            print(e)


class TogetherAI:
    def __init__(self, api_key, system_prompt):
        self.system_prompt = {"role": "system", "content": system_prompt}
        self.client = OpenAI(
            api_key=api_key,
            base_url='https://api.together.xyz',
        )
    
    def get_response(self, prompt, expecting_longer_output=False, need_json_output=False):
        user_prompt = {"role": "user", "content": prompt}

        try:
            if expecting_longer_output:
                completion = self.client.chat.completions.create(
                    model="mistralai/Mistral-7B-Instruct-v0.2",
                    messages = [self.system_prompt, user_prompt],
                    max_tokens = 7000,
                )
            else:
                completion = self.client.chat.completions.create(
                    model="mistralai/Mistral-7B-Instruct-v0.2",
                    messages = [self.system_prompt, user_prompt],
                )

            response = completion.choices[0].message
            content = response.content.strip()

            if need_json_output:
                return extract_json(content)
            else:
                return content
        
        except Exception as e:
            print(e)

class Llama2:
    def __init__(self, hf_token, system_prompt):
        # !pip install sentencepiece==0.1.99
        # !pip install transformers==4.31.0
        # !pip install accelerate==0.21.0
        # !pip install bitsandbytes==0.41.1
        # https://github.com/facebookresearch/llama/blob/main/llama/generation.py#L212
        
        from transformers import LlamaForCausalLM, LlamaTokenizer

        self.system_prompt = system_prompt
        self.tokenizer = LlamaTokenizer.from_pretrained("meta-llama/Llama-2-7b-chat-hf", token=hf_token)
        self.model = LlamaForCausalLM.from_pretrained("meta-llama/Llama-2-7b-chat-hf", load_in_8bit=True, device_map="auto", token=hf_access_token)
        self.generation_kwargs = {
            "max_new_tokens": 512,
            "top_p": 0.9,
            "temperature": 0.6,
            "repetition_penalty": 1.2,
            "do_sample": True,
        }

    def get_response(self, prompt_text, need_json_output=False):
        B_INST, E_INST = "[INST]", "[/INST]"
        B_SYS, E_SYS = "<<SYS>>\n", "\n<</SYS>>\n\n"

        # Special format required by the Llama2 Chat Model where we can use system messages to provide more context about the task
        prompt = f"{B_INST} {B_SYS} {self.system_prompt} {E_SYS} {prompt_text} {E_INST}"

        prompt_ids = tokenizer(prompt, return_tensors="pt")
        prompt_size = prompt_ids['input_ids'].size()[1]

        generate_ids = self.model.generate(prompt_ids.input_ids.to(self.model.device), **self.generation_kwargs)
        generate_ids = generate_ids.squeeze()

        response = tokenizer.decode(generate_ids.squeeze()[prompt_size+1:], skip_special_tokens=True).strip()

        if need_json_output:
                return extract_json(response)
        else:
            return response

        return response

# DO: https://ai.google.dev/tutorials/python_quickstart#use_embeddings
# def compute_embedding(self, chunks):
#     try:
#         embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
#         vector_embedding = FAISS.from_texts( texts = chunks, embedding=embeddings)
#         return vector_embedding
#     except Exception as e:
#         print(e)
#         return None

# Define a function to compute embeddings for the text   
# def compute_embedding(self, text):
#     response = openai.Embed(
#         input=text,
#         model="text-davinci-003-001",
#         max_tokens=50
#     )
#     return response['embedding']

class cv_agents:

    def __init__(self, model="", api_key=""):
        """
        Initialize the AgentManager with necessary configurations and agents.

        Args:
            user_proxy_config (dict): Configuration for the user proxy agent.
            legal_config (dict): Configuration for the legal assistant agent.
        """

        # self.system_message = system_message
        if not model:
            model = config.openai.model
        if not api_key:
            api_key = config.openai.api_key
            
        self.assistant = AssistantAgent(
            name="assistant",
            code_execution_config=False,
            # system_message=self.system_message,
            llm_config={
                "temperature": 0,
                "timeout": 600,
                "cache_seed": None,
                "config_list": [{"model": model, 
                                 "api_key": api_key}]
            },
        )

        def termination_msg(x):
            return isinstance(x, dict) and "TERMINATE" == str(x.get("content", ""))[-9:].upper()

        self.user_proxy = UserProxyAgent(
            name="user_proxy",
            is_termination_msg=termination_msg,
            human_input_mode="NEVER",
            max_consecutive_auto_reply=3
        )

    async def send_message_cvanalyser(self, message: str) -> None:
        try:
            await self.user_proxy.a_initiate_chat(
                recipient=self.assistant,
                clear_history=False,
                silent=True,
                message=message,
                max_turns=10
            )
            response = [messages for agent, messages in self.user_proxy.chat_messages.items()][0][-1]["content"].replace("TERMINATE", "")
            return response
        except Exception as e:
            logger.error(f'Error: {str(e)}')
            return None
        
class agents:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(agents, cls).__new__(cls)
        return cls._instance

    def __init__(self, system_message, model="", api_key=""):
        """
        Initialize the AgentManager with necessary configurations and agents.
        Args:
            user_proxy_config (dict): Configuration for the user proxy agent.
            legal_config (dict): Configuration for the legal assistant agent.
        """
        if not model:
            model = config.openai.model
        if not api_key:
            api_key = config.openai.api_key
                    
        if not hasattr(self, 'system_message'):
            self.system_message = system_message

            self.assistant = AssistantAgent(  
                name="assistant",
                code_execution_config=False,
                system_message=self.system_message,
                llm_config={
                    "temperature": 0,
                    "timeout": 600,
                    "cache_seed": None,
                    "config_list": [{"model": model, 
                                 "api_key": api_key}]
                },
            )

            self.analyser_proxy = UserProxyAgent(
                name="analyser_proxy",
                is_termination_msg=lambda x: isinstance(x, dict) and "TERMINATE" == str(x.get("content", ""))[-9:].upper(),
                human_input_mode="NEVER",
                max_consecutive_auto_reply=3,
            )

            self.interviewer_proxy = UserProxyAgent(
                name="interviewer_proxy",
                is_termination_msg=lambda x: isinstance(x, dict) and "TERMINATE" == str(x.get("content", ""))[-9:].upper(),
                human_input_mode="NEVER",
                max_consecutive_auto_reply=3,
            )

    async def send_message_analyser(self, message: str) -> None:
        try:
            await self.analyser_proxy.a_initiate_chat(
                recipient=self.assistant,
                clear_history=False,
                message=message,
                max_turns=10
            )
            response = [messages for agent, messages in self.analyser_proxy.chat_messages.items()][0][-1]["content"].replace("TERMINATE", "")
            return response
        except Exception as e:
            logger.error(f'Error: {str(e)}')
            raise
        
    async def send_message_interview(self, message: str) -> None:
        try:
            await self.interviewer_proxy.a_initiate_chat(
                recipient=self.assistant,
                clear_history=False,
                message=message,
                max_turns=10
            )
            response = [messages for agent, messages in self.interviewer_proxy.chat_messages.items()][0][-1]["content"].replace("TERMINATE", "")
            return response
        except Exception as e:
            logger.error(f'Error: {str(e)}')
            raise