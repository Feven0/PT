'''
-----------------------------------------------------------------------
Author: Yabebal Fantaye
Mdoified Date: 2021-07-01
-----------------------------------------------------------------------
'''
import os, sys
import json
import functools
import asyncio
import random
import re
import redis as sredis
import redis.asyncio as aredis
#import httpx
#
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, List, Iterable, Union, Tuple, Any



from api import config
from api.utils.async_utils import force_async, force_sync, run_async
from api.utils.logger import LLPackerLogger
logger = LLPackerLogger(__file__)

ONE_DAY = 24*60*60
ONE_WEEK = 7*ONE_DAY
redis_url = f"{config.cache.REDIS_URL}?decode_responses=True&protocol=3"

def get_redis_pool():    
    
    pool = aredis.ConnectionPool.from_url(redis_url)
    try:
        pool = aredis.Redis(connection_pool=pool, max_connections=4)
    except Exception as e:
        print(e)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        pool = aredis.Redis(connection_pool=pool, max_connections=4)
    #pool = aredis.Redis.from_pool(pool)        
    #pool = aredis.from_url(url)
    
    return pool

def seconds_until_midnight(dt: datetime=datetime.now()) -> int:
    # Calculate the next midnight
    midnight = (dt + timedelta(days=1)).replace(hour=0, 
                                                minute=0, 
                                                second=0, 
                                                microsecond=0)
    
    # Calculate the difference between the given datetime and the next midnight
    time_difference = midnight - dt
    
    # Return the total number of seconds remaining until midnight
    return int(time_difference.total_seconds())



async def get_key(key: str) -> Any:
    redis = get_redis_pool()
    res = await redis.get(key)
    redis.aclose()
    return res


async def set_key(key: str, value: Any, expire_seconds: Optional[int] = None) -> bool:
    redis = get_redis_pool()
    if expire_seconds is not None:
        exp = timedelta(seconds=expire_seconds)
        await redis.set(key, value, ex=exp)
    else:
        await redis.set(key, value)
        
    redis.aclose()
    
    return True

def async_client_wrapper(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs): 
           
        if args[0]._client is not None:
            await args[0]._client.aclose()
            args[0]._client = None
                     
        try:
            res = await func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in Redis async client wrapper: {e}")
            res = None
            
        # always close the pool        
        if args[0]._client is not None:
            await args[0]._client.aclose()
            args[0]._client = None
            
        return res
            
    return wrapper

def client_wrapper(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):        
        if args[0].client is None:            
            args[0].client = args[0].connect()
            
        try:
            res = func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in Redis client wrapper: {e}")            
        
        # always close the client
        if args[0].client is not None:
            args[0].client.close()
            args[0].client = None
                    
        return res
            
    return wrapper

def dict_or_list_of_dict(obj: Any) -> Any:
    if not isinstance(obj, list):
        not_list = True
        res_list = [obj]
    else:
        not_list = False
        res_list = obj
        
    output = []
    for item in res_list:
        if not isinstance(item, dict):
            try:
                res = json.loads(item)
                output.append(res)
            except Exception as e:
                print('item:',item)
                logger.error(f"Unable to convert item to dict: {e}")
        else:
            output.append(item)
    
    if not_list:
        if len(output)>0:
            output = output[0]
        else:
            output = {}
    else:
        output = output
        
    return output
        
def get_id_start(id_start: str, ndays: int, name: str=""):
    week = datetime.now() - timedelta(days=ndays)
    weekmsec = int(datetime.timestamp(week)*1000)        
    
    try:        
        id_start_msec = int(id_start.split('-')[0])
        m1 = f"requested id_start={id_start} timestamp"
        m2 = f"than {ndays} days ago!"
        if id_start_msec >= weekmsec:
            logger.good(f'{name} - Using the {m1} as it is newer {m2}')
        else:
            logger.warn(f'{name} - Using a timestamp from {ndays} days ago as {m1} is older {m2}')
            id_start_msec = weekmsec
            
        id_start = f"{id_start_msec}-0"                                        
    except Exception as e:
        logger.error(f"{name} - Unable to estimate last id timestamp from id_start={id_start}. {e}")
        logger.warn(f'{name} - Setting id_start with timestamp from ndays={ndays} ago')
        id_start = f"{weekmsec}-0"      
        
    return id_start 

class idash_names:
    job_card = "job_profile_id:job_card_stream_id::user_profile_id"
    job_profile = "job_profile_id:job_profile_stream_id"

class BaseRedisClient:
    def __init__(self, run_stage="", max_stream_size=100000):
        
        if not run_stage:
            self.run_stage = config.strapi_stage
        else:
            self.run_stage = run_stage
            
        self.MAX_STREAM_SIZE = max_stream_size

        self.idash = idash_names()
        
    #-------streams------
    def _job_profile_stream_key(self):        
        #return f"{self.run_stage}:job_profile:stream" 
        return self._job_profile_stream_key_stage()  #f"job_profile:stream" 
    
    def _job_profile_stream_key_stage(self):        
        return f"{self.run_stage}:job_profile:stream"     
    
    def _user_job_card_stream_key(self, user_profile_id: Union[str, int]):
        return f"{self.run_stage}:job_card:stream:user_profile_id:{user_profile_id}"
        
    def _user_reaction_stream_key(self, user_profile_id: Union[str, int]):
        return f"{self.run_stage}:reaction:stream:user_profile_id:{user_profile_id}"
         
    def _user_leap_stream_key(self, user_profile_id: Union[str, int]):
        return f"{self.run_stage}:leap:stream:user_profile_id:{user_profile_id}"
                
    #-------key hashes & maps------
    def _generic_idmap_key(self, id_key: Union[str, int]="", id_var: Union[str, int]=""):
        s =  f'{self.run_stage}:idhash'
        if id_key:
            s = f'{s}:{id_key}'
            if id_var:
                s = f'{s}:{id_var}'
        
        return s
    
    def _job_is_invalid_idmap_key(self):
        return f'{self.run_stage}:idhash:jobNOTvalid'
    
    def _preference_filter_event_idmap_key(self, user_profile_id):
        return f'{self.run_stage}:idhash:preference_filter:user_profile_id:{user_profile_id}'
            
    def _user_reaction_idmap_key(self, user_profile_id):
        return f'{self.run_stage}:idhash:reaction:user_profile_id:{user_profile_id}'
    
    def _user_jcard2jstream_idmap_key(self, user_profile_id):
        return f'{self.run_stage}:idhash:jcard2jstream:user_profile_id:{user_profile_id}'
    
    def _user_job2redis_idmap_key(self, user_profile_id: Union[str, int]):
        return f'{self.run_stage}:idhash:job2redis:user_profile_id:{user_profile_id}'
        
    def _all_user_profile_id_key(self, all_user_id: Union[str, int]):
        return f'{self.run_stage}:idmap:user_profile_id:all_user_id:{all_user_id}'
        
    def _all_user_preference_id_key(self, all_user_id: Union[str, int]):
        return f'{self.run_stage}:idmap:user_preference_id:all_user_id:{all_user_id}'        

    #-------index keys------            
    def _user_job_profile_latest_id_key(self, user_profile_id: Union[str, int]):
        return f'{self.run_stage}:job_profile_stream:user_profile_id:{user_profile_id}'
    
    def _user_job_card_latest_id_key(self, user_profile_id: Union[str, int]):
        return f'{self.run_stage}:job_card_stream:user_profile_id:{user_profile_id}' 
           
    def _admin_user_reaction_latest_id_key(self, admin_all_user_id: Union[str, int], 
                                           user_profile_id: Union[str, int]):
        s = f"{self.run_stage}:admin_reaction_stream:all_user_id:{admin_all_user_id}"
        return f'{s}:user_profile_id:{user_profile_id}' 
                   
    def _admin_user_leap_latest_id_key(self, admin_all_user_id: Union[str, int], 
                                       user_profile_id: Union[str, int]):
        s = f"{self.run_stage}:admin_leap_stream:all_user_id:{admin_all_user_id}"
        return f'{s}:user_profile_id:{user_profile_id}' 
                       
    #-------json stores------
    def _user_profile_key(self, user_profile_id: Union[str, int]):
        return f'{self.run_stage}:user_profile:user_profile_id:{user_profile_id}'
        
    def _user_stat_key(self, user_profile_id: Union[str, int]):
        return f'{self.run_stage}:user_stat:all_user_id:{user_profile_id}'

    def _user_preference_key(self, user_profile_id: Union[str, int]):
        return f'{self.run_stage}:user_preference:user_profile_id:{user_profile_id}'
    
    #-------pre and post processing funcs------
    def _xdata_prep(self, data: dict, 
               save_json: bool=False, 
               isxread: bool=False) -> dict:
        
        output = {}
        if isxread:
            # TODO: change item to json_string
            item_value = data.get('item', '')
            if isinstance(item_value, str) and item_value:
                cond = item_value.startswith('{') and item_value.endswith('}')           
                if cond:
                    output = json.loads(data['item'])
                else:
                    output = data
            else:
                output = data
        else:
            if save_json:
                output = data
            else:            
                output = {"item": json.dumps(data)}
                
        return output

class RedisClient(BaseRedisClient):
    def __init__(self, run_stage="", max_stream_size=100000):
        super().__init__(run_stage=run_stage, max_stream_size=max_stream_size)
        self._client = None
        
    @property
    def client(self):
        # get always returns a connection
        if self._client is None:
            self.client = get_redis_pool()
                                
        return self._client
    
    @client.setter
    def client(self, value):
        
        if value is None:
            # setting to none will close the connection if it exists
            if self._client is not None:                
                try:
                    asyncio.run(self._client.aclose())            
                except Exception as e:
                    logger.warn(f"Close connection before you set it to None: {e}")
                self._client = None
        else:
            # setting to a value will set a new connection or use existing connection
            if self._client is None:                
                self._client = value
   
    @async_client_wrapper
    async def _stream_xadd(self, key: str, data: List[Dict], save_json: bool=False):
        '''
        We are using Redis STREAM to add job profiles as time ordered set
        XADD adds a new entry to a stream.
        XACK
        XDEL 
        XREAD reads one or more entries, starting at a given position and moving forward in time.
        XRANGE returns a range of entries between two supplied entry IDs.
        XREVRANGE reverse of XRANGE 
        XLEN returns the length of a stream.
        XTRIM
        XINFO
        XACK command removes one or multiple messages from the Pending Entries List (PEL) of a stream consumer group.
        REF: 
            All stream commands: https://redis.io/docs/latest/commands/?group=stream
            Article: https://redis.io/docs/latest/develop/data-types/streams/
        '''        
        if len(data)==0:
            logger.error("Passed empty data to add to stream with key={key}")
            return 
        
        tasks = []
        try:
            # create all tasks            
            for item in data:
                if not item:
                    logger.warn(f"Empty item passed to add to stream with key={key}")
                    continue
                #print('XADD adding item.keys():',item.keys())
                fmt_item = self._xdata_prep(item, save_json=save_json)                
                coro = self.client.xadd(key, fmt_item,
                                       maxlen=self.MAX_STREAM_SIZE, 
                                       approximate=True)
                #task = asyncio.create_task(coro)  
                tasks.append(coro)  
                
            #await asyncio.wait_for(coro_single, timeout=5)
            #await asyncio.wait(coro_list, *, timeout=None, return_when=ALL_COMPLETED)
            results = await asyncio.gather(*tasks)                                                              
        except Exception as e:
            logger.error(f"Error setting items in Redis Stream key={key}: {e}")
            raise
        
        return results

    @async_client_wrapper
    async def _stream_xread(self, 
                            key: str, 
                            id_start: Union[str, int], 
                            count: int=1, 
                            cmust: list = []) -> Tuple[List[str],List[Dict]]:
        try:
            ncards = count
            id_list = []
            output = []
            skipped = 0            
            while True:
                #logger.info(f'Starting xread loop: id_start={id_start}, count={count} ...')
                
                coro = self.client.xread(count=ncards, streams={key: id_start})
                #task = asyncio.create_task(coro)
                result = await coro   
                                
                if not result:
                    logger.warn(f"{result} returned from stream content with key={key} & id={id_start}. Breaking..")
                    break
                else:    
                    try:
                        if isinstance(result, dict):
                            result = result[key][0]
                        else:
                            pass
                    except Exception as e: 
                        print('result:',result)                                                
                        logger.warn(f"Invalid xread output. Dict with key={key} and list value is expected. Breaking")
                        print(e)
                        break    
                       
                      
                print(f'Got n={len(result)} items from stream content with key={key} & id={id_start}')                                         
                
                if len(result)>0:                    
                    for item in result:   
                        if isinstance(item[0], (list, tuple)):
                            id_start = item[0][0]
                            item_value = item[0][1]                            
                        else:
                            id_start = item[0]                                    
                            item_value = item[1]  
                                                                           
                        content = self._xdata_prep(item_value, isxread=True)
                        if not content: 
                            print('Item extracted:', item) 
                            logger.warn(f"Stream content with key={key} & id={id_start} is empty! Delete + Skip ...")
                            #                          
                            rxdel = await self.client.xdel(key, id_start)
                            logger.good(f"Deleted={rxdel} for item is empty: id={id_start} stream_key={key}")                            
                             
                            skipped += 1                           
                            continue
                        
                        for c in cmust:
                            if not content.get(c, ""):
                                rxdel = await self.client.xdel(key, id_start)
                                logger.good(f"Deleted={rxdel} item for col={c} is empty: id={id_start} stream_key={key}")
                                skipped += 1
                                break
                                            
                        id_list.append(id_start)
                        output.append(content)
                else:
                    print('result',result)
                    logger.warn(f"Empty result returned from stream content with key={key} & id={id_start}. Breaking..")
                    break
                    
                if len(output)==count:
                    logger.info(f"Got {len(output)} of requested={count} items from Redis Stream {key}. Breaking")
                    break   
                else:
                    ncards = count-len(output)
                    logger.info(f"Got {len(output)} of requested={count} items from Redis Stream {key} .. continuing")
                    logger.info(f'Setting ncards={ncards}, id_start={id_start}')
                    continue
                
                    
                
            return output, id_list
        
        except Exception as e:
            print(e)
            var = f"key={key}, id_start={id_start}, count={count}"
            logger.error(f"Error getting items from Redis Stream {var}")
            raise
        
    @async_client_wrapper
    async def _stream_xlen(self, key: str, id_start: str=""):
        if not id_start:
            val = await self.client.xlen(key)        
        else:
            arr = await self.client.xrange(key, id_start, "+")
            val = len(arr)
                    
        return val           
            
    @async_client_wrapper
    async def _set_set(self, *args, **kwargs):        
        coro = self.client.set(*args, **kwargs)
        return await coro     
    
    @async_client_wrapper
    async def _set_get(self, *args, **kwargs):
        coro = self.client.get(*args, **kwargs)
        return await coro 
    
    @async_client_wrapper
    async def _json_set(self, *args, **kwargs):
        coro = self.client.json().set(*args, **kwargs)        
        return await coro #coro #asyncio.wait_for(coro, timeout=5)
    
    @async_client_wrapper
    async def _json_get(self, *args, **kwargs):
        coro = self.client.json().get(*args, **kwargs)
        return await coro #asyncio.create_task(coro)

    @async_client_wrapper
    async def _hash_set(self, *args, **kwargs):
        coro = self.client.hset(*args, **kwargs)
        return await coro #coro #asyncio.wait_for(coro, timeout=5)
    
    @async_client_wrapper
    async def _hash_setxn(self, *args, **kwargs):
        coro = self.client.hsetnx(*args, **kwargs)
        return await coro #coro #asyncio.wait_for(coro, timeout=5)    
    
    @async_client_wrapper
    async def _hash_get(self, *args, **kwargs):
        coro = self.client.hget(*args, **kwargs)
        return await coro #asyncio.create_task(coro)
                    
    @async_client_wrapper
    async def _exists(self, *args, **kwargs):
        coro = self.client.exists(*args, **kwargs)
        return await coro 


    #--------------------Generic Hash map--------------------------
    @async_client_wrapper
    async def add_to_idmap(self, 
                           key_name: str,
                           key_var: Union[str, int], 
                           map_dict: dict,
                           isfullkey=False) -> List[Union[int, str]]:
        
        #pipeline = self.client.pipeline()
        if isfullkey:
            key = key_name
        else:
            key = self._generic_idmap_key(key_name, key_var)
            
        #
        val_exist = await self._exists(key)
        
        if not val_exist:
            # add items with new key
            all_res = await self.client.hset(key, mapping=map_dict)
        else:
            # add items with existing key
            all_res = []
            for k, v in map_dict.items():
                res = await self.client.hsetnx(key, k, v)  
                all_res.append(res)

        return all_res
    
    @async_client_wrapper
    async def get_from_idmap(self, 
                             key_name: str, 
                             key_var: Union[str, int], 
                             map_key: Union[str, int]="",
                             isfullkey=False) -> Any:
        
        if isfullkey:
            key = key_name
        else:
            key = self._generic_idmap_key(key_name, key_var)
            
        if map_key:
            res = await self.client.hget(key, str(map_key))
        else:
            res = await self.client.hgetall(key)
            
        return res 
    
    @async_client_wrapper
    async def in_idmap(self, 
                       key_name: str, 
                       key_var: Union[str, int], 
                       map_key: Union[str, int],
                       isfullkey=False) -> Any:
        
        if isfullkey:
            key = key_name
        else:
            key = self._generic_idmap_key(key_name, key_var)
        
        res = await self.client.hget(key, str(map_key))
                        
        if res:
            output = True
        else:
            output = False    
        
        return output

    #----------------Job Is Invalid Report Hash: --------------------
    #        job_profile_id:{user_profile_id:"","messag":}
    #----------------------------------------------------------------
    async def report_invalid_job(self,                                  
                                 user_profile_id: Union[str, int], 
                                 job_profile_id: Union[str, int], 
                                 reason: str):
        
        key = self._job_is_invalid_idmap_key()
        res = await self.in_idmap(key, "", job_profile_id, isfullkey=True)
        if not res:
            value = json.dumps({user_profile_id: reason})
            map_dict = {job_profile_id: value}
            res = await self.add_to_idmap(key, "", map_dict, isfullkey=True)
        else:
            res = ""
            
        return res
    
    async def is_invalid_job(self, job_profile_id: Union[str, int]) -> bool:
        key = self._job_is_invalid_idmap_key()
        res = await self.in_idmap(key, "", job_profile_id, isfullkey=True)
        if res:
            output = True
        else:
            output = False
            
        return output
    
   #----------------Job Is Invalid Report Hash: --------------------
    #        job_profile_id:{user_profile_id:"","messag":}
    #----------------------------------------------------------------
    async def set_preference_filter_event(self,                                  
                                 user_profile_id: Union[str, int], 
                                 job_profile_id: Union[str, int], 
                                 event: dict):
        
        key = self._preference_filter_event_idmap_key(user_profile_id)        
        value = json.dumps(event)
        map_dict = {job_profile_id: value}
        res = await self.add_to_idmap(key, "", map_dict, isfullkey=True)
        
            
        return res
    

        
    async def get_preference_filter_event(self, 
                                          user_profile_id: Union[str, int],
                                          job_profile_id: Union[str, int]=""
                                          ) -> Dict:
        
            key = self._preference_filter_event_idmap_key(user_profile_id)
            
            res = await self.get_from_idmap(key, "", job_profile_id, isfullkey=True)  
            if not job_profile_id:
                res = {k:json.loads(v) for k, v in res.items() if k and v}
            else:
                res = json.loads(res)
            
            return res
        
    async def isin_preference_filter_event(self, 
                                           job_profile_id: Union[str, int]) -> bool:
        key = self._job_is_invalid_idmap_key()
        res = await self.in_idmap(key, "", job_profile_id, isfullkey=True)
        if res:
            output = True
        else:
            output = False
            
        return output    

    #----------------------------------------------------------------
    #------------Reaction Hash: job_profile_id:reaction idmap------
    #----------------------------------------------------------------
    async def set_user_reaction_idmap(self, 
                                      user_profile_id: Union[str, int], 
                                      reaction_idmap: dict):
        '''
        reaction_idmap: {redis_profile_id: user_reaction_type}
        '''
        #pipeline = self.client.pipeline()
        key = self._user_reaction_idmap_key(user_profile_id)
        res = await self.add_to_idmap(key, "", reaction_idmap, isfullkey=True)
        
            
        return res        
        
    async def get_user_reaction_idmap(self, 
                                      user_profile_id: Union[str, int], 
                                      job_profile_id: str="") -> Any:
        key = self._user_reaction_idmap_key(user_profile_id)
        res = await self.get_from_idmap(key, "", job_profile_id, isfullkey=True)
            
        return res    
    
    async def in_reaction_idmap(self,
                                user_profile_id: Union[str, int],  
                                job_profile_id: Union[str, int]
                                ) -> bool:
        key = self._user_reaction_idmap_key(user_profile_id)
        res = await self.in_idmap(key, "", job_profile_id, isfullkey=True)
        if res:
            output = True
        else:
            output = False
            
        return output  
    
    #----------------------------------------------------------------
    #------Job Card-Stream Hash: job_card_redis_id:job_stream_redis_id idmap------
    #----------------------------------------------------------------
    @async_client_wrapper
    async def set_user_jcard2jstream_idmap(self, 
                                      user_profile_id: Union[str, int], 
                                      idmap: dict):
        '''
        idmap: {ob_card_redis_id:job_stream_redis_id}
        '''
        #pipeline = self.client.pipeline()
        key = self._user_jcard2jstream_idmap_key(user_profile_id)
        val_exist = await self._exists(key)
        if not val_exist:
            all_res = await self.client.hset(key, mapping=idmap)
        else:
            all_res = []
            for redis_jcard_id, redis_jstream_id in idmap.items():
                res = await self.client.hsetnx(key, redis_jcard_id, redis_jstream_id)  
                all_res.append(res)

        return all_res
    
    @async_client_wrapper
    async def get_user_jcard2jstream_idmap(self, 
                                      user_profile_id: Union[str, int], 
                                      redis_jcard_id: str="") -> Any:
        key = self._user_jcard2jstream_idmap_key(user_profile_id)
        if redis_jcard_id:
            res = await self.client.hget(key, redis_jcard_id)
        else:
            res = await self.client.hgetall(key)
            
        return res        

    #----------------------------------------------------------------
    #-----------Job Card Hash: job_profile_id:redis_job_card_id idmap-------
    #----------------------------------------------------------------
    @async_client_wrapper
    async def set_user_job2redis_idmap(self, user_profile_id: Union[str, int], 
                                       job2redis_idmap: dict):
        #pipeline = self.client.pipeline()
        key = self._user_job2redis_idmap_key(user_profile_id)
        val_exist = await self._exists(key)
        if not val_exist:
            all_res = await self.client.hset(key, mapping=job2redis_idmap)
        else:
            all_res = []
            for job_id, redis_id in job2redis_idmap.items():
                res = await self.client.hsetnx(key, job_id, redis_id)  
                all_res.append(res)

        return all_res
    
    @async_client_wrapper
    async def get_user_job2redis_idmap(self, user_profile_id: Union[str, int], 
                                       job_profile_id: Union[str, int]="") -> Any:
        key = self._user_job2redis_idmap_key(user_profile_id)
        if job_profile_id:
            res = await self.client.hget(key, str(job_profile_id))
        else:
            res = await self.client.hgetall(key)
            
        return res    
    
    #----------------------------------------------------------------
    #-----------User support accessing idmap with key or value -------
    #----------------------------------------------------------------
    async def get_redis_card_ids_from_job_profile_ids(self, user_profile_id: Union[str, int],
                                                      job_profile_ids: List[Union[str, int]]
                                                      ) -> List[Union[str, int]]:
        idmap_dict = await self.get_user_job2redis_idmap(user_profile_id) 
        output =  [v for k, v in idmap_dict.items() if k in job_profile_ids]  
        
        return output
    
    async def get_job_profile_ids_from_redis_card_ids(self, user_profile_id: Union[str, int],
                                                      redis_card_ids: List[Union[str, int]]
                                                      ) -> List[Union[str, int]]:
        idmap_dict = await self.get_user_job2redis_idmap(user_profile_id) 
        output =  [k for k, v in idmap_dict.items() if v in redis_card_ids]  
        
        return output    
                      
    #----------------------------------------------------------------
    #--------------------Job Profile Stream--------------------------
    #----------------------------------------------------------------
    async def job_profile_stream_xlen(self, id_start: str=""):
        key = self._job_profile_stream_key()                
        return await self._stream_xlen(key, id_start=id_start)
        
    async def set_user_job_profile_stream_latest_id(self, user_profile_id: Union[str, int], 
                                                    latest_job_profile_id: str):
        key = self._user_job_profile_latest_id_key(user_profile_id)
        res = await self._set_set(key, latest_job_profile_id)
        return res
           
    async def get_user_job_profile_stream_latest_id(self, user_profile_id: Union[str, int]):
        key = self._user_job_profile_latest_id_key(user_profile_id)
        res = await self._set_get(key)
        if not res:
            res = "0-0"
        return res
                
    async def add_to_job_profile_stream(self, data: List[Dict], stage: bool=True):
        if stage:
            key = self._job_profile_stream_key_stage()
        else:
            key = self._job_profile_stream_key()
        
        # add job profiles to the stream
        res = await self._stream_xadd(key, data)
        
        #
        if res:
            # set the job_profile_id to job_profile_stream_id map
            for item, redis_id in zip(data, res):
                job_profile_id = item.get('job_profile_id', "")
                if not job_profile_id or not redis_id:
                    logger.warn(f"Empty job_profile_id in {item} or redis_id={redis_id}. Skipping ...")
                    continue
                else:
                    res2 = await self.set_jid2jpstream_idmap(job_profile_id, redis_id)
                    if not res2:
                        logger.warn(f"Failed to set jid2jpstream_idmap for {job_profile_id}={redis_id}")
                    else:
                        logger.good(f"Successfully set jid2jpstream_idmap for {job_profile_id}={redis_id}")
                    
        return res
        
    async def get_from_job_profile_stream(self, id_start: Union[str, int]=0, 
                                          count: int=1,
                                          ndays: int=3, 
                                          stage: bool=True):
        if stage:
            key = self._job_profile_stream_key_stage()
        else:
            key = self._job_profile_stream_key()
        
        id_start = get_id_start(str(id_start), ndays, name=key)
        data, id_list = await self._stream_xread(key, id_start, count=count)     
         
        return data, id_list
    
    @async_client_wrapper
    async def delete_from_job_profile_stream(self, 
                                             id_list: List[Union[str, int]]=[],
                                             stage: bool=True):
        if stage:
            key = self._job_profile_stream_key_stage()
        else:
            key = self._job_profile_stream_key()
        pipeline = self.client.pipeline()
        for id in id_list:
            await pipeline.xdel(key, id)
        res = await pipeline.execute()
        
        return res

    async def set_jid2jpstream_idmap(self, 
                                     job_profile_id: Union[str, int],
                                     redis_job_profile_stream_id: Union[str, int], 
                                     ) -> Any:
        key_name = self.idash.job_profile
        key_var = ""
        idmap = {job_profile_id: redis_job_profile_stream_id}
        res = await self.add_to_idmap(key_name, key_var, idmap)
        
        return res
            
    async def get_jid2jpstream_idmap(self, job_profile_id: Union[str, int]) -> Any:
        key_name = self.idash.job_profile
        key_var = ""
        res = await self.get_from_idmap(key_name, key_var, job_profile_id)
        
        return res
    
    async def is_job_profile_id_in_job_profile_stream(self, 
                                                      job_profile_id: Union[str, int]
                                                      ) -> bool:
        res = await self.get_jid2jpstream_idmap(job_profile_id)
        if res:
            output = True
        else:
            output = False

        return output
    #----------------------------------------------------------------
    #--------------------Sample Job Profile from Stream--------------------------
    #----------------------------------------------------------------
    async def get_random_job_profile(self, user_profile_id: Union[str, int],
                                        count: int=1,
                                        ndays: int=3,
                                        xjob_profile_ids: list=[],
                                        stage=True):
        
        if stage:
            stream_key = self._job_profile_stream_key_stage()
        else:
            stream_key = self._job_profile_stream_key()
                    
        
        # get all job profiles from the stream starting from id_start        
        all_profiles, all_profile_ids = await self.get_from_job_profile_stream('0-0', 
                                                                               count=1000, 
                                                                               stage=stage)
        
        # get all job profiles that the user has seen
        idmap_dict = await self.get_user_job2redis_idmap(user_profile_id)        
        seen_job_profile_ids = [k for k, v in idmap_dict.items()]
        logger.good(f"Got n={len(seen_job_profile_ids)} job profiles that the user has seen")
        
        # add xredis_ids to the seen_profile_ids
        if xjob_profile_ids and isinstance(xjob_profile_ids, list):
            seen_job_profile_ids += xjob_profile_ids
            logger.good(f"Added n={len(xjob_profile_ids)} xjob_profile_ids to the seen job profile ids")
            
        # get all job profiles that the user has not seen
        unseen_profiles = []
        skipped_seen_profiles = []
        skipped_invalid_profiles = []
        for p, ix in zip(all_profiles, all_profile_ids):
            jpid = p.get('job_profile_id',"")
            if not jpid:
                m1 = f"job profile stream id={ix},  p={p}"
                logger.warn(f"Empty job_profile_id in {m1}. Skipping ...")
                continue
            
            # check if the job profile is valid and not in the seen job profile ids
            c1 = jpid in seen_job_profile_ids
            c2 = await self.is_invalid_job(jpid)
            if c1 or c2:
                if c1:
                    skipped_seen_profiles.append((p, ix))
                if c2:
                    skipped_invalid_profiles.append((p, ix))
            else:
                unseen_profiles.append((p, ix))
                
        # get random job profiles from the unseen profiles   
        nunseen = len(unseen_profiles)     
        k = count if nunseen>=count else nunseen
        output = random.choices(unseen_profiles, k=k)
        
        if len(skipped_seen_profiles)>0:
            logger.warn(f"Skipped {len(skipped_seen_profiles)} seen job profiles")
        if len(skipped_invalid_profiles)>0:
            logger.warn(f"Skipped {len(skipped_invalid_profiles)} invalid job profiles")
            
        m1 = f"{len(output)} (samples)/{len(unseen_profiles)} (unseen)"
        m2 = f"a total of {len(all_profiles)} job profiles"
        m3 = f"user_profile_id={user_profile_id}"
        logger.good(f'Got {m1} random job profiles from {m2} for {m3}')
        
        
        return list([p for p, _ in output]), list([ix for _, ix in output])
        
        
    #----------------------------------------------------------------
    #--------------------User Job Card Stream-------------------------
    # #---------------------------------------------------------------
    async def user_job_card_stream_xlen(self, user_profile_id: Union[str, int], id_start: str=""):
        key = self._user_job_card_stream_key(user_profile_id)
        val = await self._stream_xlen(key, id_start=id_start)
                        
        return val
        
    async def set_user_job_card_stream_latest_id(self, user_profile_id: Union[str, int], 
                                                 latest_job_profile_id: str):
        key = self._user_job_card_latest_id_key(user_profile_id)
        res = await self._set_set(key, latest_job_profile_id)
        return res   
        
    
    async def get_user_job_card_stream_latest_id(self, 
                                                 user_profile_id: Union[str, int], 
                                                 id_start: str="",
                                                 ndays: int=3):
        
        stream_key = self._user_job_card_stream_key(user_profile_id)
        latest_id_key = self._user_job_card_latest_id_key(user_profile_id)  
        
        if not id_start:                        
            id_start = await self._set_get(latest_id_key)  
            
        #print('*** Given job card stream id_start:', id_start)
        id_start = get_id_start(id_start, ndays, name=stream_key)
                              
        return id_start               
      
    @async_client_wrapper      
    async def delete_from_user_job_card_stream(self, user_profile_id: Union[str, int], 
                                               id_list: List[Union[str, int]]=[]):
        key = self._user_job_card_stream_key(user_profile_id)
        pipeline = self.client.pipeline()
        for id in id_list:
            await pipeline.xdel(key, id)
        res = await pipeline.execute()
        
        return res
        
    @async_client_wrapper        
    async def xrange_from_user_job_card_stream(self, user_profile_id: Union[str, int], 
                                               id_start: Union[str, int], id_end: Union[str, int], 
                                               **kwargs):
        key = self._user_job_card_stream_key(user_profile_id)
        result = await self.client.xrange(key, str(id_start), str(id_end))
                    
        all_results = []
        if len(result)>0:                    
            for item in result:   
                if isinstance(item[0], (list, tuple)):
                    id_start = item[0][0]
                    item_value = item[0][1]                            
                else:
                    id_start = item[0]                                    
                    item_value = item[1]   
                    
                content = self._xdata_prep(item_value, isxread=True)           
                all_results.append(content)
                
        return all_results
            
    async def add_to_user_job_card_stream(self, 
                                          user_profile_id: Union[str, int],
                                          job_profile_id: Union[str, int], 
                                          data: List[Dict], 
                                          latest_job_profile_id: str=""):
               
        key = self._user_job_card_stream_key(user_profile_id)
        res = await self._stream_xadd(key, data)
            
        if res and job_profile_id:
            # add redis job card id to user job_profile_id:redis_job_card_stream_id hash table
            idmap = {job_profile_id: res[0]}
            res2 = await self.set_user_job2redis_idmap(user_profile_id, idmap)            
            logger.good(f"Successfully {res2} added jpid to redis id map: {idmap}")
             
                                        
        # since we have prepared card from job profile, set the latest job profile id    
        if res and latest_job_profile_id:
            # set the latest job_profile_stream_id in Redis
            res2 = await self.set_user_job_profile_stream_latest_id(user_profile_id, 
                                                                    latest_job_profile_id)
            
            # set the job_profile_id to job_card_stream_id map
            idmap = {res[0]: latest_job_profile_id}
            res2 = await self.set_user_jcard2jstream_idmap(user_profile_id, idmap)
            logger.good(f"Successfully added job card-to-stream id map: {idmap}")
        else:            
            logger.warn(f"WARNING: Redis job profile stream id is empty for the job card. Probably the job card is computed using job_profile extracted outside the Redis job profile stream. Skipping setting idmap!")
        
        #res = await self._stream_xadd(key, data)
        return res
        
    
    async def get_from_user_job_card_stream(self, user_profile_id: Union[str, int], 
                                            id_start: str="",
                                            count: int=1, 
                                            ndays: int=1,
                                            exclude_ids: dict={}
                                            ):
        
        #caller_func_name = sys._getframe(1).f_code.co_name
         
        
        # get exclude ids
        xredis_card_ids = []
        try:            
            xredis_card_ids = exclude_ids.get('redis_card_ids', [])
            xjob_profile_ids = exclude_ids.get('job_profile_ids', [])
            if not xredis_card_ids and xjob_profile_ids:
                xredis_card_ids = await self.get_redis_card_ids_from_job_profile_ids(user_profile_id, 
                                                                                     xjob_profile_ids)   
            
            #xredis_reacted_card_ids = await self.get_user_reaction_idmap(user_profile_id)         
            #logger.good(f'Got n={len(xredis_reacted_card_ids)} and cards user racted so far')  
            
            #xredis_card_ids += xredis_reacted_card_ids   
        except Exception as e:
            logger.error(f"Error getting exclude ids: {e}")              
            
        
        # get the last key the user read
        try:                        
            id_start = await self.get_user_job_card_stream_latest_id(user_profile_id, 
                                                                     id_start=id_start,
                                                                     ndays=ndays)                    
            #logger.info(f'Getting user_job_card_stream using stream_key={stream_key} and last id: {id_start}')
        except Exception as e:
            logger.error(f"Error getting latest job profile id from Redis: {e}")
            raise
        
        cmust = ['job_profile_id']  # delete from stream if job_profile_id is empty
        data_list = []
        id_list = []
        timestamp_list = [id_start.split('-')[0]]
        
        # handle xredis_ids
        if xredis_card_ids:
            timestamp_list += [x.split('-')[0] for x in xredis_card_ids]
            
        limit = count
        stream_key = self._user_job_card_stream_key(user_profile_id)
        
        logger.good(f'Getting job cards starting from id_start: {id_start}')
        while True:
            res, rid = await self._stream_xread(stream_key, id_start, count=limit, cmust=cmust)
            for r, d in zip(rid, res):
                id_start = r
                job_profile_id = d.get('job_profile_id', "")
                has_reaction = await self.get_user_reaction_idmap(user_profile_id, job_profile_id)
                
                # accept jobs only if they are not in the exclude list or reacted before
                if has_reaction:
                    logger.warn(f"job_profile_id={job_profile_id} has reaction. Skipping ...")                
                elif r.split('-')[0] in timestamp_list:
                    logger.warn(f'job_profile_id={job_profile_id} is excluded or duplicated. Skipping ...')                    
                else:
                    limit -= 1
                    timestamp_list.append(r.split('-')[0])
                    
                    #
                    id_list.append(r)
                    data_list.append(d)
                    
            if limit <=0 or not res:
                break
                
        logger.good(f'Got n={len(id_list)} job cards: {id_list}')

        
        return data_list, id_list

    #----------------------------------------------------------------
    #--------------------User Reaction Stream-------------------------
    #----------------------------------------------------------------
    async def get_admin_user_reaction_stream_latest_id(self, admin_all_user_id: Union[str, int], 
                                                       user_profile_id: Union[str, int]):
        key = self._admin_user_reaction_latest_id_key(admin_all_user_id, user_profile_id)
        res = await self._set_get(key)        
        return res                
            
    async def add_to_user_reaction_stream(self, user_profile_id: Union[str, int], 
                                    data: List[Dict]):
               
        key = self._user_reaction_stream_key(user_profile_id)
        res = await self._stream_xadd(key, data, save_json=True)
        return res
        
        
    async def get_from_user_reaction_stream(self, user_profile_id: Union[str, int], 
                                      count: int=10, 
                                      id_start: str="0"):
        
        stream_key = self._user_reaction_stream_key(user_profile_id)
        data, id_list = await self._stream_xread(stream_key, id_start, count=count)
        
        return data, id_list

    #----------------------------------------------------------------
    #--------------------User Stat Set--------------------------
    #----------------------------------------------------------------
    @async_client_wrapper
    async def set_user_job_stats(self, all_user_id: Union[str, int], user_stat: dict):
        key = self._user_stat_key(all_user_id)
        #logger.info(f"Setting user stat json in Redis with key={key}")
        try:            
            ttl = seconds_until_midnight()
            res = await self._json_set(key, "$", user_stat)   
            _ = await self.client.expire(key, ttl)     
            return res
        except Exception as e:
            logger.error(f"Error setting user stat json in Redis: {e}")
            raise
        
    async def get_user_job_stats(self, all_user_id: Union[str, int]) -> dict:
        key = self._user_stat_key(all_user_id)
        #logger.info(f"Getting user stat json from Redis with key={key}")
        try:
            response_json = await self._json_get(key, "$")
            if isinstance(response_json, list):
                response_json = response_json[0] if response_json else {}
            return response_json
        except Exception as e:
            logger.error(f"Error getting user stat json from Redis: {e}")
            raise

    #----------------------------------------------------------------
    #--------------------User Profile Set--------------------------
    #----------------------------------------------------------------
    async def set_user_profile(self, user_profile_id: Union[str, int], user_profile: dict):
        key = self._user_profile_key(user_profile_id)
        try:
            responses_json = json.dumps(user_profile)
            res = await self._set_set(key, responses_json)
            return res
        except Exception as e:
            logger.error(f"Error setting chat bot responses in Redis: {e}")
            raise
        
        
    async def get_user_profile(self, user_profile_id: Union[str, int]) -> dict:
        key = self._user_profile_key(user_profile_id)
        try:
            responses_json = await self._set_get(key)
            if not responses_json:
                return {}
            else:
                return json.loads(responses_json)
        except Exception as e:
            logger.error(f"Error getting chat bot responses from Redis: {e}")
            raise
    
    async def set_user_profile_id(self, all_user_id: Union[str, int], user_profile_id: Union[str, int]):
        key = self._all_user_profile_id_key(all_user_id)
        logger.info(f"Setting user_profile_id={user_profile_id} in Redis with key={key}", fg="pink")
        res = await self._set_set(key, user_profile_id)
        res1 = await self._set_get(key)
        logger.good(f"Redis: Got res={res} and res1={res1}", fg="pink")
        return res
    
    async def get_user_profile_id(self, all_user_id: Union[str, int]) -> str:
        key = self._all_user_profile_id_key(all_user_id)
        res = await self._set_get(key)
        logger.info(f"Got user_profile_id={res} from Redis with key={key}", fg="pink")
        return str(res) if res else ""
      
    #----------------------------------------------------------------  
    #--------------------User Preference Set--------------------------
    #----------------------------------------------------------------
    async def set_user_preference(self, 
                                  user_profile_id: Union[str, int], 
                                  user_preference: dict):
        
        key = self._user_preference_key(user_profile_id)
        try:
            responses_json = json.dumps(user_preference)
            res = await self._set_set(key, responses_json)
            return res
        except Exception as e:
            logger.error(f"Error setting preference in Redis: {e}")
            return ""
        
    async def get_user_preference(self, 
                                  user_profile_id: Union[str, int]) -> dict:
        
        key = self._user_preference_key(user_profile_id)
        try:
            responses_json = await self._set_get(key)
            if not responses_json:
                logger.warn(f"Empty user preference in Redis with key={key}")
                return {}
            else:
                return json.loads(responses_json)
        except Exception as e:
            logger.error(f"Error getting preferences from Redis: {e}")
            raise
    
    async def set_user_preference_id(self, 
                                     all_user_id: Union[str, int], 
                                     user_preference_id: Union[str, int]):
        key = self._all_user_preference_id_key(all_user_id)
        logger.info(f"Setting user_preference_id={user_preference_id} in Redis with key={key}", fg="pink")
        res = await self._set_set(key, user_preference_id)
        res1 = await self._set_get(key)
        logger.good(f"Redis: Got res={res} and res1={res1}", fg="pink")
        return res
    
    async def get_user_preference_id(self, all_user_id: Union[str, int]) -> str:
        key = self._all_user_preference_id_key(all_user_id)
        res = await self._set_get(key)
        logger.info(f"Got user_preference_id={res} from Redis with key={key}", fg="pink")
        return str(res) if res else ""
        
    #
    async def key_exist(self, key: str) -> bool:
        
        exists = await self._exists(key)
        
        return exists>0
    
    async def keys_exist(self, keys: list) -> bool:
        
        exists = await self._exists(*keys)
        
        return exists>0    
    
    @async_client_wrapper
    async def delete_user_data(self, user_profile_id: str, keys: List[str]=[]):

        try:
            await self.client.delete(*keys)
        except Exception as e:
            logger.error(f"Error deleting user data from Redis: {e}")
            raise
    
    @async_client_wrapper   
    async def set_key_value_pairs(self, kv: Dict, ttl: timedelta=timedelta(days=1)):
        try:
            pipeline = self.client.pipeline()
            keys = []
            for key, value in kv.items():
                pipeline.set(key, value)
                keys.append(key)
            await pipeline.execute()
            await self.set_ttl(keys, ttl=ttl)
        except Exception as e:
            logger.error(f"Error setting batch keys in Redis: {e}")
            raise
        
    @async_client_wrapper      
    async def set_ttl(self, keys: List[str], ttl: timedelta=timedelta(days=1)):
        try:
            pipeline = self.client.pipeline()
            for key in keys:
                pipeline.expire(key, int(ttl.total_seconds()))
            await pipeline.execute()
        except Exception as e:
            logger.error(f"Error setting user profile TTL in Redis: {e}")
            raise
      
# --------------------------------------------------------------------------------------------
# ----------------------------------OpenAI Wrapper--------------------------------------
# --------------------------------------------------------------------------------------------
        
class RedisSyncClient(BaseRedisClient):
    def __init__(self,  run_stage="", max_stream_size=100000):
        super().__init__(run_stage=run_stage, max_stream_size=max_stream_size)
        
        self.host = config.cache.REDIS_HOST
        self.port = config.cache.REDIS_PORT
        self.client = None
        
    def connect(self):
        client = sredis.Redis(host=self.host, 
                                   port=self.port, 
                                   decode_responses=True, 
                                   ssl=True
                        )
        return client
     
    @client_wrapper
    def _stream_xadd(self, key: str, data: List[Dict], save_json: bool=False):
        '''
        add data to stream
        '''     
        if len(data)==0:
            logger.error("Passed empty data to add to stream with key={key}")
            return 
        
        tasks = []
        try:
            pipeline = self.client.pipeline()            
            # create all tasks            
            for item in data:
                if not item:
                    logger.warn(f"Empty item passed to add to stream with key={key}")
                    continue
                #print('XADD adding item.keys():',item.keys())
                fmt_item = self._xdata_prep(item, save_json=save_json)                
                pipeline.xadd(key, fmt_item,
                                maxlen=self.MAX_STREAM_SIZE, 
                                approximate=True)
                
            results = pipeline.execute()
        except Exception as e:
            logger.error(f"Error setting items in Redis Stream key={key}: {e}")
            raise
        
        return results

    @client_wrapper
    def _stream_xread(self, 
                        key: str, 
                        id_start: Union[str, int], 
                        count: int=1, 
                        cmust: list = []) -> Tuple[List[str],List[Dict]]:
        try:
            ncards = count
            id_list = []
            output = []
            skipped = 0            
            while True:
                #logger.info(f'Starting xread loop: id_start={id_start}, count={count} ...')
                
                result = self.client.xread(count=ncards, streams={key: id_start})
                                
                if not result:
                    logger.warn(f"{result} returned from stream content with key={key} & id={id_start}. Breaking..")
                    break
                else:                           
                    try:
                        if isinstance(result, dict):
                            result = result[key][0]
                        else:
                            if key==result[0][0]:
                                result = result[0][1]
                            else:
                                logger.error('Unable to determine the stream key from xread result. Breaking..')
                                idepth = 0
                                while isinstance(result, list):                                    
                                    logger.divider(f"depth={idepth}", fg='red')
                                    logger.error(f'result is list with len(result)={len(result)}')
                                    result = result[0]
                                    logger.error(f'0th item type is result.type={type(result)}')
                                    idepth += 1
                                    
                                break
                    except Exception as e:  
                        print('result:',result)                                              
                        logger.warn(f"Invalid xread output. Dict with key={key} and list value is expected. Breaking")
                        print(e)
                        break
                              
                logger.good(f'Got n={len(result)} items from stream content with key={key} & id={id_start}')                                         
                
                if len(result)>0:      
                                  
                    for item in result:   
                        if isinstance(item[0], (list, tuple)):
                            id_start = item[0][0]
                            item_value = item[0][1]                            
                        else:
                            id_start = item[0]                                    
                            item_value = item[1]  
                                                                           
                        content = self._xdata_prep(item_value, isxread=True)
                        if not content: 
                            print('Item extracted:', item) 
                            logger.warn(f"Stream content with key={key} & id={id_start} is empty! Delete + Skip ...")
                            #                          
                            rxdel = self.client.xdel(key, id_start)
                            logger.good(f"Deleted={rxdel} for item is empty: id={id_start} stream_key={key}")                            
                             
                            skipped += 1                           
                            continue
                        
                        for c in cmust:
                            if not content.get(c, ""):
                                rxdel = self.client.xdel(key, id_start)
                                logger.good(f"Deleted={rxdel} item for col={c} is empty: id={id_start} stream_key={key}")
                                skipped += 1
                                break
                                            
                        id_list.append(id_start)
                        output.append(content)
                                                                
                else:
                    print('result',result)
                    logger.warn(f"Empty result returned from stream content with key={key} & id={id_start}. Breaking..")
                    break
                    
                if len(output)==count:
                    logger.info(f"Got {len(output)} of requested={count} items from Redis Stream {key}. Breaking")
                    break   
                else:
                    ncards = count-len(output)
                    logger.info(f"Got {len(output)} of requested={count} items from Redis Stream {key} .. continuing")
                    logger.info(f'Setting ncards={ncards}, id_start={id_start}')
                    continue                                    
                
            logger.good(f'Got n={len(output)} VALID items from stream content with key={key}')
            
            return output, id_list
        
        except Exception as e:
            print(e)
            var = f"key={key}, id_start={id_start}, count={count}"
            logger.error(f"Error getting items from Redis Stream {var}")
            raise
        
         
    #--------------------Job Profile Stream--------------------------
    @client_wrapper
    def job_profile_stream_xlen(self, id_start=""):
        key = self._job_profile_stream_key()
        if not id_start:
            val = self.client.xlen(key)        
        else:
            arr = self.client.xrange(key, id_start, "+")
            val = len(arr)   
              
        return val
        
    @client_wrapper
    def set_user_job_profile_stream_latest_id(self, user_profile_id: str, latest_job_profile_id: str):
        key = self._user_job_profile_latest_id_key(user_profile_id)
        res = self.client.set(key, latest_job_profile_id)
        return res
    
    @client_wrapper       
    def get_user_job_profile_stream_latest_id(self, user_profile_id: str):
        key = self._user_job_profile_latest_id_key(user_profile_id)
        res = self.client.get(key)
        if not res:
            res = "0-0"
        return res
                
    def add_to_job_profile_stream(self, data: List[Dict], stage: bool=True):
        if stage:
            key = self._job_profile_stream_key_stage()
        else:
            key = self._job_profile_stream_key()
        res = self._stream_xadd(key, data)
        return res
        
    def get_from_job_profile_stream(self, id_start: Union[str, int]=0, 
                                          ndays: int=3, count: int=1, 
                                          stage: bool=True):
        if stage:
            key = self._job_profile_stream_key_stage()
        else:
            key = self._job_profile_stream_key()  
            
        id_start = get_id_start(str(id_start), ndays, name=key)
        data, id_list = self._stream_xread(key, id_start, count=count)       
        return data, id_list        
        
# --------------------------------------------------------------------------------------------
# ----------------------------------OpenAI Wrapper--------------------------------------
# --------------------------------------------------------------------------------------------
        
class RedisOpenAIAssistentClient():
    def __init__(self, midcol: str, max_stream_size=10000):
                
        self.midcol = midcol
        self.MAX_STREAM_SIZE = max_stream_size
        
        self.host = config.cache.REDIS_HOST
        self.port = config.cache.REDIS_PORT
        self.client = None
        
    def connect(self):
        client = sredis.Redis(host=self.host, 
                                   port=self.port, 
                                   decode_responses=True, 
                                   ssl=True
                        )
        return client
            
    def _thread_run_key(self, idval: str):
        return f"openai:thread_run:metadata.id:{idval}"
    
    @client_wrapper
    def set_openai_thread_run_ids(self, metadata, thread_id, run_id, ndays=1):
        ttl = timedelta(days=ndays)
        midval = metadata.get(self.midcol)
        
        if midval is None:
            logger.error(f"Metadata does not have {self.midcol} key. Cannot set openai thread run ids.")
            return
        
        key = self._thread_run_key(midval)
        print('setting in redis key:', key)
        
        data = json.dumps({"thread_id": thread_id, "run_id": run_id})
        
        res = self.client.set(key, data)
        
        if ttl:
            self.client.expire(key, ttl)
        
        return res    
    
    @client_wrapper
    def get_openai_thread_run_ids(self, metadata):
        midval = metadata.get(self.midcol)
        if midval is None:
            logger.error(f"Metadata does not have {self.midcol} key. Cannot get openai thread run ids.")
            return None, None
        
        key = self._thread_run_key(midval)
        output = self.client.get(key)
        if output:
            output = json.loads(output)
        else:
            output = {}
        
        return output.get('thread_id'), output.get('run_id') 
       
       

def prefixed_key(f):
    """
    A method decorator that prefixes return values.

    Prefixes any string that the decorated method `f` returns with the value of
    the `prefix` attribute on the owner object `self`.
    """

    def prefixed_method(*args, **kwargs):
        self = args[0]
        key = f(*args, **kwargs)
        return f'{self.prefix}:{key}'

    return prefixed_method


class Keys:
    """Methods to generate key names for Redis data structures."""

    def __init__(self, prefix: str = 'cache'):
        self.prefix = prefix      

    @prefixed_key
    def key(self, name: str, id: str = "") -> str:
        if id:
            return f'{name}:{id}'    
        else:
            return f'{name}'

    @prefixed_key
    def job_profile_stream_key(self, id: str = "") -> str:
        return f'job_profile_stream:user_profile_id:{id}'
    
    @prefixed_key
    def job_profile_key(self, id: str = "") -> str:
        return f'job_profile_id:{id}'
    
    @prefixed_key
    def all_user_key(self, id: str = "") -> str:
        return f'job_profile_id:{id}'    

    @prefixed_key
    def user_reaction_key(self, id: str = "") -> str:
        return f'user_reaction_id:{id}'  
    
    @prefixed_key
    def user_preference_key(self, id: str = "") -> str:
        return f'user_preference:all_user_id:{id}'     

    @prefixed_key
    def dynamic_user_preference_key(self, id: str = "") -> str:
        return f'dynamic_user_preference:all_user_id:{id}' 


def datetime_parser(dct):
    for k, v in dct.items():
        if isinstance(v, str) and v.endswith('+00:00'):
            try:
                dct[k] = datetime.fromisoformat(v)
            except:
                pass
    return dct