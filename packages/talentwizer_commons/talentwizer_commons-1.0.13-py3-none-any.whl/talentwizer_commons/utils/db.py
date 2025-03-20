from dotenv import load_dotenv
load_dotenv()
from pymongo import MongoClient
import os
import redis
import logging

logger = logging.getLogger(__name__)

# Add error handling for missing MONGO_URI
mongo_uri = os.environ.get("MONGO_URI")
if not mongo_uri:
    raise ValueError(
        "MONGO_URI environment variable is not set. "
        "Please make sure you have a .env file with MONGO_URI defined."
    )

client = MongoClient(mongo_uri)
mongo_database = client[os.environ["MONGODB_DATABASE"]]

def get_sequence_collection():
    """Get the email sequences collection."""
    return mongo_database["email_sequences"]

def get_sequence_audit_collection():
    """Get the email sequence audits collection."""
    return mongo_database["email_sequence_audits"]

def get_mongo_database():
    """Get the MongoDB database instance."""
    return mongo_database

def get_redis_client(decode_responses=True):
    """Get Redis client with proper connection settings"""
    redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    return redis.Redis.from_url(
        redis_url,
        decode_responses=decode_responses,
        socket_timeout=5,
        socket_connect_timeout=5,
        health_check_interval=30,
        retry_on_timeout=True
    )

# Export the commonly used collections and functions
__all__ = [
    'mongo_database',
    'get_sequence_collection',
    'get_sequence_audit_collection',
    'get_mongo_database'
]