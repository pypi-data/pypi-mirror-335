import datetime
from bson import ObjectId

from pydantic import BaseModel
from utils.db import mongo_database

class _Prompt(BaseModel):
    """
    The data of a prompt consisting of the prompt, timestamp and job id.
    """
    prompt: str = ""
    timestamp: datetime.datetime = datetime.datetime.now()
    job_id: str = ""

# function to save promptt to database with timestamp
def save_prompt(data: _Prompt):
    """
    Save prompt to database with timestamp.
    
    :param prompt: Prompt to save.
    :type prompt: str
    :return: Empty response.
    :rtype: dict
    """
    # save prompts to database
    result = mongo_database["Prompts"].insert_one(data.dict())

    # update prompt id in job table
    mongo_database["Job"].update_one(
        {"_id": ObjectId(data.job_id)},
        {"$push": {"prompts": str(result.inserted_id)}}
    )

    return {"id": str(result.inserted_id)}

def get_prompts(job_id: str):
    """
    Get all prompts for a job.
    
    :param job_id: ID of the job to get prompts for.
    :type job_id: str
    :return: List of prompts.
    :rtype: list
    """
    prompts = mongo_database["Job"].find_one({"_id": ObjectId(job_id)})["prompts"]

    return list(prompts)

def get_prompt_details(prompt_id: str):
    """
    Get details of a prompt.
    
    :param prompt_id: ID of the prompt to get details for.
    :type prompt_id: str
    :return: Details of the prompt.
    :rtype: dict
    """
    prompt = mongo_database["Prompts"].find_one({"_id": ObjectId(prompt_id)})

    return prompt