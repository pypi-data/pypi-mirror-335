from datetime import datetime, timedelta
import redis
import logging
from .db import get_sequence_audit_collection
from .celery_init import get_redis_url

logger = logging.getLogger(__name__)

async def cleanup_stale_tasks(older_than_hours: int = 24):
    """Clean up stale tasks from Redis and update MongoDB status."""
    try:
        redis_client = redis.Redis.from_url(
            get_redis_url(),
            decode_responses=True
        )
        audit_collection = get_sequence_audit_collection()
        cutoff_time = datetime.utcnow() - timedelta(hours=older_than_hours)
        
        # Clean up Redis task events
        pattern = "flower:task:*"
        for key in redis_client.scan_iter(pattern):
            try:
                task_id = key.split(":")[-1]
                # Check MongoDB status
                task = audit_collection.find_one({"schedule_id": task_id})
                if task and task["status"] in ["SENT", "FAILED", "CANCELLED"]:
                    redis_client.delete(key)
                    logger.info(f"Cleaned up completed task {task_id} from Redis")
            except Exception as e:
                logger.error(f"Error cleaning up task {key}: {e}")

        # Clean up Redis queues
        for queue in ['unacked', 'reserved', 'scheduled']:
            queue_key = f"celery:{queue}"
            try:
                # Get all tasks with scores (timestamps) before cutoff
                stale_tasks = redis_client.zrangebyscore(
                    queue_key,
                    '-inf',
                    float(cutoff_time.timestamp())
                )
                if stale_tasks:
                    redis_client.zrem(queue_key, *stale_tasks)
                    logger.info(f"Removed {len(stale_tasks)} stale tasks from {queue_key}")
            except Exception as e:
                logger.error(f"Error cleaning up queue {queue_key}: {e}")

        # Update MongoDB status for stale scheduled tasks
        result = audit_collection.update_many(
            {
                "status": "SCHEDULED",
                "scheduled_time": {"$lt": cutoff_time}
            },
            {
                "$set": {
                    "status": "FAILED",
                    "error_message": "Task expired",
                    "updated_at": datetime.utcnow()
                }
            }
        )
        logger.info(f"Updated {result.modified_count} stale tasks in MongoDB")

    except Exception as e:
        logger.error(f"Error in cleanup_stale_tasks: {e}")
        raise

