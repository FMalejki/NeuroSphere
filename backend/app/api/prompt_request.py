from fastapi import APIRouter, HTTPException, File
from app.models.prompt_request_model import PromptRequestModel
from app.services.prompt_service import process_prompt_request
from typing import List, Any
import json

router = APIRouter()

@router.post("/prompt-request", response_model=dict)
async def process_ai_request(request: dict):
    try:
        response = await process_prompt_request(
            prompt_ids=request["prompt_ids"],
            model_id=request["model_id"],
            user_message=request["user_message"],
            user_id=request["user_id"],
            conversation_id=request["conversation_id"],
            files = request["files"]
        )
        return {
            "status": "success",
            "response": response
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")