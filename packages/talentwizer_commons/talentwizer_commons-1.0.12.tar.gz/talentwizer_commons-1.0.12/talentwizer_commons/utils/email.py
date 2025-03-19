import logging
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
import redis
from typing import List, Optional
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from urllib.parse import unquote
import os

from .core import (
    REDIS_URL,
    CELERY_BROKER_URL,
    redis_client,
    celery_app
)
from .email_utils import (
    send_email_from_user_email_sync,
    schedule_email,
    create_message
)
from .token_utils import refresh_access_token, is_token_expired
from .sequence_utils import (
    sequence_audit_collection,
    )

logger = logging.getLogger(__name__)

# Keep only email-specific models and routes
class EmailPayload(BaseModel):
    from_email: Optional[EmailStr] = None
    to_email: List[EmailStr]
    cc: Optional[List[EmailStr]] = None
    bcc: Optional[List[EmailStr]] = None
    subject: Optional[str] = None
    body: Optional[str] = None
    attachments: Optional[List[str]] = None

email_router = e = APIRouter()

# Keep only email-specific routes and functions
async def send_email_by_admin_account(emailPayload: EmailPayload):
    from_email = os.getenv("ADMIN_EMAIL")
    if not from_email:
        logging.error("Admin email is not set in environment variables")
        return False

    to_email = emailPayload.to_email
    subject = emailPayload.subject
    body = emailPayload.body
    attachments = emailPayload.attachments

    comma_separated_emails = ",".join(to_email) if to_email else ""
    if not comma_separated_emails:
        logging.error("Recipient email addresses are empty or malformed")
        return False

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = unquote(comma_separated_emails)

    if subject:
        msg['Subject'] = subject
    else:
        logging.warning("Email subject is empty")

    if body:
        msg.attach(MIMEText(body, 'plain'))
    else:
        logging.warning("Email body is empty")

    # Attach files if any
    if attachments:
        for attachment_path in attachments:
            try:
                with open(attachment_path, "rb") as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                    encoders.encode_base64(part)
                    filename = os.path.basename(attachment_path)
                    part.add_header('Content-Disposition', f'attachment; filename={filename}')
                    msg.attach(part)
            except FileNotFoundError:
                logging.error(f"Attachment file not found: {attachment_path}")
            except PermissionError:
                logging.error(f"Permission denied for attachment file: {attachment_path}")
            except Exception as e:
                logging.error(f"Unexpected error attaching file {attachment_path}: {e}")
    
    try:
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        s.login(from_email, os.getenv("ADMIN_EMAIL_PASSWORD"))
        s.sendmail(from_email, unquote(comma_separated_emails), msg.as_string())
        s.quit()
        logging.info("Email sent successfully through admin email")
        return True
    except smtplib.SMTPAuthenticationError:
        logging.error("SMTP authentication failed. Check ADMIN_EMAIL and ADMIN_EMAIL_PASSWORD")
    except smtplib.SMTPConnectError as e:
        logging.error(f"SMTP connection error: {e}")
    except smtplib.SMTPRecipientsRefused:
        logging.error(f"All recipients were refused: {comma_separated_emails}")
    except smtplib.SMTPException as e:
        logging.error(f"SMTP error occurred: {e}")
    except Exception as e:
        logging.error(f"Unexpected error while sending email: {e}")
    return False

@e.get("/scheduled-tasks/stats")
async def get_scheduled_tasks_stats():
    stats = {
        "redis": {"status": "unknown"},
        "celery": {"status": "unknown"},
        "database": {"status": "unknown"}
    }
    try:
        # Redis checks with connection pooling and error handling
        try:
            redis_pool = redis.ConnectionPool.from_url(
                CELERY_BROKER_URL,
                socket_timeout=5,
                socket_connect_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30,
                max_connections=10
            )
            
            redis_client = redis.Redis(connection_pool=redis_pool)
            redis_client.ping()  # Test connection
            
            stats["redis"] = {
                "status": "connected",
                "unacked": redis_client.zcard('unacked'),
                "scheduled": redis_client.zcard('scheduled'),
                "queue_length": redis_client.llen('celery')
            }
        except redis.ConnectionError as e:
            logger.error(f"Redis connection error: {str(e)}")
            stats["redis"].update({
                "status": "disconnected",
                "error": str(e)
            })
        finally:
            if 'redis_pool' in locals():
                redis_pool.disconnect()

        # Celery checks with timeout
        try:
            # Only use supported timeout parameter
            inspector = celery_app.control.inspect(timeout=3.0)
            
            # Check worker availability
            if not inspector.ping():
                raise ConnectionError("No Celery workers responded to ping")
            
            active = inspector.active() or {}
            scheduled = inspector.scheduled() or {}
            reserved = inspector.reserved() or {}
            
            stats["celery"] = {
                "status": "connected",
                "active": sum(len(tasks) for tasks in active.values()),
                "reserved": sum(len(tasks) for tasks in reserved.values()),
                "scheduled": sum(len(tasks) for tasks in scheduled.values())
            }
        except (ConnectionError, TimeoutError, OSError) as e:
            logger.error(f"Celery inspection error: {str(e)}")
            stats["celery"].update({
                "status": "disconnected",
                "error": str(e)
            })

        # Database checks with error handling
        try:
            pipeline = [{"$group": {"_id": "$status", "count": {"$sum": 1}}}]
            audit_counts = list(sequence_audit_collection.aggregate(pipeline))
            
            stats["database"] = {
                "status": "connected",
                "audit_counts": audit_counts
            }
        except Exception as e:
            logger.error(f"Database error: {str(e)}")
            stats["database"].update({
                "status": "error",
                "error": str(e)
            })

        return stats

    except Exception as e:
        logger.error(f"Failed to get task stats: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "error": str(e),
            "component_status": {
                "redis": stats["redis"]["status"],
                "celery": stats["celery"]["status"],
                "database": stats["database"]["status"]
            }
        }