from .celery_init import celery_app, send_scheduled_email, restore_persisted_tasks
from .core import REDIS_URL, CELERY_BROKER_URL, redis_client

__all__ = [
    'celery_app',
    'send_scheduled_email',  # Important - explicitly export the task
    'restore_persisted_tasks',
    'REDIS_URL',
    'CELERY_BROKER_URL',
    'redis_client'
]
