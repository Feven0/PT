from celery import Celery
from api import config


celery_app = Celery(
    'worker',
    broker=config.cache.REDIS_URL,
    backend=config.cache.REDIS_URL
    # ssl = True,
    # decode_responses=False  
)

# Configure Redis transport options to organize keys under parrot_celery_tasks namespace
celery_app.conf.update(
    # Organize broker (kombu) keys under parrot_celery_tasks:kombu namespace
    broker_transport_options={
        'global_keyprefix': 'parrot_celery_tasks:_kombu:',
        'fanout_prefix': True,
        'fanout_patterns': True,
    },
    # Organize result backend keys under parrot_celery_tasks:task_meta namespace  
    result_backend_transport_options={
        'global_keyprefix': 'parrot_celery_tasks:task_meta:',
    },
    # Set task result key prefix
    result_backend='redis://' + config.cache.REDIS_URL.split('redis://')[-1],
    # Additional organization settings
    task_result_expires=3600,  # 1 hour expiry for task results
    result_expires=3600,
)

# Import tasks to register them with the worker
from . import audio_tasks
