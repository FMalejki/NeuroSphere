"""
Seller information management module.

This module provides functionality to interact with seller data in the MongoDB database.
It includes functions to create, retrieve, update, and delete seller information,
along with associated product relationships.

The module handles seller data including names, descriptions, and product listings,
converting between MongoDB document format and the application's Seller model.
"""
import os
from typing import List, Optional

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

from app.models.seller_model import Seller

load_dotenv()

MONGO_URI = os.getenv("MONGODB_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")

try:
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[MONGO_DB_NAME]
    sellers_collection = db["sellers"]
except Exception as e:
    raise RuntimeError(f"Failed to connect to MongoDB: {e}") from e

async def create_seller_in_db(seller_data: dict) -> Seller:
    """
    Creates seller in the database
    """
    result = await sellers_collection.insert_one(seller_data)
    created_seller = await sellers_collection.find_one({"_id": result.inserted_id})
    return Seller(
        id=str(created_seller["_id"]),
        name=created_seller["name"],
        description=created_seller["description"],
        products=created_seller["products"],
        opinions=created_seller["opinions"],
        public_key=created_seller["public_key"],
    )

async def list_sellers_from_db() -> List[Seller]:
    """
    Gets list of sellers from database
    """
    sellers = []
    async for seller in sellers_collection.find():
        sellers.append(Seller(
            id=str(seller["_id"]),
            name=seller["name"],
            description=seller["description"],
            products=seller["products"],
            opinions=seller["opinions"],
            public_key=seller["public_key"],
        ))
    return sellers

async def get_seller_from_db(seller_id: str) -> Optional[Seller]:
    """
    Get singular seller from the database
    """
    seller = await sellers_collection.find_one({"_id": str(seller_id)})
    if not seller:
        return None
    return Seller(
        id=str(seller["_id"]),
        name=seller["name"],
        description=seller["description"],
        products=seller["products"],
        opinions=seller["opinions"],
        public_key=seller["public_key"],
    )
async def get_seller_public_key_db(seller_id: str) -> Optional[str]:
    """
    Nie mam pojęcia 
    """
    seller = await sellers_collection.find_one({"_id": str(seller_id)})
    if not seller:
        return None
    return seller["public_key"]
