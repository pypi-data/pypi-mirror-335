from llama_index.vector_stores.mongodb import MongoDBAtlasVectorSearch

import os
import logging
import pymongo

def get_mongo_store():
    try:
        logger = logging.getLogger("uvicorn")
        mongo_client = get_mongo_client()
        store = MongoDBAtlasVectorSearch(
                mongo_client,
                db_name=os.environ["MONGODB_DATABASE"],
                collection_name=os.environ["MONGODB_VECTORS"],
                index_name=os.environ["MONGODB_VECTOR_INDEX"],
            )
        return store
    except Exception as e:
        logger.error(f"Error while connecting to index: {e}")
        # Handle the error as required
        return None 

def get_mongo_client():
    """Establish connection to the MongoDB."""
    try:
        mongo_uri = os.environ["MONGO_URI"]
        client = pymongo.MongoClient(mongo_uri)
        print("Connection to MongoDB successful")
        return client
    except pymongo.errors.ConnectionFailure as e:
        print(f"Connection failed: {e}")
        return None


