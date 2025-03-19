from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel, EmailStr, Field  # Add Field to imports
from bson import ObjectId
from bson.json_util import dumps
import json
from typing import Optional
from datetime import datetime, timedelta
from urllib.parse import unquote

from talentwizer_commons.utils.db import mongo_database
from urllib.parse import unquote
from fastapi.responses import JSONResponse
# from fastapi_mail import FastMail, MessageSchema,ConnectionConfig
import smtplib
from dotenv import load_dotenv
import os
load_dotenv()
import traceback
import chargebee
import os

from datetime import datetime
from talentwizer_commons.utils.objectid import PydanticObjectId

# Create an instance of APIRouter to handle user-related routes
user_router = u = APIRouter()

class _UserCreateRequest(BaseModel):
    email: str
    plan: str

class _User(BaseModel):
    id: PydanticObjectId | None = Field(default=None, alias="_id")
    email: EmailStr
    plan: str
    end_date: datetime
    start_date: datetime
    user_companies_count: Optional[int] = None
    user_jobs_count: Optional[int] = None

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_schema_extra": {
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "email": "user@example.com",
                "plan": "basic",
                "end_date": "2024-12-31T00:00:00Z",
                "start_date": "2024-01-01T00:00:00Z"
            }
        }
    }

class _Contact(BaseModel):
    #The data of a candidate consisting of the candidate email and contact.
    # uid: Optional[str]
    email: str
    contact: Optional[str] = None

class SubscriptionRequest(BaseModel):
    user_id: str
    plan_type: str
    frequency: str

class RenewalRequest(BaseModel):
    user_id: str
    frequency: str

# Endpoint to check if a user exists
@u.get("/exists/{email}", response_model=_User)
async def check_user(email: str):
    """
    Check if a user exists.

    :param email: Email of the user to be checked.
    :type email: str
    :return: User data if the user exists.
    :rtype: dict
    """
    
    try:    
        # Check if user exists
        email=unquote(email)
        user_data = mongo_database["Users"].find_one({"email": email})
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user_data['id'] = str(user_data['_id'])
        # Handle start_date
        if 'start_date' in user_data:
            if isinstance(user_data['start_date'], dict):
                user_data['start_date'] = user_data['start_date']['$date']
            if isinstance(user_data['start_date'], datetime):
                user_data['start_date'] = user_data['start_date'].isoformat()

        # Handle end_date
        if 'end_date' in user_data:
            if isinstance(user_data['end_date'], dict):
                user_data['end_date'] = user_data['end_date']['$date']
            if isinstance(user_data['end_date'], datetime):
                user_data['end_date'] = user_data['end_date'].isoformat()

        
        user_model = _User(**user_data)
        return user_model
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e)) 
    
@u.post("/create/user")
async def create_user(user: _UserCreateRequest):
    user_data = mongo_database["Users"].find_one({"email": user.email})
    if user_data:
        return {"id": str(user_data["_id"])}

    user_data = user.dict()
    user_data.setdefault('user_companies_count', 0)
    user_data.setdefault('user_jobs_count', 0)
    user_data.setdefault('user_contacts_count', 0)
    user_data.setdefault('user_emails_count', 0)
    user_data.setdefault('user_can_send_emails', False)
    user_data.setdefault('created_at', datetime.now())
    user_data.setdefault('updated_at', datetime.now())
    user_data['start_date'] = datetime.now().isoformat() + "Z"
    user_data['end_date'] = (datetime.now() + timedelta(days=7)).isoformat() + "Z"  # Assuming free plan is monthly
    result = mongo_database["Users"].insert_one(user_data)

    # Create Stripe Customer
    API_KEY = os.getenv("CHARGEBEE_SECRET_KEY")
    SITE = os.getenv("CHARGEBEE_SITE")

    chargebee.configure("{API_KEY}","{SITE}")
    customer = chargebee.Customer.create(email=user.email)
    
    # Subscribe Customer to Free Plan
    # basic_plan=mongo_database["Plan"].find_one({"plan_type":"Basic"})
    # free_plan_id = os.getenv('STRIPE_FREE_PLAN_MONTHLY_ID')
    # free_plan_id=basic_plan["monthly_price_id"]
    # subscription = chargebee.Subscription.create_with_items(
    #     customer=customer.id,
    #     items=[{"plan": free_plan_id}]
    # )
    result = chargebee.Subscription.create_with_items(customer.id,{
        "subscription_items" : [
            {
                "item_price_id" : "FREE",
                "unit_price" : 100,
                "billing_cycles" : 1,
                "quantity" : 1
                
            }]
    })

    subscription = result.subscription
    customer = result.customer
    # Store the Stripe customer ID and subscription ID in MongoDB
    user_data['stripe_customer_id'] = customer.id
    user_data['stripe_subscription_id'] = subscription.id
    user_data['start_date'] = datetime.now().isoformat() + "Z"
    user_data['end_date'] = (datetime.now() + timedelta(days=7)).isoformat() + "Z"  # Assuming free plan is monthly
    
    mongo_database["Users"].update_one({"_id": result.inserted_id}, {"$set": user_data})

    return {"id": str(result.inserted_id)}

@u.get("/get-customer-id/{email}")
async def get_customer_id(email: str):
    user_data = mongo_database["Users"].find_one({"email": email})
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")

    stripe_customer_id = user_data.get("stripe_customer_id")
    if not stripe_customer_id:
        raise HTTPException(status_code=404, detail="Stripe customer ID not found")

    return {"stripe_customer_id": stripe_customer_id}

# Endpoint to create a new candidate
@u.post("/create/candidate")
async def create_candidate(
    data: _Contact,
):
    """
    Create a new candidate.

    :param data: Data of the candidate to be created.
    :type data: dict
    :return: ID of the created candidate.
    :rtype: dict
    """
    
    if data.email == "" or data.email == None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No candidate provided",
        )
    
    # check if user exists
    user_data = mongo_database["Candidate"].find_one({"email": data.email})
    if user_data:
        # raise HTTPException(
        #     status_code=status.HTTP_400_BAD_REQUEST,
        #     detail="Candidate already exists"
        # )
        return {"id": str(user_data["_id"])}

    response = mongo_database["Candidate"].insert_one(data.dict())

    return {"id": str(response.inserted_id)}


@u.get("/has_access")
async def has_access(email: str, entity_type: str):
    
    
    plan_collection = mongo_database["Plan"]
    user_collection = mongo_database["Users"]
    # Retrieve user's plan details
    user_plan = user_collection.find_one({"email": email})
    if user_plan is None:
        raise HTTPException(status_code=404, detail="User not found")

    plan = plan_collection.find_one({"plan_type": user_plan["plan"]})
    if plan is None:
        raise HTTPException(status_code=404, detail="Plan not found")

    # Retrieve entity count based on entity type
    # print(user_plan)
    entity_count = 0
    # print(entity_type.lower() )
    if entity_type.lower() == "company":
        entity_count = user_plan["user_companies_count"]
    elif entity_type.lower() == "job":
        entity_count = user_plan["user_jobs_count"]
    elif entity_type.lower() == "contact":
        entity_count = user_plan["user_contacts_count"]
    elif entity_type.lower() == "email":
        entity_count = user_plan["user_emails_count"]
    else:
        raise HTTPException(status_code=400, detail="Invalid entity type")
    
    # if (plan["max_companies_per_user"] == "Unlimited") and (plan["max_jobs"] == "Unlimited") and (plan["max_mobile_contacts_per_user"] == "Unlimited") and (plan["max_emails_per_user"] == "Unlimited"):
    #     return True
    if (plan["max_companies_per_user"] == "Unlimited" or plan["max_companies_per_user"] == -1) and \
        (plan["max_jobs"] == "Unlimited" or plan["max_jobs"] == -1) and \
        (plan["max_mobile_contacts_per_user"] == "Unlimited" or plan["max_mobile_contacts_per_user"] == -1) and \
        (plan["max_emails_per_user"] == "Unlimited" or plan["max_emails_per_user"] == -1):
        return True


    # Check if entity count exceeds the limit
    if entity_type.lower() == "company" and entity_count >= int(plan["max_companies_per_user"]):
        is_within_limit = False 
    elif entity_type.lower() == "job" and entity_count >= int(plan["max_jobs"]):
         is_within_limit = False
    elif entity_type.lower() == "contact" and entity_count >= int(plan["max_mobile_contacts_per_user"]):
        is_within_limit = False
    elif entity_type.lower() == "email" and entity_count >= int(plan["max_emails_per_user"]):
        is_within_limit = False
    else:
        is_within_limit = True

    return is_within_limit

@u.put("/increment/{entity_type}")
async def increment_entity_count(entity_type: str, email: str):

    users_collection = mongo_database["Users"]

    if entity_type.lower() not in ["contact", "email"]:
        raise HTTPException(status_code=400, detail="Invalid entity type")

    # Find the user document
    user = users_collection.find_one({"email": email})

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Increment the respective counter
    if entity_type.lower() == "contact":
        updated_count = user["user_contacts_count"] + 1
        users_collection.update_one({"email": email}, {"$set": {"user_contacts_count": updated_count,"updated_at": datetime.now()}})
    elif entity_type.lower() == "email":
        updated_count = user["user_emails_count"] + 1
        users_collection.update_one({"email": email}, {"$set": {"user_emails_count": updated_count,"updated_at": datetime.now()}})

    return {"message": "Counter incremented successfully"}
    
def calculate_end_date(start_date: datetime, frequency: str) -> datetime:
    if frequency == "monthly":
        return start_date + timedelta(days=30)
    elif frequency == "yearly":
        return start_date + timedelta(days=365)
    else:
        raise ValueError("Invalid frequency. Must be 'monthly' or 'yearly'.")

@u.post("/plan/subscribe")
async def create_user_plan(subscription: SubscriptionRequest):
    user_collection = mongo_database["Users"]
    user = user_collection.find_one({"_id": ObjectId(subscription.user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Ensure valid plan type and frequency
    valid_plan_types = ["free", "starter", "premium", "enterprise"]
    if subscription.plan_type not in valid_plan_types:
        raise HTTPException(status_code=400, detail="Invalid plan type")
    
    valid_frequencies = ["monthly", "yearly"]
    if subscription.frequency not in valid_frequencies:
        raise HTTPException(status_code=400, detail="Invalid frequency")

    start_date = datetime.now()
    end_date = calculate_end_date(start_date, subscription.frequency)

    # Update the user document with the subscription details
    user_collection.update_one(
        {"_id": ObjectId(subscription.user_id)},
        {"$set": {
            "plan": subscription.plan_type,
            "start_date": start_date.isoformat() + "Z",
            "end_date": end_date.isoformat() + "Z",
            "updated_at": datetime.now()
        }}
    )

    return {
        "plan": subscription.plan_type,
        "start_date": start_date.isoformat() + "Z",
        "end_date": end_date.isoformat() + "Z"
    }


@u.post("/plan/renewal")
async def renew_plan(renewal: RenewalRequest):
    users_collection = mongo_database["Users"]
    user = users_collection.find_one({"_id": ObjectId(renewal.user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    current_end_date_str = user.get("end_date")
    if not current_end_date_str:
        raise HTTPException(status_code=400, detail="User does not have an active plan")

    try:
        current_end_date = datetime.fromisoformat(current_end_date_str.rstrip("Z"))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid end date format")

    # Calculate the new end date based on the frequency
    new_end_date = calculate_end_date(current_end_date, renewal.frequency)

    # Reset the counters and update the end date
    users_collection.update_one(
        {"_id": ObjectId(renewal.user_id)},
        {"$set": {
            "start_date": current_end_date,
            "end_date": new_end_date.isoformat() + "Z",
            "user_companies_count": 0,
            "user_jobs_count": 0,
            "user_contacts_count": 0,
            "user_emails_count": 0,
            "updated_at": datetime.now()
        }}
    )

    return {
        "user_id": renewal.user_id,
        "new_end_date": new_end_date.isoformat() + "Z"
    }

@u.post("/send/email")
async def send_Email(req:Request):
 
    response= await req.json()
    data=response["data"] 
    subject = response["subject"]

    support_email=os.environ["SUPPORT_EMAIL"]
    support_password=os.environ["SUPPORT_PASSWORD"]
    
    emails=response["email"]
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login(support_email,support_password )
    message = data
    
    for dest in emails:
        dest=unquote(dest)
        message = f"Subject: {subject}\n\n{data}"
        s.sendmail(support_email, dest, message.encode('utf-8'))
  
    s.quit()
    
    return JSONResponse(status_code=200, content={"Detail":"Email Sent Successfully"})

