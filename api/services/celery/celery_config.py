from celery import Celery
from api import config

# celery_app = Celery(
#     'worker',
#     broker=f'redis://localhost:6379/0',  
#     backend=f'redis://localhost:6379/0'
# )

# ssl_options = {
#     'ssl_cert_reqs': 'CERT_NONE'  # Must be a string per Celery/redis-py requirements
# }

celery_app = Celery(
    'worker',
    broker=config.cache.REDIS_URL,
    backend=config.cache.REDIS_URL
    # ssl = True,
    # decode_responses=False  
)

# # Configure task routes to ensure tasks go to the right queues
# celery_app.conf.task_routes = {
#     'process_audio_and_save_external_celery': {'queue': 'audio_processing'},
#     'process_upload_external_files_celery': {'queue': 'file_processing'},
# }

# Import tasks to register them with the worker
from . import tasks