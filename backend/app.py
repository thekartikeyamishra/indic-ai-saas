from fastapi import FastAPI
from transformers import EncoderDecoderModel, PreTrainedTokenizerFast
import torch
import razorpay
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import stripe
from fastapi import Depends
import psycopg2
from dotenv import load_dotenv
from twilio.rest import Client
from fastapi import Form

load_dotenv()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# Initialize FastAPI App
app = FastAPI()

# Load Pre-trained Indic Tokenizer and Model
tokenizer = PreTrainedTokenizerFast.from_pretrained("indic_encoder_decoder")
model = EncoderDecoderModel.from_pretrained("indic_encoder_decoder")

# Twilio Credentials (Replace with real ones)
TWILIO_SID = "your_twilio_sid"
TWILIO_AUTH = "your_twilio_auth_token"
TWILIO_WHATSAPP_NUMBER = "whatsapp:+14155238886"

client = Client(TWILIO_SID, TWILIO_AUTH)

# Connect to PostgreSQL
conn = psycopg2.connect(
    database="your_db",
    user="your_user",
    password="your_password",
    host="your_host",
    port="5432"
)

# Database Connection
conn = psycopg2.connect(
    database="your_db",
    user="your_user",
    password="your_password",
    host="your_host",
    port="5432"
)

app = FastAPI()

# Data Model
class UserData(BaseModel):
    user_id: str
    feature_used: str
    input_text: str
    output_text: str
    additional_info: dict = {}

@app.post("/collect_data")
async def collect_data(data: UserData):
    """Stores anonymized user-generated text and interactions"""
    cursor = conn.cursor()
    query = """
        INSERT INTO user_data (user_id, feature_used, input_text, output_text, additional_info)
        VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(query, (data.user_id, data.feature_used, data.input_text, data.output_text, json.dumps(data.additional_info)))
    conn.commit()
    return {"message": "Data collected successfully"}

@app.post("/purchase_credits")
async def purchase_credits(email: str, amount: int):
    """Creates a Stripe Payment Intent & Adds Credits to User"""
    intent = stripe.PaymentIntent.create(
        amount=amount * 100, currency="INR",
        payment_method_types=["card"]
    )

    cursor = conn.cursor()
    cursor.execute("UPDATE users SET credits = credits + %s WHERE email = %s", (amount, email))
    conn.commit()

    return {"client_secret": intent["client_secret"]}

@app.post("/send_whatsapp")
async def send_whatsapp_message(phone: str = Form(...), message: str = Form(...)):
    """Sends WhatsApp Message via Twilio"""
    try:
        msg = client.messages.create(
            from_=TWILIO_WHATSAPP_NUMBER,
            body=message,
            to=f"whatsapp:{phone}"
        )
        return {"message_id": msg.sid}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


razorpay_client = razorpay.Client(auth=(os.getenv("RAZORPAY_KEY"), os.getenv("RAZORPAY_SECRET")))

class PaymentRequest(BaseModel):
    amount: int  # in INR
    currency: str = "INR"
    email: str

@app.post("/create_order")
async def create_order(payment: PaymentRequest):
    """Creates a Razorpay order for subscription or API purchase"""
    order = razorpay_client.order.create({
        "amount": payment.amount * 100,  # Convert to paisa
        "currency": payment.currency,
        "payment_capture": 1
    })
    return {"order_id": order["id"], "email": payment.email}

@app.post("/generate")
async def generate_text(input_text: str):
    """Generate AI-powered text from Indian language input."""
    inputs = tokenizer(input_text, return_tensors="pt", padding=True, truncation=True)
    outputs = model.generate(inputs["input_ids"], max_length=250)
    decoded_output = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return {"generated_text": decoded_output}

@app.get("/get_users")
async def get_users():
    """Fetch all users from the database"""
    cursor = conn.cursor()
    cursor.execute("SELECT id, email, credits FROM users")
    users = [{"id": row[0], "email": row[1], "credits": row[2]} for row in cursor.fetchall()]
    return users

@app.post("/generate")
async def generate_text(user_id: str, input_text: str):
    """Generates AI-powered text and stores data for AI training"""
    inputs = tokenizer(input_text, return_tensors="pt", padding=True, truncation=True)
    outputs = model.generate(inputs["input_ids"], max_length=250)
    generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # Store Data
    await collect_data(UserData(
        user_id=user_id,
        feature_used="Text Generation",
        input_text=input_text,
        output_text=generated_text
    ))

    return {"generated_text": generated_text}

@app.post("/send_whatsapp")
async def send_whatsapp_message(user_id: str, phone: str, message: str):
    """Handles WhatsApp Chatbot Interactions"""
    bot_response = "This is an AI-generated response."  # Placeholder AI Response

    # Store Data
    await collect_data(UserData(
        user_id=user_id,
        feature_used="WhatsApp Chatbot",
        input_text=message,
        output_text=bot_response
    ))

    return {"message_id": "12345", "bot_response": bot_response}

# Run with: uvicorn app:app --reload
