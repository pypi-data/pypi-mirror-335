from fastapi import FastAPI, HTTPException, APIRouter, Depends,Request
from pydantic import BaseModel
import stripe
import os
import logging
from talentwizer_commons.utils.db import mongo_database

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Stripe with your secret key
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# Initialize FastAPI and MongoDB client
app = FastAPI()

stripe_session_router = APIRouter()

class CheckoutSessionRequest(BaseModel):
    price_id: str
    email: str

@stripe_session_router.post("/create-checkout-session")
async def create_checkout_session(request: Request):
    logger.info("Received request to create checkout session")
    # logger.info(f"Request data: {request}")
    data=await request.json()
    # print(data)
    email=data['email']
    price_id=data['price_id']
    

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
        checkout_session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=["card"],
            line_items=[
                {
                    "price": price_id,
                    "quantity": 1,
                },
            ],
            mode="subscription",
            success_url=success_url,
            cancel_url=cancel_url,
        )
        logger.info(f"Created checkout session: {checkout_session['id']}")
        return {"id": checkout_session["id"]}
    
    except Exception as e:
        logger.error(f"Error creating checkout session: {e}")
        raise HTTPException(status_code=500, detail="Error creating checkout session")
