import os, sys
#
import warnings
warnings.filterwarnings("ignore")
#
import instructor
from litellm import completion
import openai
from pydantic import BaseModel

#
from .pathfig import *
from api import config
from api.utils.logger import LLPackerLogger

logger = LLPackerLogger(os.path.basename(__file__))

openai_api_key = config.openai.api_key
client = openai.OpenAI(api_key=openai_api_key)

## set ENV variables
os.environ["OPENAI_API_KEY"] = openai_api_key
#os.environ["COHERE_API_KEY"] = "cohere key"




# Define your desired output structure
class UserInfo(BaseModel):
    name: str
    age: int


def extract_user_info(message: str) -> UserInfo:
    # Patch the OpenAI client
    #client = instructor.from_openai(openai.OpenAI(api_key=openai_api_key))   
    client = instructor.from_litellm(completion) #litellm infers the client from the model and inits from env api key
     
    # Extract structured data from natural language
    user_info = client.chat.completions.create(
        model="gpt-3.5-turbo",
        response_model=UserInfo,
        messages=[{"role": "user", "content": message}],
    )
    return user_info.choices[0].message

async def extract():
    client = instructor.from_openai(openai.AsyncOpenAI(api_key=openai_api_key))
    return await client.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=[
            {"role": "user", "content": "Create a user"},
        ],
        response_model=UserInfo,
    )
    
