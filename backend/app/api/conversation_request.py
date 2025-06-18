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
    Retrieves a complete conversation by ID, including all messages with their text content and files.
    
    Args:
        conversation_id (str): The ID of the conversation to retrieve
        
    Returns:
        dict: The complete conversation data with messages
        
    Raises:
        ValueError: If conversation is not found
        RuntimeError: If there's a database error
    """
    conversation_collection = await connect_to_mongo()
    try:
        # Convert to ObjectId for MongoDB query
        oid = ObjectId(conversation_id)
        conversation = await conversation_collection.find_one({"_id": oid})
        
        if not conversation:
            raise ValueError(f"Conversation with ID {conversation_id} not found")
        
        # Format the conversation data for the frontend
        formatted_conversation = {
            "id": str(conversation["_id"]),
            "user_id": conversation.get("user_id", ""),
            "chosen_model": conversation.get("chosen_model", ""),
            "chosen_prompts": conversation.get("chosen_prompts", []),
            "conversation_title": conversation.get("conversation_title", "Untitled"),
            "parameters": conversation.get("parameters", {}),
            "messages": []
        }
        
        # Process all messages, ensuring both text content and files are included
        for msg in conversation.get("messages", []):
            message_data = {
                "role": msg.get("role", "unknown"),
                "content": msg.get("content", ""),  # Ensure text content is included
                "timestamp": msg.get("timestamp", datetime.now().isoformat())
            }
            
            # Add files if present
            if "files" in msg and msg["files"]:
                # Convert binary data back to base64 for frontend display
                processed_files = []
                for file in msg["files"]:
                    if "data" in file and isinstance(file["data"], bytes):
                        # Convert binary data to base64 string
                        file_data = base64.b64encode(file["data"]).decode('utf-8')
                    else:
                        file_data = file.get("data", "")
                    
                    processed_files.append({
                        "name": file.get("name", "unknown"),
                        "type": file.get("type", "application/octet-stream"),
                        "size": file.get("size", 0),
                        "data": file_data
                    })
                message_data["files"] = processed_files
            
            formatted_conversation["messages"].append(message_data)
        
        logger.info(f"Retrieved conversation {conversation_id} with {len(formatted_conversation['messages'])} messages")
        return formatted_conversation
        
    except Exception as e:
        logger.error(f"Error retrieving conversation {conversation_id}: {str(e)}")
        raise RuntimeError(f"Error retrieving conversation: {e}") from e
    