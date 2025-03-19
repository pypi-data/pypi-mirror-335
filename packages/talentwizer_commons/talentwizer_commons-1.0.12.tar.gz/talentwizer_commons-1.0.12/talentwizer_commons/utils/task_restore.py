import os
import redis
import logging
from datetime import datetime
import json
from .celery_init import celery_app, send_scheduled_email
from .db import mongo_database
from .core import redis_client, get_redis_client

logger = logging.getLogger(__name__)

def restore_tasks():
    """Restore and reschedule tasks from MongoDB."""
    try:
        logger.info("Starting task restoration process...")
        restored_count = 0
        sequence_audit_collection = mongo_database["email_sequence_audits"]

        # Find all SCHEDULED tasks that were not sent and are past due
        tasks = sequence_audit_collection.find({
            "status": "SCHEDULED",
            "scheduled_time": {"$lt": datetime.utcnow()}
        }).sort([("sequence_id", 1), ("step_index", 1)])

        for task in tasks:
            try:
                # Get sequence for thread ID
                sequence = sequence_collection.find_one({"_id": ObjectId(task["sequence_id"])})
                if sequence:
                    # Update email payload with sequence thread ID
                    email_payload = task["email_payload"]
                    email_payload["thread_id"] = sequence.get("thread_id")

                # Schedule for immediate execution
                new_task = celery_app.send_task(
                    'send_scheduled_email',  # Note: simplified task name
                    kwargs={
                        'email_payload': email_payload,
                        'user_email': email_payload.get('sender')
                    },
                    queue='email_queue',
                    routing_key='email.send'
                )

                # Update audit record
                sequence_audit_collection.update_one(
                    {"_id": task["_id"]},
                    {"$set": {
                        "schedule_id": new_task.id,
                        "rescheduled_at": datetime.utcnow()
                    }}
                )

                restored_count += 1
                logger.info(f"Restored task {task['_id']} with new ID {new_task.id}")

            except Exception as e:
                logger.error(f"Failed to restore task {task.get('_id')}: {str(e)}")
                continue

        logger.info(f"Task restoration completed. Restored {restored_count} tasks")
        return restored_count

    except Exception as e:
        logger.error(f"Task restoration failed: {str(e)}")
        return 0


