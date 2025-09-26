import redis
import json
from typing import Dict, List, Optional
from api.services.secret import get_auth
from api import config
REDIS_PASSWORD = get_auth(ssmkey='REDIS_PASSWORD')

class RedisBase:
    """Base class for Redis operations"""
    
    def __init__(self, db: int = 0):
        self.redis = redis.Redis(
            host=config.cache.REDIS_HOST,
            port=config.cache.REDIS_PORT,
            password=REDIS_PASSWORD,
            # ssl = True,
            # decode_responses=False  
        )

    def get(self, key: str) -> Optional[Dict]:
        """Get a value from Redis"""
        try:
            data = self.redis.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            print(f"Redis get error: {e}")
            return None
            
    def set(self, key: str, value: Dict, ttl: Optional[int] = None) -> None:
        """Set a value in Redis with optional TTL"""
        try:
            data = json.dumps(value)
            if ttl:
                self.redis.setex(key, ttl, data)
            else:
                self.redis.set(key, data)
        except Exception as e:
            print(f"Redis set error: {e}")
            
    def delete(self, key: str) -> None:
        """Delete a key from Redis"""
        try:
            self.redis.delete(key)
        except Exception as e:
            print(f"Redis delete error: {e}")
            
    def batch_get(self, keys: List[str]) -> Dict[str, Dict]:
        """Batch get values from Redis"""
        if not keys:
            return {}
            
        try:
            pipe = self.redis.pipeline()
            for key in keys:
                pipe.get(key)
            results = pipe.execute()
            
            return {
                key: json.loads(value) 
                for key, value in zip(keys, results) 
                if value is not None
            }
        except Exception as e:
            print(f"Redis batch_get error: {e}")
            return {}
            
    def batch_set(self, key_values: Dict[str, Dict], ttl: Optional[int] = None) -> None:
        """Batch set values in Redis with optional TTL"""
        if not key_values:
            return
            
        try:
            pipe = self.redis.pipeline()
            for key, value in key_values.items():
                data = json.dumps(value)
                if ttl:
                    pipe.setex(key, ttl, data)
                else:
                    pipe.set(key, data)
            pipe.execute()
        except Exception as e:
            print(f"Redis batch_set error: {e}")
            
    def batch_delete(self, keys: List[str]) -> None:
        """Batch delete keys from Redis"""
        if not keys:
            return
            
        try:
            pipe = self.redis.pipeline()
            for key in keys:
                pipe.delete(key)
            pipe.execute()
        except Exception as e:
            print(f"Redis batch_delete error: {e}") 