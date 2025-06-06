"""
Endpoints for chat module 
"""
import base64
from datetime import datetime
import logging

from fastapi import APIRouter, HTTPException
from bson import ObjectId
from bson.binary import Binary

from app.models.conversation_model import Conversation
from app.db.get_conversation_info import create_conversation_in_db, get_conversation_info
from app.db.get_conversation_info import connect_to_mongo


router = APIRouter()

logger = logging.getLogger("app")

@router.post("/conversations/", response_model=Conversation)
async def create_conversation(conv_data: dict):
    """
    Creates conversation in the database with the data provided from frontend.
    If no title is provided, it generates a default title based on the chosen model and date.
    """
    try:
        logger.info("Creating new conversation with data: %s", conv_data)
        title = conv_data.get('conversation_title',
        f"{conv_data['chosen_model']} Chat - {datetime.now().strftime('%b %d, %Y')}")    
        conv_dict = {
            "user_id": conv_data['user_id'],
            "chosen_model": conv_data['chosen_model'],
            "chosen_prompts": conv_data['chosen_prompts'],
            "parameters": conv_data.get('parameters', {}),
            "messages": [],
            "conversation_title": title
        }
        conv_final = await create_conversation_in_db(conv_dict)
        return conv_final
    except HTTPException as e:
        raise e
    except (TypeError, ValueError) as e:
        raise HTTPException(status_code=500, detail=f'Error: {str(e)}') from e

@router.get("/conversations/{user_id}")
async def get_conversation(user_id: str):
    """
    Retrieves conversations for a given user ID.
    If no conversations are found, it returns an empty list instead of a 404 error.
    """
    got_conversations = await get_conversation_info(user_id)
    if not got_conversations:
        return []  # Return empty list instead of 404
    print("Got conversations:", got_conversations)
    return got_conversations

@router.get("/conversation/{conversation_id}")
async def get_single_conversation(conversation_id: str):
    """
    Retrieves a single conversation by its ID.
    Load messages and photos from the database, and encode file data to base64 if necessary.
    """
    try:
        conversation_collection = await connect_to_mongo()
        if not ObjectId.is_valid(conversation_id):
            raise HTTPException(status_code=400, detail="Invalid conversation ID")
        document = await conversation_collection.find_one({"_id": ObjectId(conversation_id)})
        if not document:
            raise HTTPException(status_code=404, detail="Conversation not found")
        messages = document.get("messages", [])
        for message in messages:
            if "files" in message and message["files"]:
                for file in message["files"]:
                    if "data" in file and file["data"]:
                        if isinstance(file['data'], (Binary, bytes)):
                            try:
                                file["data"] = base64.b64encode(file["data"]).decode('utf-8')
                            except (TypeError, ValueError) as e:
                                print(f"Failed to encode file data: {e}")
                                file["data"] = None
        formatted_conversation = {
            "id": str(document["_id"]),
            "user_id": document["user_id"],
            "chosen_model": document["chosen_model"],
            "chosen_prompts": document.get("chosen_prompts", []),
            "conversation_title": document.get("conversation_title", "Chat"),
            "parameters": document.get("parameters", {}),
            "messages": messages
        }
        return formatted_conversation
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}") from e
    