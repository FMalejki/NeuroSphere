from fastapi import APIRouter, HTTPException
from app.models.prompt_request_model import PromptRequestModel
from app.services.prompt_service import process_prompt_request
from app.db.get_prompt_data import get_user_prompts  # Import funkcji do pobierania promptów

router = APIRouter()

@router.post("/prompt-request", response_model=dict)
async def process_ai_request(request: PromptRequestModel):
    try:
        response = await process_prompt_request(
            prompt_ids=request.prompt_ids,
            model_id=request.model_id,
            user_message=request.user_message,
            user_id=request.user_id,
            conversation_id=request.conversation_id
        )
        return {
            "status": "success",
            "response": response
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("/get_user_prompts/{user_id}", response_model=list)
async def get_user_prompts_endpoint(user_id: str):
    try:
        prompts = await get_user_prompts(user_id)
        if not prompts:
            raise HTTPException(status_code=404, detail="No prompts found for this user")
        return prompts
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching prompts: {str(e)}")