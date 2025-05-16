from fastapi import HTTPException
from app.db.get_prompt_data import get_prompt_data
from app.services.send_request_to_ai_api import send_request_to_ai_api

async def process_prompt_request(prompt_ids: list, model_id: str, user_message: str, user_id: str, conversation_id: str):
    try:
        prompts_data = [await get_prompt_data(prompt_id) for prompt_id in prompt_ids]
        if not all(prompts_data):
            raise HTTPException(status_code=404, detail="One or more prompts not found!")

        response = await send_request_to_ai_api(
            prompts_data=prompts_data,
            model_info=model_id,
            user_message=user_message,
            user_id=user_id,
            conversation_id=conversation_id
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing prompt request: {str(e)}")