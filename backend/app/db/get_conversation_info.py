from datetime import datetime
from app.models.conversation_model import Conversation
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient 
import asyncio
import os
from typing import List, Optional
from dotenv import load_dotenv

load_dotenv()  

MONGO_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("MONGO_DB_NAME", "neurosphere")
COLLECTION_NAME = "conversations"

async def connect_to_mongo():
    try:
        client = AsyncIOMotorClient(MONGO_URI)
        db = client[DB_NAME]
        conversation_collection = db[COLLECTION_NAME]
        return conversation_collection
    except Exception as e:
        raise RuntimeError(f"Failed to connect to MongoDB: {e}")


async def create_conversation_in_db(conversation_data: dict) -> Conversation:
    conversation_collection = await connect_to_mongo()
    try:
        # Add a default title if not provided
        if "conversation_title" not in conversation_data:
            conversation_data["conversation_title"] = f"Chat {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        result = await conversation_collection.insert_one(conversation_data)
        created_conversation = await conversation_collection.find_one({"_id": result.inserted_id})
        
        return Conversation(
            id=str(created_conversation["_id"]),
            user_id=created_conversation["user_id"],
            chosen_model=created_conversation["chosen_model"],
            chosen_prompts=created_conversation["chosen_prompts"],
            conversation_title=created_conversation.get("conversation_title", "New Chat"),
            parameters=created_conversation["parameters"],
            messages=[],
        )
    except Exception as e:
        raise RuntimeError(f"Error while creating conversation: {e}")


async def get_conversation_info(user_id: str):
    conversation_collection = await connect_to_mongo()
    print("Connected to MongoDB")
    try:
        cursor = conversation_collection.find({"user_id": user_id})
        conversations = []
        async for document in cursor:
            # Format each document to match what the frontend expects
            formatted_conversation = {
                "id": str(document["_id"]),
                "user_id": document["user_id"],
                "chosen_model": document["chosen_model"],
                "chosen_prompts": document["chosen_prompts"],
                # Set a default title if not present
                "conversation_title": document.get("conversation_title", "Chat " + str(len(conversations) + 1)),
                "parameters": document.get("parameters", {}),
                "messages": document.get("messages", [])
            }
            conversations.append(formatted_conversation)
            print(f"Formatted conversation: {formatted_conversation}")

        if not conversations:
            print(f"No conversations found for user ID: {user_id}")
            return []  # Return empty array instead of raising error
        
        return conversations
    except Exception as e:
        print(f"Error while fetching conversation info: {e}")
        raise RuntimeError(f"Error while fetching conversation info: {e}")
    

async def update_conversation_in_db(conversation_id: str, update_data: dict):
    conversation_collection = await connect_to_mongo()
    print("Connected to MongoDB")
    
    #"""
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
    print("final step")
    conversation_collection = await connect_to_mongo()
    print("Connected to MongoDB")
    try:
        # Create a new message object
        new_message = {
            "role": rol,
            "content": message,
            "timestamp": datetime.now().isoformat()  # Dodanie znacznika czasu
        }
        print(new_message)
        filter = {"_id": ObjectId(conversation_id)} 

        # Use $push to add the new message to the messages list
        await conversation_collection.update_one(
            filter,
            {"$push": {"messages": new_message}}
        )
        print("updated")
    except Exception as e:
        raise RuntimeError(f"Error while adding message to conversation: {e}")
    
    



#async def list_conversations_from_db(user_id: str):
#    conversations = []
#    async for conversation in conversation_collection.find({"user_id": user_id}):
#        conversations.append(Conversation(
#            id=str(conversation["_id"]),
#            user_id=conversation["user_id"],
#            chosen_model=conversation["chosen_model"],
#            chosen_prompts=conversation["chosen_prompts"],
#            parameters=conversation["parameters"],
#            messages=conversation["messages"],
#        ))
#    return conversations
    
    
    
#if not ObjectId.is_valid(conversation_id):
#    print("Invalid ObjectId format")
#    return
#
#conversation = await conversation_collection.find_one({"_id": ObjectId(conversation_id)})
#if not conversation:
#    print("Conversation not found")
#    return
#
#print("\n Conversation Info:")
#print(f"ID: {conversation['_id']}")
#print(f"User ID: {conversation.get('user_id')}")
#print(f"Chosen Model: {conversation.get('chosen_model')}")
#print(f"Chosen Prompts: {conversation.get('chosen_prompts')}")
#print(f"Parameters: {conversation.get('parameters')}")
#print("Messages:")
#for msg in conversation.get("messages", []):
#    print(f" - [{msg['role']}] {msg['content']}")

#if __name__ == "__main__":
#    conv_id = input("Enter the conversation ID: ").strip()
#    asyncio.run(get_conversation_info(conv_id))
