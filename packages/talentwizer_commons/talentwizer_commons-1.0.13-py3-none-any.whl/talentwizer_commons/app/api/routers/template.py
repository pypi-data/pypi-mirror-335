from fastapi import APIRouter, HTTPException, Body, Path
from pydantic import BaseModel, Field, model_validator  # Change validator to model_validator
from typing import List, Optional
from bson import ObjectId
from talentwizer_commons.utils.db import mongo_database
from talentwizer_commons.utils.template_utils import populate_template_v2
from talentwizer_commons.utils.objectid import PydanticObjectId  # Update import
from datetime import datetime
import logging
import traceback

# Configure logging
logger = logging.getLogger("talentwizer_commons.app.api")

template_router = t = APIRouter()

# MongoDB Setup - use existing mongo_database instead of motor
person_db = mongo_database["Person"]
template_collection = mongo_database["templates"]
variable_collection = mongo_database["variables"]
sequence_collection = mongo_database["email_sequences"]
sequence_audit_collection = mongo_database["email_sequence_audits"]

# Helper function to convert MongoDB ObjectId to string
def to_dict(document):
    """Convert MongoDB document to a dictionary with stringified `_id`."""
    document["_id"] = str(document["_id"])
    return document

# Pydantic Models
# Update SequenceStep model to remove unsubscribe
class SequenceStep(BaseModel):
    sendingTime: str = Field(..., title="Sending Time")
    sender: str = Field(..., title="Sender")
    subject: str = Field(..., title="Subject")
    content: str = Field(..., title="Content")
    variables: List[str] = Field(..., title="Variables")
    aiCommands: List[str] = Field(..., title="AI Smart Commands")
    emailSignature: str = Field(..., title="Email Signature")
    days: Optional[int] = None  # Make these optional
    time: Optional[str] = None
    timezone: Optional[str] = None
    dayType: Optional[str] = None
    is_initial: bool = False  # Whether this is first email in thread
    thread_id: Optional[str] = None  # For tracking email thread
    # Remove unsubscribe field from step level

    @model_validator(mode='before')
    def validate_time_fields(cls, values):
        """Validate time-related fields based on sendingTime value."""
        if values.get('sendingTime') == 'immediate':
            values['days'] = None
            values['time'] = None
            values['timezone'] = None
            values['dayType'] = None
        return values

# Update Template model without unsubscribe field
class Template(BaseModel):
    id: PydanticObjectId | None = Field(default=None, alias="_id")
    name: str = Field(..., title="Template Name", max_length=100)
    steps: List[SequenceStep] = Field(..., title="Sequence Steps")
    cc: list[str] = Field(default_factory=list)
    bcc: list[str] = Field(default_factory=list)
    unsubscribe: bool = Field(default=False)  # Add unsubscribe at template level

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_schema_extra": {
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "name": "Example Template",
                "steps": [],
                "cc": [],
                "bcc": []
            }
        }
    }

# Update TemplateUpdate model as well
class TemplateUpdate(BaseModel):
    name: str | None = Field(None, title="Template Name", max_length=100)
    steps: List[SequenceStep] | None = Field(None, title="Sequence Steps")
    cc: Optional[List[str]] = Field(default_factory=list)
    bcc: Optional[List[str]] = Field(default_factory=list)
    unsubscribe: Optional[bool] = Field(default=None)  # Add unsubscribe flag

class Variable(BaseModel):
    _id: str
    name: str = Field(..., title="Variable Name", max_length=100)

class EmailScheduleRequest(BaseModel):
    profile_ids: List[str]
    template_id: str
    job_title: str
    tokenData: dict  # Add token data field

class EmailSequence(BaseModel):
    profile_id: str
    template_id: str
    public_identifier: str
    sequence_steps: List[dict]
    status: str = "PENDING"  # PENDING, IN_PROGRESS, COMPLETED, FAILED
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class EmailSequenceAudit(BaseModel):
    sequence_id: str
    step_index: int
    template_id: str
    profile_id: str
    public_identifier: str
    email_payload: dict
    scheduled_time: datetime
    status: str  # SCHEDULED, SENT, FAILED
    sent_time: Optional[datetime] = None  # Make it optional with None as default
    error_message: Optional[str] = None   # Make it optional with None as default
    created_at: datetime = Field(default_factory=datetime.utcnow)
    token_data: Optional[dict] = None  # Add this field to allow token data
    thread_id: Optional[str] = None
    is_initial: bool = False
    replied: bool = False
    unsubscribed: bool = False

    class Config:
        validate_assignment = True
        extra = 'forbid'

@t.get("/variables", response_model=List[Variable], summary="Fetch all predefined variables")
async def get_variables():
    variables = list(variable_collection.find())
    return [to_dict(variable) for variable in variables]

@t.post("/variables/", response_model=Variable, summary="Create a new predefined variable")
async def create_variable(variable: Variable):
    variable_dict = variable.dict()
    result = variable_collection.insert_one(variable_dict)
    if result.inserted_id:
        return to_dict({**variable_dict, "_id": result.inserted_id})
    raise HTTPException(status_code=500, detail="Failed to create variable")

@t.get("/sending-time-options", summary="Fetch sending time options")
async def get_sending_time_options():
    options = [
        {"label": "Immediate", "value": "immediate"},
        {"label": "Next Business Day", "value": "next_business_day"},
        {"label": "After", "value": "after"}
    ]
    return options

# Routes
@t.get("/", response_model=List[Template], summary="Fetch all templates")
async def get_templates():
    templates = list(template_collection.find())
    # Convert ObjectId to string for JSON serialization
    for template in templates:
        if "_id" in template:
            template["_id"] = str(template["_id"])
    return templates

@t.get("/{id}", response_model=Template, summary="Fetch a template by ID")
async def get_template_by_id(
    id: str = Path(..., title="Template ID", description="ID of the template to fetch")
):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid template ID")
    
    template = template_collection.find_one({"_id": ObjectId(id)})
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Ensure cc/bcc are included in response
    result = {
        **template,
        "cc": template.get("cc", []),  # Default to empty list if not present
        "bcc": template.get("bcc", [])  # Default to empty list if not present
    }
    
    return to_dict(result)

@t.post("/", response_model=Template, summary="Create a new template") 
async def create_template(template: Template):
    """Create template with template-level unsubscribe that propagates to steps."""
    template_dict = template.dict(exclude={"_id"})
    
    # Get unsubscribe from template level
    template_unsubscribe = template_dict.get('unsubscribe', False)
    
    # Ensure each step has the template's unsubscribe setting
    for step in template_dict['steps']:
        step['unsubscribe'] = template_unsubscribe
        
    # Keep other template fields
    if hasattr(template, 'cc'):
        template_dict['cc'] = template.cc
    if hasattr(template, 'bcc'):
        template_dict['bcc'] = template.bcc

    result = template_collection.insert_one(template_dict)
    if result.inserted_id:
        return to_dict({**template_dict, "_id": result.inserted_id})
    raise HTTPException(status_code=500, detail="Failed to create template")

@t.put("/{id}", response_model=Template)
async def edit_template(
    id: str = Path(..., title="Template ID"),
    update_data: TemplateUpdate = Body(...)
):
    """Update template with unsubscribe handling."""
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid template ID")
    
    try:
        update_dict = update_data.dict(exclude_none=True)
        update_dict["updated_at"] = datetime.utcnow()

        # Get the current template to preserve unsubscribe if not provided
        if update_dict.get('unsubscribe') is None:
            current_template = template_collection.find_one({"_id": ObjectId(id)})
            if current_template:
                update_dict['unsubscribe'] = current_template.get('unsubscribe', False)
        
        logger.info(f"Updating template {id} with data: {update_dict}")
        
        result = template_collection.find_one_and_update(
            {"_id": ObjectId(id)},
            {"$set": update_dict},
            return_document=True
        )
        
        if not result:
            raise HTTPException(status_code=404, detail="Template not found")
        
        return to_dict(result)
        
    except Exception as e:
        logger.error(f"Error updating template {id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@t.delete("/{id}", summary="Delete a template")
async def delete_template(
    id: str = Path(..., title="Template ID", description="ID of the template to delete")
):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid template ID")
    result = template_collection.delete_one({"_id": ObjectId(id)})
    if result.deleted_count:
        return {"message": "Template deleted successfully"}
    raise HTTPException(status_code=404, detail="Template not found")


def populate_template_content(content: str, profile: dict) -> str:
    # Replace variables in content with profile data
    # Add your variable replacement logic here
    return content

# Update the AI commands collection schema to be simpler
ai_commands_collection = mongo_database["ai_commands"]

@t.get("/ai-commands", response_model=List[dict])
async def get_ai_commands():
    """Fetch all predefined AI commands."""
    try:
        commands = list(ai_commands_collection.find({}, {"title": 1, "prompt": 1}))
        return [to_dict(cmd) for cmd in commands]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Remove create endpoint since we'll manage commands through backend only

@t.post("/preview/subject")
async def preview_subject(request: dict):
    """Preview processed subject line for a profile."""
    try:
        profile_id = request.get("profile_id")
        subject = request.get("subject", "")
        job_title = request.get("job_title")
        client_info = request.get("client_info", {})
        step_index = request.get("step_index", 0)
        sequence_id = request.get("sequence_id")

        if not profile_id:
            raise HTTPException(status_code=400, detail="Profile ID is required")

        # Get profile from database
        profile = person_db.find_one({"public_identifier": profile_id})
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")

        # For follow-up emails, try to get original subject from sequence
        if step_index > 0:
            try:
                if sequence_id:
                    sequence = sequence_collection.find_one({"_id": ObjectId(sequence_id)})
                    if sequence and sequence.get("original_subject"):
                        logger.info(f"Using original subject for follow-up: {sequence['original_subject']}")
                        return {"subject": sequence["original_subject"]}
                    else:
                        logger.info("No original subject found for follow-up, returning empty")
                        return {"subject": ""}
                else:
                    logger.info("No sequence ID provided for follow-up, returning empty")
                    return {"subject": ""}
            except Exception as e:
                logger.error(f"Error fetching sequence {sequence_id}: {str(e)}")
                return {"subject": ""}

        # For initial email
        try:
            # Add is_preview flag to client_info
            client_info['is_preview'] = True
            processed_subject = await populate_template_v2(subject, profile, job_title, client_info)
            return {"subject": processed_subject}
        except Exception as e:
            logger.error(f"Error processing subject template: {str(e)}", exc_info=True)
            return {"subject": ""}

    except Exception as e:
        logger.error(f"Error in preview_subject: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@t.post("/preview/content")
async def preview_content(request: dict):
    """Preview processed content for a profile."""
    try:
        profile_id = request.get("profile_id")
        content = request.get("content")
        job_title = request.get("job_title")
        client_info = request.get("client_info", {})

        if not all([profile_id, content]):
            raise HTTPException(status_code=400, detail="Missing required fields")

        # Get profile from database
        profile = person_db.find_one({"public_identifier": profile_id})
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")

        # Add is_preview flag to client_info
        client_info['is_preview'] = True

        # Process the content
        processed_content = await populate_template_v2(content, profile, job_title, client_info)

        return {"content": processed_content}

    except Exception as e:
        logger.error(f"Error processing content preview: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
