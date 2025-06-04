import os
import base64
from dotenv import load_dotenv
from app.models.conversation_model import Conversation, Message
from app.db.get_conversation_info import get_conversation_info, update_conversation_in_db, update_message_to_conversation, update_message_with_files_to_conversation
from typing import List, Dict, Any, Optional
from bson import ObjectId
from bson.binary import Binary


async def add_message_to_conversation(conversation_id: str, message: str, rol: str):
    #Adds a message to the conversation with the given ID.
    try:
        print("before next step")
        await update_message_to_conversation(conversation_id, message, rol)
    except Exception as e:
        raise RuntimeError(f"Error while adding message to conversation: {e}")

async def add_message_with_files_to_conversation(
    conversation_id: str, 
    message: str, 
    rol: str,
    files: Optional[List[Dict[str, Any]]] = None
):
    """
    Adds a message with file data to the conversation with the given ID.
    Converts base64 data to binary format using BSON Binary type before storing.
    """
    try:
        print("Adding message with files to conversation")
        
        file_objects = []

        if files and len(files) > 0:
            for file in files:
                if "info" in file and "data" in file:
                    file_info = file["info"]
                    
                    if isinstance(file["data"], str):
                        data_str = file["data"]
                        if "," in data_str:
                            data_str = data_str.split(",", 1)[1]
                        
                        # Convert base64 to binary and wrap with BSON Binary type
                        binary_data = Binary(base64.b64decode(data_str))
                    else:
                        # If it's already binary, wrap it with BSON Binary type
                        binary_data = Binary(file["data"])
                    
                    file_objects.append({
                        "name": file_info.get("name", "unnamed_file"),
                        "type": file_info.get("type", "application/octet-stream"),
                        "size": file_info.get("size", 0),
                        "data": binary_data  # Using BSON Binary type
                    })
        
        await update_message_with_files_to_conversation(
            conversation_id, 
            message,
            rol, 
            file_objects
        )
    except Exception as e:
        print(f"Error processing files: {str(e)}")
        raise RuntimeError(f"Error while adding message with files to conversation: {e}")

#def add_message_to_conversation(conversation_id: str, message: str, rol: str):#->Conversation
#    #"""
#    #Adds a message to the conversation with the given ID.
#    #"""
#    try:
#        # Fetch
#        #conversation = get_conversation_info(conversation_id)
#        #if not conversation:
#        #    raise ValueError("Conversation not found")
#        
#        # Add new message
#        M = Message(rol,message)
#        #conversation.messages.append(M)
#        
#        update_conversation_in_db(conversation_id, {"messages": conversation.messages})
#        #return conversation
#    except Exception as e:
#        raise RuntimeError(f"Error while adding message to conversation: {e}")
