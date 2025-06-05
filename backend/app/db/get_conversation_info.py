from datetime import datetime
from app.models.conversation_model import Conversation
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient 
import asyncio
import os
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv
import base64
from bson.binary import Binary

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
        if "conversation_title" not in conversation_data or not conversation_data["conversation_title"]:
            conversation_data["conversation_title"] = f"Chat {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        print(f"Creating conversation with title: {conversation_data['conversation_title']}")
        
        result = await conversation_collection.insert_one(conversation_data)
        created_conversation = await conversation_collection.find_one({"_id": result.inserted_id})
        
        return Conversation(
            id=str(created_conversation["_id"]),
            user_id=created_conversation["user_id"],
            chosen_model=created_conversation["chosen_model"],
            chosen_prompts=created_conversation.get("chosen_prompts", []),
            conversation_title=created_conversation["conversation_title"],  # Keep the original title
            parameters=created_conversation.get("parameters", {}),
            messages=created_conversation.get("messages", []),
        )
    except Exception as e:
        print(f"Error in create_conversation_in_db: {str(e)}")
        raise RuntimeError(f"Error while creating conversation: {e}")


async def get_conversation_info(user_id: str):
    conversation_collection = await connect_to_mongo()
    print(f"Connected to MongoDB, fetching conversations for user: {user_id}")
    try:
        pipeline = [
            {"$match": {"user_id": user_id}},
            {"$project": {
                "_id": 1,
                "user_id": 1,
                "chosen_model": 1,
                "chosen_prompts": 1,
                "conversation_title": 1,
                "parameters": 1,
                "message_count": {"$size": {"$ifNull": ["$messages", []]}}
            }},
            {"$sort": {"_id": -1}}
        ]
        
        cursor = conversation_collection.aggregate(pipeline)
        conversations = []
        
        async for document in cursor:
            formatted_conversation = {
                "id": str(document["_id"]),
                "user_id": document["user_id"],
                "chosen_model": document["chosen_model"],
                "chosen_prompts": document.get("chosen_prompts", []),
                "conversation_title": document.get("conversation_title", f"Chat {len(conversations) + 1}"),
                "parameters": document.get("parameters", {}),
                "message_count": document.get("message_count", 0)
            }
            conversations.append(formatted_conversation)
            
        print(f"Total conversations found: {len(conversations)}")
        return conversations
    except Exception as e:
        print(f"Error while fetching conversation info: {e}")
        raise RuntimeError(f"Error while fetching conversation info: {e}")

async def update_conversation_in_db(conversation_id: str, update_data: dict):
    conversation_collection = await connect_to_mongo()
    print(f"Connected to MongoDB, updating conversation {conversation_id}")
    
    try:        
        result = await conversation_collection.update_one(
            {"_id": ObjectId(conversation_id)},  
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            print(f"No conversation found with ID: {conversation_id}")
            raise ValueError(f"Conversation with ID {conversation_id} not found")
        print(f"Updated conversation: {result.modified_count} document(s)")
    except Exception as e:
        print(f"Error in update_conversation_in_db: {str(e)}")
        raise RuntimeError(f"Error while updating conversation: {e}")
    
    
async def update_message_to_conversation(conversation_id: str, message: str, rol: str):
    print("final step")
    conversation_collection = await connect_to_mongo()
    print("Connected to MongoDB")
    try:
        new_message = {
            "role": rol,
            "content": message,
            "timestamp": datetime.now().isoformat()
        }
        print(new_message)
        
        filter = {"_id": ObjectId(conversation_id)} 

        result = await conversation_collection.update_one(
            filter,
            {"$push": {"messages": new_message}}
        )
        
        if result.matched_count == 0:
            print(f"No conversation found with ID: {conversation_id}")
        else:
            print(f"Updated conversation: {result.modified_count} document(s)")
    except Exception as e:
        print(f"Error in update_message_to_conversation: {str(e)}")
        raise RuntimeError(f"Error while adding message to conversation: {e}")
    
async def update_message_with_files_to_conversation(
    conversation_id: str, 
    message: str, 
    rol: str,
    files: List[Dict[str, Any]] = None
):
    print("Adding message with files to MongoDB")
    conversation_collection = await connect_to_mongo()
    print("Connected to MongoDB")
    
    try:
        new_message = {
            "role": rol,
            "content": message,
            "timestamp": datetime.now().isoformat(),
            "files": files or []
        }
        print(f"New message with {len(files) if files else 0} files")
        
        filter = {"_id": ObjectId(conversation_id)} 

        result = await conversation_collection.update_one(
            filter,
            {"$push": {"messages": new_message}}
        )
        
        if result.matched_count == 0:
            print(f"No conversation found with ID: {conversation_id}")
        else:
            print(f"Updated conversation with file data: {result.modified_count} document(s)")
    except Exception as e:
        print(f"Error in update_message_with_files_to_conversation: {str(e)}")
        raise RuntimeError(f"Error while adding message with files to conversation: {e}")



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
