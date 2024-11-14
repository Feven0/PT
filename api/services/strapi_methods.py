
from numpy import int64
import pandas as pd
import requests
import json
import os,sys
import numpy as np


from api import config
from api.services.secret import get_auth, lambda_friendly_path
from api.utils.logger import LLPackerLogger

logger = LLPackerLogger(os.path.basename(__file__))

class StrapiMethods:
    def __init__(self, **kwargs):
        
        # define run environment
        if config.strapi.stage=='dev':
            run_stage =  kwargs.get('run_stage',config.strapi.stage)
        else:
            run_stage = config.strapi.stage
        
        logger.info('StrapiMethods run_stage:', run_stage, level=11)
        root, ssmkey = config.get_strapi_params(run_stage)

        self.api_url = f"https://{root}.10academy.org/graphql" 
        self.ssmkey = ssmkey
        
        self.token = get_auth(ssmkey,
                             envvar='STRAPI_TOKEN',
                             fconfig=lambda_friendly_path(f'.env/{root}.json'))       
        

    def fetch_data(self, table, token=None):
        # Construct the full URL using self.api_url
        url = f"{self.api_url.replace('graphql', 'api')}/{table}"
       
        try:
            # Make the request with the correct headers
            r = requests.get(url, headers={
                "Authorization": f"Bearer {self.token}", 
                "Content-Type": "application/json"
            })
            
            # Return the response as JSON
            return r.json()
        
        except Exception as e:
            print(f"Error fetching data: {e}")
            raise
    
                
    def update(self,table, id, params, token=None):
        
        r = requests.put(table+ str(id),
        data=json.dumps({
           "data":params
        }),
        headers={
            "Authorization": f"Bearer {self.token}", 
            'Content-Type': 'application/json'
        })
        
        
    def insert_data (self,data,table, token=None):
      
        try:
            r = requests.post(

                f"{self.api_url.replace('graphql','api')}/{table}", 

                data = json.dumps({"data":data}),
                # self.token['token']
                headers = {

                "Authorization": f"Bearer {self.token}", 

                "Content-Type": "application/json"}

            ).json()
        except Exception as e:
            print(e)
            raise
            
        return r
    
    def update_data (self, id, data, table, token=None):
      
        try:
            r = requests.put(

                f"{self.api_url.replace('graphql','api')}/{table}/{id}", 

                data = json.dumps({"data":data}),
                # self.token['token']
                headers = {

                "Authorization": f"Bearer {self.token}", 

                "Content-Type": "application/json"}

            ).json()
        except Exception as e:
            print(e)
            raise
            
        return r
    

   
        
    
        

 

if __name__ == "__main__":
    obj = StrapiMethods()
    # table= "/api/title-trainees"
    
    table= "https://dev-cms.10academy.org/api/applicant-informations"
  