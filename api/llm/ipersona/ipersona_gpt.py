import time, asyncio
from openai import OpenAI
import textwrap
from api import config

OPENAI_API_KEY = config.openai.api_key
client = OpenAI(api_key=OPENAI_API_KEY)



def openai_gpt_assistant_with_streaming(msg):
    model = 'gpt-4o-mini'
    temperature=0
    messages = [{'role': 'user', 'content': msg}]

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        stream=True
    )
    for chunk in response:
            chunk_message = chunk.choices[0].delta.content 
            if chunk_message: 
                yield chunk_message
                
def generate_response(messages):
    response_stream = openai_gpt_assistant_with_streaming(messages)
    
    response_text = ""
    for chunk in response_stream:
        chunk_message = chunk.choices[0].delta.content
        if chunk_message is not None:
            response_text += chunk_message
            wrapped_text = textwrap.fill(response_text, width=80)
            yield f"{wrapped_text}\n" 
            

def openai_gpt_assistant_without_streaming(msg):
    model = 'gpt-4o-mini'
    temperature=0
    messages = [{'role': 'user', 'content': msg}]

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature
    )
    
    response_message = response.choices[0].message.content  
    return response_message