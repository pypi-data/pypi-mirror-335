import stripe
import os
from datetime import datetime, timedelta
from bson import ObjectId
from fastapi import HTTPException
from talentwizer_commons.utils.db import mongo_database
import logging

logger = logging.getLogger("uvicorn")
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

def find_user_by_email(email: str):
    user = mongo_database["Users"].find_one({"email": email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def find_user_by_id(user_id: str):
    user = mongo_database["Users"].find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def calculate_end_date(start_date: datetime, frequency: str) -> datetime:
    if frequency == "monthly":
        return start_date + timedelta(days=30)
    elif frequency == "yearly":
        return start_date + timedelta(days=365)
    else:
        raise ValueError("Invalid frequency. Must be 'monthly' or 'yearly'.")
    
def calculate_prorate_amount(subscription):
    try:
        sample_subscription_item = {
                "id": subscription["items"]["data"][0]["id"],
                "plan": subscription["items"]["data"][0]["plan"]["id"],
                "quantity": 0,
            }

        upcoming_prorated_invoice = stripe.Invoice.upcoming(
            customer=subscription["customer"],
            subscription=subscription["id"],
            subscription_items=[sample_subscription_item],
        )

        # Calculate the prorated amount
        prorated_amount = 0
        for invoice_item in upcoming_prorated_invoice["lines"]["data"]:
            if invoice_item["type"] == "invoiceitem" and invoice_item["amount"] < 0:
                prorated_amount = abs(invoice_item["amount"])
                break

        # logger.info(f"Calculated prorated amount: {prorated_amount}")
        return prorated_amount
    except Exception as e:
        logging.error("Error While calculating Refund")
        raise HTTPException(status_code=400, detail=str(e))

def update_subscription_details(user, subscription):
    # Extract subscription details from the event data
    plan_id = subscription['items']['data'][0]['plan']['id']
    current_period_start = subscription['current_period_start']
    current_period_end = subscription['current_period_end']

    # Retrieve plan details from Stripe using product_id and plan_id
    plan = stripe.Plan.retrieve(plan_id, expand=['product'])

    # Extract plan type and frequency from the retrieved plan
    plan_type = plan['product']['name']
    frequency = plan['interval']

    # Convert timestamps to ISO format strings
    start_date = datetime.fromtimestamp(current_period_start).isoformat() + "Z"
    end_date = datetime.fromtimestamp(current_period_end).isoformat() + "Z"
    
    previous_subscription_id=user["stripe_subscription_id"]
    stripe.api_key=os.getenv("STRIPE_SECRET_KEY")
    
    try:
        previous_subscription = stripe.Subscription.retrieve(previous_subscription_id)
        prorated_amount=calculate_prorate_amount(previous_subscription)
        latest_invoice_id = previous_subscription["latest_invoice"]
        if latest_invoice_id:
            invoice = stripe.Invoice.retrieve(latest_invoice_id)
            # logger.info(invoice)
            # unused_amount = invoice["amount_due"] - invoice["amount_paid"]
            if prorated_amount > 0:
                # Create a refund for the unused amount
                stripe.Refund.create(
                    charge=invoice["charge"],
                    amount=prorated_amount,
                )
            logger.info(f"Refunded amount: {prorated_amount}")
            
        canceled_Subscription=stripe.Subscription.cancel(
            previous_subscription_id,
            prorate=False
            )
        logger.info(f"Canceled subscription: {previous_subscription_id}")

        # Update data to be set in MongoDB
        update_data = {
            "stripe_subscription_id": subscription['id'],
            "start_date": start_date,
            "end_date": end_date,
            "user_companies_count": 0,
            "user_jobs_count": 0,
            "plan": plan_type,  # Set plan type retrieved from Stripe
            "user_contacts_count": 0,
            "user_emails_count": 0,
            "updated_at": datetime.now()
        }

        # Update MongoDB with subscription details
        mongo_database["Users"].update_one(
            {"_id": user["_id"]},
            {"$set": update_data}
        )
        return start_date, end_date, plan_type, frequency
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # return start_date, end_date, plan_type, frequency
