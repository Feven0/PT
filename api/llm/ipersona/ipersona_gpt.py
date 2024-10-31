import time, asyncio
from openai import OpenAI
import textwrap
from IPython.display import display, clear_output, HTML

OPENAI_API_KEY = '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'

client = OpenAI(api_key=OPENAI_API_KEY)


from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import textwrap

app = FastAPI()

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
            

# @app.post("/api/stream")
async def stream_endpoint():
    model = 'gpt-4o-mini'
    messages = [{'role': 'user', 'content': "Tell me about Ethiopia in 100 words?"}]
    
    return StreamingResponse(generate_response(client, model, messages), media_type='text/plain')


async def openai_gpt_assistant_without_streaming(msg):
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