from fastapi import HTTPException
from app.db.get_prompt_data import get_prompt_data
from app.services.send_request_to_ai_api import send_request_to_ai_api

async def process_prompt_request(prompt_ids: list, model_id: str, user_message: str, user_id: str, conversation_id: str):
    try:
        prompts_data = []
        for prompt_id in prompt_ids:
            prompt_data = await get_prompt_data(prompt_id)
            if not prompt_data:
                raise HTTPException(status_code=404, detail=f"Prompt ID {prompt_id} not found!")
            prompts_data.append(prompt_data)

        # Logowanie do debugowania
        print(f"Prompts data: {prompts_data}")
        print(f"Model ID: {model_id}, User Message: {user_message}, User ID: {user_id}, Conversation ID: {conversation_id}")

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