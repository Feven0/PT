import os, sys
import pandas as pd
import sys
import json
import re
import time
from datetime import datetime
import numpy as np

from openai import OpenAI

from dotenv import load_dotenv
load_dotenv()

from ..modules.pathfig import * 
##
from api import config
import api.utils.s3_utils as s3utils
from api.utils.read_jobs_s3 import ReadJobsS3
from tenx_job_recommender.api.llm.utils.token_counter import count_token
from api.modules.job_preprocessor import JobPreprocessor
from api.modules.trainee_information import TraineeInformation
from api.utils.logger import LLPackerLogger
from api.modules.job_schema import JobSchema, get_weaviate_wrapper


logger = LLPackerLogger(os.path.basename(__file__))


openai_api_key = config.openai.api_key
client = OpenAI(api_key=openai_api_key)
bucket_name='auto-job-recommendation'

def save_objects_into_weaviate(labelled_df):
    # connect to schema
    class_name = 'Job'
    jsc = JobSchema(class_name)
    weaviate = jsc.weaviate
    
    value_to_search = ['good fit', 'not good fit']
    columns_with_value = [col for col in labelled_df.columns if any(val.lower() in labelled_df[col].astype(str).str.lower().tolist() for val in value_to_search)]
    if columns_with_value:
        label = columns_with_value[0]
    else:
        print("No column contains found")
            
    labelled_df = labelled_df.drop(columns=['date.1'])
    labelled_df = labelled_df.dropna(subset=[label])
    labelled_df.rename(columns={label: 'tags'}, inplace=True)
    
    func = lambda x: 'itrain:fit' if x.lower() == 'good fit' else 'itrain:unfit'
    labelled_df['tags'] = labelled_df['tags'].apply(func)
    
    metadata_str = 'label:algorithm:openai-gpt4-turbo-preview, label:date:'
    labelled_df['metadata'] = metadata_str + labelled_df['date']
    for k in ["rubrics", "rationale"]:
        if k in labelled_df.columns:
            labelled_df['metadata'] += labelled_df[k].map(lambda x: str(x))
    
    
    logger.info(f' Inserting Labelled jobs into weaviate. Shape: {labelled_df.shape}')
    saved_obj = weaviate.save_objects(labelled_df, class_name=class_name)
    
    fit_jobs = labelled_df[labelled_df['tags'].astype(str).str.lower() == 'itrain:fit'.lower()]
    logger.good(f'Got {fit_jobs.shape} jobs good fit jobs out of {labelled_df.shape} jobs')
    
    return fit_jobs
    
def save_simulated_cv(cv):
    class_name = 'SimulatedCV'
    jsc = JobSchema(class_name)
    weaviate = jsc.weaviate
    
    # _, schema = jsc.check_schema_exists(class_name)
    obj = weaviate.save_objects(cv, class_name='SimulatedCV')
    
    return True 

    
    

def extract_json_from_llm_response(response, dataframe=True):

        if isinstance(response, dict):
            text = response['output']        
        elif isinstance(response, str):
            text = response
        else:
            logger.info("extract_json_from_llm_response", "response is not a string or a dictionary")
            return {}

        try:
            if '```json' in text:                
                out = text.split('```json')[1].split('```')[0].replace('\n','')
            elif '```' in text:
                out = text.split('```')[1].split('```')[0].replace('\n','')
            else:
                out = text

            classifications = json.loads(out)
            df = pd.DataFrame(classifications)            
        
            return df
        except Exception as e:
            print(e)
            logger.error("extract_json_from_llm_response",
                            exception=e,
                            message="Error while extracting json from response"
                         )
            raise
        
def llm_request(prompt,messages):        
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            response_format={ "type": "json_object" },
            messages=[messages,
                      prompt]
        )
        
        res = response.choices[0].message.content
        finish_reason = response.choices[0].finish_reason
        
        if finish_reason == "completed":
            return res
        else:
            logger.warn("finish_reason is not completed. Parsing response ...")
            res = res + '}'
            
        return res
