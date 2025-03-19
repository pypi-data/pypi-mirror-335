import redis
import os
from celery import Celery
from kombu import Queue, Exchange
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Redis Configuration
def get_redis_url():
    """Get properly formatted Redis URL."""
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = os.getenv('REDIS_PORT', '6379')
    REDIS_DB = os.getenv('REDIS_DB', '0')
    REDIS_SSL = os.getenv("REDIS_SSL", "false").lower() == "true"
    return f"{'rediss' if REDIS_SSL else 'redis'}://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"

REDIS_URL = get_redis_url()
CELERY_BROKER_URL = REDIS_URL  # Used by both Celery and FastAPI

# Initialize Redis
redis_client = redis.Redis.from_url(
    REDIS_URL,
    decode_responses=True,
    socket_timeout=5,
    retry_on_timeout=True,
    health_check_interval=30
)

# Initialize Celery
celery_app = Celery(
    'talentwizer_commons',
    broker=CELERY_BROKER_URL,
    backend=CELERY_BROKER_URL
)

# Update Celery configuration
celery_app.conf.update(
    broker_connection_retry=True,
    broker_connection_max_retries=None,
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    task_track_started=True,
    task_ignore_result=False,
    task_store_errors_even_if_ignored=True,
    result_expires=None,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,
    worker_lost_wait=30
)

# Queue configuration
default_exchange = Exchange('default', type='direct')
email_exchange = Exchange('email', type='direct')

celery_app.conf.task_queues = (
    Queue('celery', default_exchange, routing_key='celery'),
    Queue('email_queue', email_exchange, routing_key='email.#'),
)

# Redis helpers
def get_redis_client() -> redis.Redis:
    """Get a new Redis client instance."""
    return redis.Redis.from_url(
        REDIS_URL,
        decode_responses=True,
        socket_timeout=5,
        retry_on_timeout=True,
        health_check_interval=30
    )

async def check_redis_queue(redis_client: redis.Redis, key: str, task_id: str) -> bool:
    """Safely check Redis queue existence and type."""
    try:
        key_type = redis_client.type(key)
        if key_type == b'zset':
            return redis_client.zscore(key, task_id) is not None
        elif key_type == b'none':
            redis_client.zadd(key, {task_id: float(datetime.now().timestamp())})
            return True
        else:
            redis_client.delete(key)
            redis_client.zadd(key, {task_id: float(datetime.now().timestamp())})
            return True
    except Exception as e:
        logger.error(f"Redis operation failed for key {key}: {str(e)}")
        return False

# Fix Redis cleanup
def cleanup_redis_queues():
    """Clean up Redis queues before starting Celery."""
    try:
        redis_client = get_redis_client()
        keys_to_clean = [
            'unacked*', 'reserved*', 'flower:*',
            'celery*', 'email_queue*',
            '_kombu*', 'flower_task*'
        ]
        
        for pattern in keys_to_clean:
            try:
                keys = redis_client.keys(pattern)
                if keys:
                    redis_client.delete(*keys)
                    logger.info(f"Cleaned {len(keys)} keys matching {pattern}")
            except Exception as e:
                logger.error(f"Error cleaning Redis pattern {pattern}: {str(e)}")
    except Exception as e:
        logger.error(f"Error in cleanup_redis_queues: {str(e)}")
    finally:
        try:
            redis_client.close()
        except:
            pass

# Export commonly used instances/variables
__all__ = [
    'REDIS_URL',
    'CELERY_BROKER_URL',
    'redis_client',
    'celery_app',
    'get_redis_client',
    'check_redis_queue',
    'cleanup_redis_queues'
]
