"""
Endpoint for prompts
"""
import logging

from fastapi import APIRouter, HTTPException, Request
from app.services.prompt_service import process_prompt_request

router = APIRouter()

logger = logging.getLogger("app")

@router.post("/prompt-request", response_model=dict)
async def process_ai_request(request: Request):
    """
    Endpoint for prompt processing
    """
    try:
        request_data = await request.json()
        user_id = request_data.get("user_id", "unknown")
        conversation_id = request_data.get("conversation_id", "unknown")
        logger.info("Received prompt request from user_id: %s, conversation_id: %s",
                    user_id, conversation_id)
        required_fields = ["prompt_ids", "model_id", "user_message", "user_id", "conversation_id"]
        for field in required_fields:
            if field not in request_data:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        files = request_data.get("files", None)
        generate_image = request_data.get("generate_image", False) # Extract generate_image flag

        response = await process_prompt_request(
            prompt_ids=request_data["prompt_ids"],
            model_id=request_data["model_id"],
            user_message=request_data["user_message"],
            user_id=request_data["user_id"],
            conversation_id=request_data["conversation_id"],
            files=files,
            generate_image=generate_image # Pass generate_image flag
        )
        logger.info("Succesfully processed prompt for user_id: %s", user_id)
        return {
            "status": "success",
            "response": response
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error in process_ai_request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}") from e