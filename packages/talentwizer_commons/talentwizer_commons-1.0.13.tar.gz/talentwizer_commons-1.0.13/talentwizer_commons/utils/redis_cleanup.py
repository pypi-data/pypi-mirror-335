import redis
import os
import logging

logger = logging.getLogger(__name__)

def cleanup_redis_queues():
    """Initialize Redis queues with proper formats."""
    try:
        redis_url = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
        redis_client = redis.Redis.from_url(
            redis_url,
            decode_responses=True,
            socket_timeout=5,
            retry_on_timeout=True
        )
        
        # Clear old keys first
        for key in ['unacked', 'reserved', 'scheduled']:
            redis_client.delete(f'celery:{key}')
        
        # Initialize with dummy data that will be replaced
        current_timestamp = redis_client.time()[0]
        dummy_data = {
            'dummy_task': float(current_timestamp)
        }
        
        # Initialize sorted sets with dummy data
        redis_client.zadd('celery:unacked', dummy_data)
        redis_client.zadd('celery:reserved', dummy_data)
        redis_client.zadd('celery:scheduled', dummy_data)
        
        # Remove dummy data
        redis_client.zrem('celery:unacked', 'dummy_task')
        redis_client.zrem('celery:reserved', 'dummy_task')
        redis_client.zrem('celery:scheduled', 'dummy_task')
        
        logger.info("Redis queues initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize Redis queues: {str(e)}")
        raise

if __name__ == "__main__":
    cleanup_redis_queues()
