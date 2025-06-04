from fastapi import APIRouter, HTTPException
from typing import List
from bson import ObjectId
from datetime import datetime

from app.models.conversation_model import Conversation, ConversationCreate, Message
from app.db.get_conversation_info import create_conversation_in_db, get_conversation_info
from app.services.openai_service import parse_response
from app.db.get_conversation_info import connect_to_mongo
from bson.binary import Binary
import base64

router = APIRouter()

@router.post("/conversations/", response_model=Conversation)
async def create_conversation(conv_data: dict):
    try:
        print(conv_data)
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")



@router.get("/conversations/{user_id}")
async def get_conversation(user_id: str):
    print("User ID:", user_id)
    got_conversations = await get_conversation_info(user_id)
    if not got_conversations:
        return []  # Return empty list instead of 404
    print("Got conversations:", got_conversations)
    return got_conversations

@router.get("/conversation/{conversation_id}")
async def get_single_conversation(conversation_id: str):
    try:
        conversation_collection = await connect_to_mongo()
        
        if not ObjectId.is_valid(conversation_id):
            raise HTTPException(status_code=400, detail="Invalid conversation ID")
            
        document = await conversation_collection.find_one({"_id": ObjectId(conversation_id)})
        
        if not document:
            raise HTTPException(status_code=404, detail="Conversation not found")
            
        # Process messages to convert binary data to base64 for files
        messages = document.get("messages", [])
        for message in messages:
            if "files" in message and message["files"]:
                for file in message["files"]:
                    if "data" in file and file["data"]:
                        if isinstance(file["data"], Binary) or isinstance(file["data"], bytes):
                            try:
                                file["data"] = base64.b64encode(file["data"]).decode('utf-8')
                            except Exception as e:
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
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")



#return await get_conversation_info(conversation_id) ## do wyje 
# if not ObjectId.is_valid(conversation_id):
#    raise HTTPException(status_code=400, detail="Invalid conversation ID")





#from fastapi import APIRouter, HTTPException
#from typing import List
#from bson import ObjectId
#
#from app.models.conversation_model import ConversationCreate, Conversation, ConversationBase
#from app.db.get_conversation_info import conversation_collection  
#
#router = APIRouter()
#
#@router.post("/conversations/", response_model=ConversationBase)
#async def create_conversation(conv_data: ConversationCreate):
#    conv_dict = conv_data#.dict()
#    result = await conversation_collection.insert_one(conv_dict)
#    saved = await conversation_collection.find_one({"_id": result.inserted_id})
#    return Conversation(**saved)
#
#@router.get("/conversations/{conversation_id}", response_model=Conversation)
#async def get_conversation(conversation_id: str):
#    if not ObjectId.is_valid(conversation_id):
#        raise HTTPException(status_code=400, detail="Invalid conversation ID")
#
#    conversation = await conversation_collection.find_one({"_id": ObjectId(conversation_id)})
#    if not conversation:
#        raise HTTPException(status_code=404, detail="Conversation not found")
#
#    return Conversation(**conversation)
#
#@router.get("/conversations/user/{user_id}", response_model=List[Conversation])
#async def get_user_conversations(user_id: int):
#    cursor = conversation_collection.find({"user_id": user_id})
#    conversations = [Conversation(**doc) async for doc in cursor]
#    return conversations



