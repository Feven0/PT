
import os, sys
import json
import time
from typing import List, Dict


import api.utils.s3_utils as s3utils

#local config
from api import config

from api.utils.logger import LLPackerLogger
logger = LLPackerLogger(__file__)

class fileManager:
    def __init__(self, use_local_storage=False, bucket=None):
        self.use_local_storage = use_local_storage
        if not bucket:
            bucket = config.s3.zlm_bucket
        self.bucket = bucket
        
    def _save_to_file_cache(self, local_file, filename, key=""):                    
        
        file_key = os.path.basename(filename)
        if key:
            file_key = os.path.join(key, file_key)
                    
        if self.bucket:
            try:
                s3utils.upload_file_to_s3(local_file, file_key, self.bucket, isfile=True) 
            except Exception as e:
                logger.error(f"Error saving to S3: {os.path.basename(filename)}")
                print(e)
                    
        return file_key
          
    def _read_from_file_cache(self, filename, key=""):
        # get filename                   
        file_key = os.path.basename(filename)
        if key:
            file_key = os.path.join(key, file_key)
        
        try:        
            listobj = s3utils.read_text_file_from_s3(self.bucket, file_key)
        except Exception as e:
            logger.error(f"Error reading from S3: {os.path.basename(filename)}")
            print(e)
            listobj = ""
            
        return listobj
              