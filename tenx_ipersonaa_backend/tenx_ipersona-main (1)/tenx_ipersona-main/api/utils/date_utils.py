import re
from datetime import datetime, timedelta
import copy
import json

from .pathfig import * 

from api import config
from api.utils.logger import LLPackerLogger
logger = LLPackerLogger(os.path.basename(__file__))

def date_string_to_datetime(date_string):
    return date_string.strftime("%Y-%m-%dT%H:%M:%S+00:00")


def parse_date_posted(d):
    if not d:
        return datetime.now()
    else:
        since = re.findall(r'\d+',d)
        if not since:
            since = [0]

        #
        kw = {}
        for k, v in {'day':'days', 'hour':'hours', 
                     'minute':'minutes', 'second':'seconds'}.items():
            
            if k in d:
                kw = {v: int(since[0])}
                break

        if not kw:
            kw = {'hours': int(since[0])}

        # 
        print(kw)
        odate = datetime.now() - timedelta(**kw)
        return odate
    
def get_date_and_days_from_now(d):
    now = datetime.now()

    if not d:
        d = now
        
    if isinstance(d, str):
        if d.strip():            
            if d.endswith('Z'):            
                d = d[:-1]
                    
            try:            
                d = datetime.fromisoformat(d)
            except Exception as e:
                print(e)
                print("Error parsing date: ", d)
                d = datetime.strptime(d.split('T')[0], '%Y-%m-%d') #+ now.utcoffset()
        else:
            d = now
                
    elif isinstance(d, datetime):
        pass        
    else:
        d = now
       
    try: 
        delta = now - d
    except Exception as e:
        print(e)
        print(f"Error computing delta: now={now} minus date={d}")
        delta = now.replace(tzinfo=None) - d.replace(tzinfo=None)
        print(f"delta={delta}")    
        
    days_from_now = delta.days
    
    d = d.isoformat()
    d = str(d)
    if not d.endswith('Z'):            
        d = d + 'Z'
        
    return d, days_from_now

def weaviate_date(date=None, now=True, **kwargs):
    
    format = kwargs.get("format", "%Y-%m-%d")
    
    if date is None:
        date = datetime.now()

    if isinstance(date, str):
        
        date = datetime.strptime(date, format)
        output = date_string_to_datetime(date)
        
    elif isinstance(date, datetime):
        date = date
        output = date_string_to_datetime(date)
        
    elif isinstance(date, list):
        if all(isinstance(d, str) for d in date):
            output = [date_string_to_datetime(datetime.strptime(d, format)) for d in date]
        elif all(isinstance(d, datetime) for d in date):
            output = [date_string_to_datetime(d) for d in date]
    else:   
        logger.info("Date is not a string or datetime object")
        return date
    
    return output
        
        