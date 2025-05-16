import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from typing import Dict, Any, Optional
from app.models.prompt_model import PromptModel
from pymongo import MongoClient

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")

try:
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[MONGO_DB_NAME]
except Exception as e:
    raise RuntimeError(f"Failed to connect to MongoDB: {e}")

client = MongoClient(MONGO_URI)
db = client[MONGO_DB_NAME]

async def get_prompt_data(prompt_id: str) -> Optional[Dict[str, Any]]:
    try:
        collection = db["products"]
        
        query = {"_id": ObjectId(prompt_id)} if ObjectId.is_valid(prompt_id) else {"_id": prompt_id}
        
        prompt_data = await collection.find_one(query)
        if not prompt_data:
            return None

        return PromptModel(
            id=str(prompt_data["_id"]),
            text=prompt_data.get("prompt_text", ""),
        )

    except Exception as e:
        raise RuntimeError(f"Error while fetching prompt data: {e}")

async def get_user_prompts(user_id: str):
    try:
        prompts = list(db.prompts.find({"user_id": user_id}))
        return prompts
    except Exception as e:
        print(f"Error fetching prompts for user {user_id}: {e}")
        return []