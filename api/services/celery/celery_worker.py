from celery import Celery
from api import config


celery_app = Celery(
    'worker',
    broker=config.cache.REDIS_URL,
    backend=config.cache.REDIS_URL
    # ssl = True,
    # decode_responses=False  
)

# Import tasks to register them with the worker
from . import audio_tasks
