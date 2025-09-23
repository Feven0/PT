from celery import Celery
from api import config


celery_app = Celery(
    'socket_only_worker',
    broker=config.cache.REDIS_URL,
    backend=config.cache.REDIS_URL
)

# only import the socket test tasks to avoid pulling in heavy modules
celery_app.conf.imports = (
    "api.services.celery.socket_test_tasks",
)





