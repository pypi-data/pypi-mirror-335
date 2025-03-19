from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId
from enum import Enum
from talentwizer_commons.utils.db import mongo_database

status_router = s = APIRouter()

# MongoDB Setup
status_collection = mongo_database["statuses"]

class StatusValue(str, Enum):
    NOT_CONTACTED = "NOT_CONTACTED"
    CONTACTED = "CONTACTED"
    SCREENING_CALL = "SCREENING_CALL"
    REJECTED = "REJECTED"
    ON_HOLD = "ON_HOLD"
    HIRED = "HIRED"

class Status(BaseModel):
    status_label: str
    status_value: StatusValue

class StatusUpdate(BaseModel):
    ids: List[str]
    status: StatusValue

@s.put("/bulk")
async def update_bulk_statuses(status_update: StatusUpdate):
    object_ids = [ObjectId(id) for id in status_update.ids]
    result =  status_collection.update_many(
        {"_id": {"$in": object_ids}},
        {"$set": {"status_value": status_update.status}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="No statuses updated")
    return {"message": f"{result.modified_count} statuses updated"}

@s.post("/", response_model=Status)
async def create_status(status: Status):
    status_dict = status.dict()
    result = status_collection.insert_one(status_dict)
    status_dict["_id"] = str(result.inserted_id)
    return status_dict

@s.get("/", response_model=List[Status])
async def get_statuses():
    statuses = status_collection.find().to_list(1000)
    for status in statuses:
        status["_id"] = str(status["_id"])
    return statuses

@status_router.get("/statuses/label/{status_value}")
async def get_status_label(status_value: StatusValue):
    status_document =  status_collection.find_one({"status_value": status_value})
    if not status_document:
        raise HTTPException(status_code=404, detail="Status not found")
    return {"status_label": status_document["status_label"]}

