# stripe_webhook.py

from fastapi import APIRouter, HTTPException, Request
import stripe
import os
from talentwizer_commons.utils.db import mongo_database
from talentwizer_commons.utils.subscription_management import update_subscription_details

webhook_router = APIRouter()
endpoint_secret = os.getenv('STRIPE_WEBHOOK_SECRET')

@webhook_router.post("/")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except (ValueError, stripe.error.SignatureVerificationError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    try:
        if event['type'] == 'customer.subscription.updated':
            handle_subscription_event(event['data']['object'])
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 
    
    return {"status": "success"}

def handle_subscription_event(subscription):
    stripe_customer_id = subscription['customer']
    user = mongo_database["Users"].find_one({"stripe_customer_id": stripe_customer_id})
    if user:
        update_subscription_details(user, subscription)
