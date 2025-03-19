import os
import json
from datetime import datetime
from .celery_init import celery_app
from celery.result import AsyncResult
import redis
import logging

logger = logging.getLogger(__name__)

class TaskStateManager:
    def __init__(self):
        self.redis_client = redis.Redis.from_url(
            os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
            decode_responses=True
        )

    def restore_tasks(self):
        """Restore tasks from Redis persistence"""
        try:
            # Get all tasks from Redis sorted sets
            task_keys = ['celery:unacked', 'celery:reserved', 'celery:scheduled']
            restored_tasks = []

            for key in task_keys:
                tasks = self.redis_client.zrange(key, 0, -1, withscores=True)
                for task_id, score in tasks:
                    try:
                        # Get task result from Celery
                        task = AsyncResult(task_id, app=celery_app)
                        if task.state not in ['SUCCESS', 'FAILURE', 'REVOKED']:
                            restored_tasks.append({
                                'id': task_id,
                                'state': task.state,
                                'queue': key.split(':')[1],
                                'scheduled': datetime.fromtimestamp(score).isoformat()
                            })
                    except Exception as e:
                        logger.error(f"Error restoring task {task_id}: {str(e)}")

            logger.info(f"Restored {len(restored_tasks)} tasks")
            return restored_tasks

        except Exception as e:
            logger.error(f"Error in restore_tasks: {str(e)}")
            return []

    def save_task_state(self, task_id: str, state: dict):
        """Save task state to Redis"""
        try:
            self.redis_client.set(
                f'celery:task_state:{task_id}',
                json.dumps(state),
                ex=86400  # expire after 24 hours
            )
        except Exception as e:
            logger.error(f"Error saving task state: {str(e)}")

    def get_task_state(self, task_id: str) -> dict:
        """Get task state from Redis"""
        try:
            state = self.redis_client.get(f'celery:task_state:{task_id}')
            return json.loads(state) if state else {}
        except Exception as e:
            logger.error(f"Error getting task state: {str(e)}")
            return {}

task_state_manager = TaskStateManager()
