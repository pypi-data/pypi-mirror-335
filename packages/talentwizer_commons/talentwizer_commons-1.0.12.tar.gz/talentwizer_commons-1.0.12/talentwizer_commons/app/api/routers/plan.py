from fastapi import APIRouter, HTTPException, Body
from talentwizer_commons.utils.db import mongo_database
from typing import List
import stripe
import os

from datetime import datetime
from app.models import PlanData, PlanUpdater

# Create an instance of APIRouter to handle plan-related routes
plan_router = APIRouter()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

@plan_router.post("/")
async def create_plan(plan_data: PlanData):
    # Instantiate PlanUpdater with connection details
    updater = PlanUpdater(mongo_database, "Plan")

    plan_data_dict = plan_data.dict()
    plan_data_dict["created_at"] = datetime.now()
    plan_data_dict["updated_at"] = datetime.now()
    
    # Create the product in Stripe
    # stripe_product = stripe.Product.create(
    #     name=plan_data.plan_type,
    #     description=plan_data.description,
    #     metadata={
    #         "max_companies_per_user": plan_data.max_companies_per_user,
    #         "max_jobs": plan_data.max_jobs,
    #         "max_resumes_per_job": plan_data.max_resumes_per_job,
    #         "max_searches_per_job": plan_data.max_searches_per_job,
    #         "max_total_search": plan_data.max_total_search,
    #         "max_emails_per_user": plan_data.max_emails_per_user,
    #         "max_mobile_contacts_per_user": plan_data.max_mobile_contacts_per_user
    #     }
    # )

    # Create the monthly price in Stripe
    # monthly_price = stripe.Price.create(
    #     unit_amount=plan_data.monthly_price,
    #     currency="usd",
    #     recurring={"interval": "month"},
    #     product=stripe_product.id
    # )

    # Create the yearly price in Stripe
    # yearly_price = stripe.Price.create(
    #     unit_amount=plan_data.yearly_price,
    #     currency="usd",
    #     recurring={"interval": "year"},
    #     product=stripe_product.id
    # )
    
    # plan_data_dict["monthly_price_id"]= monthly_price.id
    # plan_data_dict["yearly_price_id"]= yearly_price.id
        
    plan_id = updater.create_plan(plan_data_dict)

    return {
        "plan_id": plan_id,
        # "stripe_product_id": stripe_product.id,
        # "monthly_price_id": monthly_price.id,
        # "yearly_price_id": yearly_price.id,
        "message": "Plan created successfully"
    }

@plan_router.put("/{plan_id}")
async def update_plan(plan_id: str, plan_data: PlanData):
    # Instantiate PlanUpdater with connection details
    updater = PlanUpdater(mongo_database, "Plan")

    # Construct updates dictionary with provided parameters
    updates = plan_data.dict(exclude_unset=True)
    updates["updated_at"] = datetime.now()

    # Update the plan details in MongoDB
    updater.update_plan(plan_id, updates)

    # Fetch the current plan details from MongoDB
    current_plan = updater.collection.find_one({"plan_id": plan_id})

    if not current_plan or "stripe_product_id" not in current_plan:
        raise HTTPException(status_code=404, detail="Plan not found or Stripe product ID missing")

    # Update the product in Stripe
    stripe.Product.modify(
        current_plan["stripe_product_id"],
        name=plan_data.plan_type,
        description=plan_data.description,
        metadata={
            "max_companies_per_user": plan_data.max_companies_per_user,
            "max_jobs": plan_data.max_jobs,
            "max_resumes_per_job": plan_data.max_resumes_per_job,
            "max_searches_per_job": plan_data.max_searches_per_job,
            "max_total_search": plan_data.max_total_search,
            "max_emails_per_user": plan_data.max_emails_per_user,
            "max_mobile_contacts_per_user": plan_data.max_mobile_contacts_per_user
        }
    )

    return {"message": "Plan details updated successfully"}

# New endpoint to get all plans
@plan_router.get("/")
async def get_plans():
    updater = PlanUpdater(mongo_database, "Plan")
    plans = updater.get_plans()
    if not plans:
        raise HTTPException(status_code=404, detail="No plans found")
    return plans
