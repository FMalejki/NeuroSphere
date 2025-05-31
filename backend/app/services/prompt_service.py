from fastapi import HTTPException
from app.db.get_prompt_data import get_prompt_data
from app.db.get_model_api_info import get_model_api_info
from app.services.send_request_to_ai_api import send_request_to_ai_api

async def process_prompt_request(prompt_ids: list, model_id: str, user_message: str, user_id: str, conversation_id: str, files=None):
    print(f"Processing prompt request: user_id={user_id}, conversation_id={conversation_id}")
    print(f"Prompt IDs: {prompt_ids}")
    print(f"Model ID: {model_id}")
    
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")
    if not conversation_id:
        raise HTTPException(status_code=400, detail="conversation_id is required")
    
    prompts_data = []
    for prompt_id in prompt_ids:
        prompt_data = await get_prompt_data(prompt_id)
        print(f"Retrieved prompt data: {prompt_data}")
        if not prompt_data:
            raise HTTPException(status_code=404, detail=f"Prompt ID {prompt_id} not found!")
        prompts_data.append(prompt_data)
    
    try:
        response = await send_request_to_ai_api(
            prompts_data=prompts_data,
            model_info=model_id,
            user_message=user_message,
            user_id=user_id,
            conversation_id=conversation_id,
            files=files
        )
        return response
    except Exception as e:
        print(f"Error in send_request_to_ai_api: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process request: {str(e)}")