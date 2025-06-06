"""
Module for handling message additions to user conversations.
Provides functionality to add text messages and messages with file attachments.
"""
import base64
import logging

from typing import List, Dict, Any, Optional

from app.db.get_conversation_info import update_message_to_conversation, update_message_with_files_to_conversation

logger = logging.getLogger("app")

async def add_message_to_conversation(conversation_id: str, message: str, rol: str):
    """
    Adds a text message to the conversation with the given ID.
    
    Args:
        conversation_id: The ID of the conversation
        message: The message text content
        rol: The role of the message sender
        
    Raises:
        RuntimeError: If there's an error adding the message
    """
    try:
        logger.debug("Processing message addition to conversation")
        await update_message_to_conversation(conversation_id, message, rol)
    except Exception as e:
        raise RuntimeError(f"Error while adding message to conversation: {e}") from e


async def add_message_with_files_to_conversation(
    conversation_id: str,
    message: str,
    rol: str,
    files: Optional[List[Dict[str, Any]]] = None
):
    """
    Adds a message with file data to the conversation with the given ID.
    Converts base64 data to binary before storing.
    
    Args:
        conversation_id: The ID of the conversation
        message: The message text content
        rol: The role of the message sender
        files: List of file objects containing metadata and content
        
    Raises:
        RuntimeError: If there's an error processing files or adding the message
    """
    try:
        logger.debug("Adding message with files to conversation")
        
        file_objects = []

        if files and len(files) > 0:
            for file in files:
                if "info" in file and "data" in file:
                    file_info = file["info"]
                    
                    if isinstance(file["data"], str):
                        data_str = file["data"]
                        if "," in data_str:
                            data_str = data_str.split(",", 1)[1]
                        
                        binary_data = base64.b64decode(data_str)
                    else:
                        binary_data = file["data"]
                    
                    file_objects.append({
                        "name": file_info.get("name", "unnamed_file"),
                        "type": file_info.get("type", "application/octet-stream"),
                        "size": file_info.get("size", 0),
                        "data": binary_data
                    })
        
        await update_message_with_files_to_conversation(
            conversation_id,
            message,
            rol,
            file_objects
        )
    except Exception as e:
        logger.error("Error processing files: %s", str(e))
        raise RuntimeError(f"Error while adding message with files to conversation: {e}") from e
