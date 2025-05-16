from fastapi import APIRouter, HTTPException
from typing import List
from bson import ObjectId
from app.models.conversation_model import Conversation, ConversationCreate
from app.db.get_conversation_info import create_conversation_in_db, get_conversation_info, list_conversations_from_db
from app.services.openai_service import parse_response

router = APIRouter()

@router.post("/conversations/", response_model=Conversation)
async def create_conversation(conv_data: ConversationCreate):
    try:
        conv_dict = {
            "user_id": conv_data.user_id,
            "chosen_model": conv_data.chosen_model,
            "chosen_prompts": conv_data.chosen_prompts,
            "parameters": conv_data.parameters
        }
        new_conversation = await create_conversation_in_db(conv_dict)
        return new_conversation
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating conversation: {str(e)}")

@router.get("/conversations/user/{user_id}", response_model=List[Conversation])
async def get_user_conversations(user_id: str):
    try:
        conversations = await list_conversations_from_db(user_id)
        if not conversations:
            raise HTTPException(status_code=404, detail="No conversations found for this user")
        return conversations
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching conversations: {str(e)}")

@router.get("/conversations/detail/{conversation_id}", response_model=Conversation)
async def get_conversation(conversation_id: str):
    try:
        if not ObjectId.is_valid(conversation_id):
            raise HTTPException(status_code=400, detail="Invalid conversation ID")
        conversation = await get_conversation_info(conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        return conversation
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching conversation: {str(e)}")



