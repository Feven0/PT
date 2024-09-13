import re
from datetime import datetime, timedelta
import copy
import json

from .pathfig import * 

from api import config
from api.utils.logger import LLPackerLogger
logger = LLPackerLogger(os.path.basename(__file__))
                   

def merge_list_of_dict(old, new, on='name'):
    if not isinstance(old, list) or not isinstance(new, list):
        logger.error("Invalid input for merge! Elements for merge Must be list!")
        return old
    if not old:
        return new
    if not new:
        return old
    if not isinstance(old[0], dict) or not isinstance(new[0], dict):
        # merging list of non-dict elements
        return list(set(old + new))
    else:
        # merging list of dict elements
        pass
    
    oldnames = [o[on] for o in old]
    
    output = copy.deepcopy(old)
    for n in new:
        # if n is already in old, skip
        if n in old:
            continue
        
        # merge new with old        
        newname = n[on]
        if newname not in oldnames:
                # if n is not in old, add
            output.append(n)
        else:
            # if n is in old, but with modified, replace
            output.insert(oldnames.index(newname), n)
                
    return output

def merge_dicts(oldIn, newIn):
    old = copy.deepcopy(oldIn)
    new = copy.deepcopy(newIn) 
    if not isinstance(old, dict) or not isinstance(new, dict):
        logger.error(f"Invalid input for merge_dicts! type(old)={type(old)}, type(new)={type(new)}")
        return old
    
    output = {}
    for k,v in new.items():
        if k in old.keys():
            if isinstance(v, dict):
                output[k] = merge_dicts(old[k], v)
            elif isinstance(v, list):
                output[k] = merge_list_of_dict(old[k], v)                    
            else:
                output[k] = v                
        else:
            output[k] = v
            
    return output
                            
def recursive_merge(oldIn, newIn, 
                    on='name',
                    root_keys=["user_profile", "attributes"]):
    
    old = copy.deepcopy(oldIn)
    new = copy.deepcopy(newIn)
    if not isinstance(old, dict) or not isinstance(new, dict):
        logger.error("Invalid input for recursive merge! Elements for merge Must be dict!")
        return old

    on_key = old.pop(on, "")
                    
    for root_key in root_keys:
        if root_key in old.keys():                    
            old = old[root_key]
            
        if root_key in new.keys():
            new = new[root_key]
        
    user_profile = merge_dicts(old, new)
        
    output = {root_key:user_profile} 

    if on_key:
        output[on] = on_key
    
    return output