"""
Prompt data retrieval module.

This module provides functionality to fetch prompt data from the MongoDB database.
It queries the 'products' collection to retrieve prompt templates, descriptions,
and associated metadata based on the provided prompt ID.

The module handles both MongoDB ObjectId and string identifier formats for lookup
and returns structured prompt information for use in generating AI responses.
"""
import os
from typing import Dict, Any, Optional

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

from app.models.prompt_model import PromptModel

load_dotenv()

MONGO_URI = os.getenv("MONGODB_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")

try:
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[MONGO_DB_NAME]
except Exception as e:
    raise RuntimeError(f"Failed to connect to MongoDB: {e}") from e

async def get_prompt_data(prompt_id: str) -> Optional[Dict[str, Any]]:
    """
    Gets prompt data from MongoDB
    """
    try:
        collection = db["products"]
        query = {"_id": ObjectId(prompt_id)} if ObjectId.is_valid(prompt_id) else {"_id": prompt_id}
        prompt_data = await collection.find_one(query)
        if not prompt_data:
            return None

        return PromptModel(
            id=str(prompt_data["_id"]),
            text=str(prompt_data["promptText"]),
        )

    except Exception as e:
        raise RuntimeError(f"Error while fetching prompt data: {e}") from e
    