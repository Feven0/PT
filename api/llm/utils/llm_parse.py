import os, sys
import json
import json_repair
from datetime import datetime, timedelta
from api.utils.logger import LLPackerLogger

logger = LLPackerLogger(os.path.basename(__file__))

def extract_json(response, quite=False):
    
    if isinstance(response, (dict, list)):
        # return as it is 
        if not quite: logger.info("extract_json", "response is already in json format")
        return response       
    elif isinstance(response, str):
        # Method 1
        try:
            # try simple to load it as json
            res = json.loads(response)
            if not quite: logger.info("extract_json", "response is already in jsons format")
            return res
        except:
            if not quite: logger.warn("extract_json: simple json load failed. Trying to fix json string ...")
           
        # Method 2 
        try:
            if not quite: logger.info("extract_json", "response is not in json format. Trying to extract json from response")
            if '```json' in text:                
                out = text.split('```json')[1].split('```')[0].replace('\n','')
            elif '```' in text:
                out = text.split('```')[1].split('```')[0].replace('\n','')
            else:
                out = text

            res = json.loads(out)
            return res        
        except Exception as e:
            if not quite: logger.warn(f"extract_json: unable to fix json string. Trying with json_repair ...")
                        
            # it is not in json string format
            
            # Method 3
            text = response
            try:                
                res = json_repair.loads(text)
                if isinstance(res, (dict, list)):
                    if not quite: logger.info("extract_json: result obtained using repair json")
                    return res
            except:
                if not quite: logger.error("extract_json: unable to repair json string using json_repair. Raise exception")
                raise
    else:
        if not quite: logger.info("extract_json", "response is not a string or a dictionary")
        return {}

