from fastapi import APIRouter, HTTPException, Request
from app.services.prompt_service import process_prompt_request
import json

router = APIRouter()

@router.post("/prompt-request", response_model=dict)
async def process_ai_request(request: Request):
    try:
        request_data = await request.json()
        print(f"Received request data: {request_data}")
        
        required_fields = ["prompt_ids", "model_id", "user_message", "user_id", "conversation_id"]
        for field in required_fields:
            if field not in request_data:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        files = request_data.get("files", None)
        
        response = await process_prompt_request(
            prompt_ids=request_data["prompt_ids"],
            model_id=request_data["model_id"],
            user_message=request_data["user_message"],
            user_id=request_data["user_id"],
            conversation_id=request_data["conversation_id"],
            files=files
        )
        return {
            "status": "success",
            "response": response
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error in process_ai_request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")