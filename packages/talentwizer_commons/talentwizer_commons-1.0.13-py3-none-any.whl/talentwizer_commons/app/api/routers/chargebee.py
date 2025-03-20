from fastapi import FastAPI, HTTPException, APIRouter, Depends,Request
from pydantic import BaseModel
import chargebee
import os
import logging
from talentwizer_commons.utils.db import mongo_database

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Stripe with your secret key
API_KEY = os.getenv("CHARGEBEE_SECRET_KEY")
SITE = os.getenv("CHARGEBEE_SITE")

chargebee.configure("{API_KEY}","{SITE}")
# Initialize FastAPI and MongoDB client
app = FastAPI()

chargebee_session_router = csr = APIRouter()

class CheckoutSessionRequest(BaseModel):
    price_id: str
    email: str
    quantity: int
    unit_price: int

@csr.post("/create-checkout-session")
async def create_checkout_session(request: CheckoutSessionRequest):
    logger.info("Received request to create checkout session")
    # logger.info(f"Request data: {request}")
    data=await request.json()
    # print(data)
    email=data['email']
    price_id=data['price_id']
    quantity=data['quantity']
    unit_price=data['unit_price']
    
    # Fetch the customer ID from MongoDB
    try:
        user_data = mongo_database["Users"].find_one({"email": email})
        if not user_data:
            logger.error(f"User with email {email} not found")
            raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        logger.error(f"Error fetching user data: {e}")
        raise HTTPException(status_code=500, detail="Error fetching user data")

    customer_id = user_data.get("stripe_customer_id")

    logger.info(f"Fetched customer ID: {customer_id}")
    success_url=os.getenv("PAYMENT_SUCCESS_URL")
    cancel_url=os.getenv("PAYMENT_CANCEL_URL")
    # Create a Stripe Checkout Session
    try:
       
        checkout_session = chargebee.HostedPage.checkout_existing_for_items({
            "subscription" : {"id" : customer_id},
            "subscription_items" : [
                {
                    "item_price_id" : price_id,
                    "quantity" : quantity,
                    "unit_price" : unit_price
                }]
            })
        
        hosted_page = checkout_session.hosted_page
        logger.info(f"Created checkout session: {hosted_page['id']}")
        return {"id": checkout_session["id"]}
    
    except Exception as e:
        logger.error(f"Error creating checkout session: {e}")
        raise HTTPException(status_code=500, detail="Error creating checkout session")
