"""
Service module for processing prompt requests and sending them to AI API.
This module handles the retrieval of prompt data and manages API communication.
"""
import logging

from fastapi import HTTPException
from app.db.get_prompt_data import get_prompt_data
from app.services.send_request_to_ai_api import send_request_to_ai_api
from app.models.prompt_request_model import PromptRequestModel

logger = logging.getLogger("app")

async def process_prompt_request(
    prompt_ids: list,
    model_id: str,
    user_message: str,
    user_id: str,
    conversation_id: str,
    files=None
):
    """
    Process a prompt request with the given parameters.
    
    Args:
        prompt_ids: List of prompt identifiers to process
        model_id: ID of the AI model to use
        user_message: Message from the user
        user_id: User identifier
        conversation_id: Conversation identifier
        files: Optional files attached to the request
        
    Returns:
        The response from the AI API
        
    Raises:
        HTTPException: If any required parameters are missing or processing fails
    """
    logger.info("Processing prompt request: user_id=%s, conversation_id=%s", user_id, conversation_id)
    logger.debug("Prompt IDs: %s", prompt_ids)
    logger.debug("Model ID: %s", model_id)
    
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")
    if not conversation_id:
        raise HTTPException(status_code=400, detail="conversation_id is required")
    
    try:
        prompt_request = PromptRequestModel(
            prompt_ids=prompt_ids,
            model_id=model_id,
            user_message=user_message,
            user_id=user_id,
            conversation_id=conversation_id,
            files=files
        )
    except ValueError as e:
        logger.error("Error creating PromptRequestModel: %s", str(e))
        raise HTTPException(status_code=400, detail=f"Invalid request parameters: {str(e)}")
    
    prompts_data = []
    for prompt_id in prompt_ids:
        prompt_data = await get_prompt_data(prompt_id)
        logger.debug("Retrieved prompt data: %s", prompt_data)
        if not prompt_data:
            raise HTTPException(status_code=404, detail=f"Prompt ID {prompt_id} not found!")
        prompts_data.append(prompt_data)
    
    try:
        response = await send_request_to_ai_api(
            prompt_request=prompt_request,
            prompts_data=prompts_data
        )
        return response
    except Exception as e:
        logger.error("Error in send_request_to_ai_api: %s", str(e))
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to process request: {str(e)}"
        ) from e