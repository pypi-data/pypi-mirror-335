from datetime import datetime, timezone
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError
import logging
from talentwizer_commons.utils.db import mongo_database
import asyncio
from typing import Dict, Any

logger = logging.getLogger(__name__)
session_db = mongo_database["session"]
__all__ = ['get_valid_token', 'get_valid_token_async']

def get_token_from_session(email: str, lookup_type: str = "integration") -> dict:
    """Get integration token data from sessions collection.
    
    Args:
        email: The email address to look up
        lookup_type: Either "main" (to find integration by main email) or "integration" (to find directly by integration email)
    """
    try:
        query = {}
        if (lookup_type == "main"):
            # Find integration session using main email
            query = {
                "$or": [
                    {"email": email},  # Direct match on main email
                    {"linkedAccounts.mainEmail": email}  # Match on linked account main email
                ]
            }
            logger.info(f"Looking up integration session with main email: {email}")
        else:
            # Find directly by integration email
            query = {
                "$or": [
                    {"integrationSession.email": email},  # Direct match on integration email
                    {"linkedAccounts.integrationEmail": email}  # Match on linked integration email
                ]
            }
            logger.info(f"Looking up session with integration email: {email}")

        logger.debug(f"Using query: {query}")
        session = session_db.find_one(query)
        
        if not session:
            error_msg = f"No session found for {lookup_type} email {email}"
            logger.error(error_msg)
            raise ValueError(error_msg)
            
        if not session.get("integrationSession"):
            error_msg = f"No integration session found for {lookup_type} email {email}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        logger.info(f"Found integration session: Main={session.get('email')}, Integration={session['integrationSession']['email']}")
        return session["integrationSession"]
        
    except Exception as e:
        logger.error(f"Error getting token data: {str(e)}")
        raise

def is_token_expired(token_data: dict) -> bool:
    """Check if token is expired or will expire in next 5 minutes."""
    if not token_data.get('expires_at'):
        return True
    
    expires_at = token_data['expires_at']
    now = int(datetime.now(timezone.utc).timestamp())
    return now >= (expires_at - 300)

def refresh_access_token(token_data: dict) -> dict:
    """Refresh access token and update sessions collection."""
    try:
        creds = Credentials(
            token=token_data["accessToken"],
            refresh_token=token_data["refreshToken"],
            token_uri="https://oauth2.googleapis.com/token",
            client_id=token_data["clientId"],
            client_secret=token_data["clientSecret"],
            scopes=token_data["scope"].split()
        )
        
        # Create a Request object and use it to refresh credentials
        request = Request()
        creds.refresh(request)  # Pass the request object to the refresh method
        
        updated_token = {
            **token_data,
            "accessToken": creds.token,
            "expires_at": int(creds.expiry.timestamp()) if creds.expiry else None,
            "refreshToken": creds.refresh_token or token_data["refreshToken"]
        }
        
        # Update token in database
        mongo_database["sessions"].update_one(
            {"integrationSession.email": token_data["email"]},
            {
                "$set": {
                    "integrationSession.accessToken": updated_token["accessToken"],
                    "integrationSession.refreshToken": updated_token["refreshToken"],
                    "integrationSession.expires_at": updated_token["expires_at"]
                }
            }
        )
        
        logger.info(f"Successfully refreshed token for {token_data['email']}")
        return updated_token
        
    except Exception as e:
        logger.error(f"Failed to refresh token: {str(e)}", exc_info=True)
        raise

def get_valid_token(email: str, lookup_type: str = "integration") -> Dict[str, Any]:
    """Get valid token, refreshing if needed."""
    token_data = get_token_from_session(email, lookup_type)
    
    if is_token_expired(token_data):
        logger.info(f"Refreshing expired token for {email}")
        token_data = refresh_access_token(token_data)
    
    return token_data

async def get_valid_token_async(email: str, lookup_type: str = "integration") -> Dict[str, Any]:
    """Async wrapper for get_valid_token that accepts lookup_type parameter."""
    return await asyncio.to_thread(get_valid_token, email, lookup_type)

async def update_stored_token(token_data: dict):
    """Update the stored token in the database."""
    try:
        mongo_database["sessions"].update_one(
            {"integrationSession.email": token_data["email"]},
            {
                "$set": {
                    "integrationSession.accessToken": token_data["accessToken"],
                    "integrationSession.refreshToken": token_data["refreshToken"],
                    "integrationSession.expires_at": token_data["expires_at"]
                }
            }
        )
        logger.info(f"Successfully updated stored token for {token_data['email']}")
    except Exception as e:
        logger.error(f"Failed to update stored token: {str(e)}", exc_info=True)
        raise
