from app.models.conversation_model import Conversation
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient 
import asyncio
import os
from typing import List, Optional
from dotenv import load_dotenv

load_dotenv()  

MONGO_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("MONGO_DB_NAME", "ai_models_db")
COLLECTION_NAME = "conversations"

try:
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[DB_NAME]
    conversation_collection = db[COLLECTION_NAME]
except Exception as e:
    raise RuntimeError(f"Failed to connect to MongoDB: {e}")

async def create_conversation_in_db(conversation_data: dict) -> Conversation:
    try:
        #result = await conversation_collection.insert_one(conversation_data)
        #await conversation_collection.find_one({"_id": result.inserted_id})
        result = await conversation_collection.insert_one(conversation_data)
        created_conversation = await conversation_collection.find_one({"_id": result.inserted_id})
        return Conversation(
            id=str(created_conversation["_id"]),
            user_id=created_conversation["user_id"],
            chosen_model=created_conversation["chosen_model"],
            chosen_prompts=created_conversation["chosen_prompts"],
            #conversation_title=created_conversation["conversation_title"], #do stworzenia
            conversation_title="Default_Titl", #Placeholder
            parameters=created_conversation["parameters"],
            messages=[],
        )
    except Exception as e:
        raise RuntimeError(f"Error while creating conversation: {e}")


async def get_conversation_info(user_id: str):
    try:
        conversation = await conversation_collection.find_one({"_id": ObjectId(user_id)})
        if not conversation:
            raise ValueError("Conversation not found")
        
        return Conversation(
            id=str(conversation["_id"]),
            user_id=conversation["user_id"],
            chosen_model=conversation["chosen_model"],
            chosen_prompts=conversation["chosen_prompts"],
            conversation_title=conversation["conversation_title"], # stworzenia
            parameters=conversation["parameters"],
            messages=conversation["messages"],
        )
    except Exception as e:
        raise RuntimeError(f"Error while fetching conversation info: {e}")
    

async def update_conversation_in_db(conversation_id: str, update_data: dict):
   #"""
   #Updates a conversation in the MongoDB database.
   #
   #Args:
   #    conversation_id (str): The ID of the conversation to update.
   #    update_data (dict): The data to update. Can include one or more fields.
   #
   #Returns:
   #    dict: The updated conversation object.
   #"""
    try:        
        result = await conversation_collection.update_one(
            {"_id": str(conversation_id)},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise ValueError(f"Conversation with ID {conversation_id} not found")
    except Exception as e:
        raise RuntimeError(f"Error while updating conversation: {e}")
    
    
async def update_message_to_conversation(conversation_id: str, message: str, rol: str):
    """
    Adds a message to the conversation with the given ID.
    """
    try:
        # Create a new message object
        new_message = {
            "role": rol,
            "content": message
        }

        # Use $push to add the new message to the messages list
        await conversation_collection.update_one(
            conversation_id,
            {"$push": {"messages": new_message}}
        )
    except Exception as e:
        raise RuntimeError(f"Error while adding message to conversation: {e}")
    

async def list_conversations_from_db(user_id: str):
    """
    Pobiera listę konwersacji dla danego użytkownika z bazy danych.
    """
    try:
        conversations = []
        async for conversation in conversation_collection.find({"user_id": user_id}):
            conversations.append(Conversation(
                id=str(conversation["_id"]),
                user_id=conversation["user_id"],
                chosen_model=conversation["chosen_model"],
                chosen_prompts=conversation["chosen_prompts"],
                parameters=conversation["parameters"],
                messages=conversation.get("messages", []),
            ))
        return conversations
    except Exception as e:
        raise RuntimeError(f"Error while listing conversations for user {user_id}: {e}")
