from fastapi import HTTPException
from models.user import UserLogin
from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")

try:
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB_NAME]
    users_collection = db["users"]
except Exception as e:
    raise RuntimeError(f"Failed to connect to MongoDB: {e}")

def authenticate_user(login_data: UserLogin):
    # Check if the identifier is an email or username
    if "@" in login_data.identifier:  # If the identifier contains '@', treat it as an email
        user = users_collection.find_one({"email": login_data.identifier})
    else:  # Otherwise, treat it as a username
        user = users_collection.find_one({"username": login_data.identifier})

    # If user not found or password doesn't match
    if not user or user["password"] != login_data.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {"message": "Login successful", "user": user}
