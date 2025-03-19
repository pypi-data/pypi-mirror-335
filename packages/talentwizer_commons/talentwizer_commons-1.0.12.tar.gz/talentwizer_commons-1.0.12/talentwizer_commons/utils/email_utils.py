from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import logging
import json
from typing import Dict, Any
import asyncio
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from talentwizer_commons.utils.db import mongo_database
from .core import celery_app, redis_client, check_redis_queue, get_redis_client
from .test_utils import get_test_delay
import os

logger = logging.getLogger(__name__)
sequence_collection = mongo_database["email_sequences"]
sequence_audit_collection = mongo_database["email_sequence_audits"]


def create_message(email_payload: dict, thread_id: str = None) -> dict:
    """Create email message with proper threading."""
    try:
        mime_msg = MIMEMultipart('alternative')
        mime_msg['to'] = ', '.join(email_payload['to_email'])
        mime_msg['from'] = email_payload.get('sender')
        
        # Add CC/BCC if present
        if email_payload.get('cc'):
            mime_msg['cc'] = ', '.join(email_payload['cc'])
        if email_payload.get('bcc'):
            mime_msg['bcc'] = ', '.join(email_payload['bcc'])
        
        # Handle threading for follow-up emails
        if not email_payload.get('is_initial') and thread_id:
            message_id = f"{thread_id}@mail.gmail.com"
            mime_msg['References'] = f"<{message_id}>"
            mime_msg['In-Reply-To'] = f"<{message_id}>"
            subject = email_payload.get('subject', '')
            if not subject.startswith('Re:'):
                subject = f"Re: {subject}"
            mime_msg['subject'] = subject
        else:
            mime_msg['subject'] = email_payload.get('subject', '')

        content = email_payload.get('content') or email_payload.get('body')

        # Add unsubscribe URL to content if enabled
        if email_payload.get('unsubscribe') and email_payload.get('sequence_id'):
            frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3001')
            unsubscribe_url = (
                f"{frontend_url}/unsubscribe"
                f"?sequence_id={email_payload['sequence_id']}"
                f"&public_identifier={email_payload['public_identifier']}"
            )
            unsubscribe_html = f"""
                <br><br>
                <div style="color: #666; font-size: 12px; margin-top: 20px; border-top: 1px solid #eee; padding-top: 10px;">
                    <p>Don't want to receive these emails? <a href="{unsubscribe_url}" style="color: #556bd8; text-decoration: underline;">Click here to unsubscribe</a></p>
                </div>
            """
            content += unsubscribe_html

        html_part = MIMEText(content, 'html', 'utf-8')
        mime_msg.attach(html_part)

        raw_message = base64.urlsafe_b64encode(mime_msg.as_bytes()).decode()
        
        message = {
            'raw': raw_message,
            'threadId': thread_id if thread_id else None
        }

        return message

    except Exception as e:
        logger.error(f"Error creating message: {str(e)}")
        raise

def build_gmail_service(token_data: dict):
    """Build Gmail service with proper error handling."""
    try:
        if not token_data:
            raise ValueError("Token data is required")

        required_fields = ['accessToken', 'clientId', 'clientSecret']
        missing_fields = [field for field in required_fields if not token_data.get(field)]
        
        if missing_fields:
            raise ValueError(f"Missing required token fields: {', '.join(missing_fields)}")

        scopes = [token_data.get('scope', 'https://www.googleapis.com/auth/gmail.send')]
        
        creds = Credentials(
            token=token_data["accessToken"],
            refresh_token=token_data.get("refreshToken"),
            token_uri="https://oauth2.googleapis.com/token",
            client_id=token_data["clientId"],
            client_secret=token_data["clientSecret"],
            scopes=scopes
        )

        return build('gmail', 'v1', credentials=creds)

    except Exception as e:
        logger.error(f"Failed to build Gmail service: {str(e)}", exc_info=True)
        raise

def send_email_from_user_email_sync(token_data: dict, email_payload: dict) -> dict:
    """Send email synchronously using Gmail API."""
    try:
        service = build_gmail_service(token_data)
        message = create_message(email_payload, email_payload.get('thread_id'))
        
        response = service.users().messages().send(
            userId='me',
            body=message
        ).execute()

        return {
            "status_code": 200,
            "message": "Email sent successfully",
            "threadId": response.get('threadId')
        }

    except Exception as e:
        logger.error(f"Error sending email: {str(e)}", exc_info=True)
        raise

def send_message_gmail(service, user_id, message, thread_id=None):
    """Send an email via Gmail API with proper thread handling."""
    try:
        if thread_id:
            message['threadId'] = thread_id
            logger.info(f"Added threadId to message body: {thread_id}")

        response = service.users().messages().send(
            userId=user_id,
            body=message
        ).execute()

        return {
            "status_code": 200,
            "message": "Email sent successfully",
            "threadId": response.get('threadId')
        }

    except Exception as e:
        logger.error(f"Error sending Gmail message: {str(e)}")
        raise

async def schedule_email(email_payload: dict, scheduled_time: datetime = None, token_data: dict = None) -> str:
    """Schedule an email to be sent at a specific time."""
    try:
        # Schedule task with correct name and metadata
        task = celery_app.send_task(
            'send_scheduled_email',
            kwargs={
                'email_payload': email_payload,
                'user_email': token_data.get('email'),
                'scheduled_time': scheduled_time.isoformat() if scheduled_time else None
            },
            eta=scheduled_time,
            queue='email_queue',
            routing_key='email.send'
        )
        
        return str(task.id)
    except Exception as e:
        logger.error(f"Failed to schedule email: {str(e)}", exc_info=True)
        raise
