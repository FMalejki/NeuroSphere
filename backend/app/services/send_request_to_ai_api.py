import asyncio
from typing import Dict, List, Any

from app.models.prompt_model import PromptModel
from app.services.openai_service import build_payload, parse_response
from app.services.user_conversation_message_adder import add_message_to_conversation
from app.services.openai_service import send_to_openai, send_to_gemini, send_to_hugging_face
from app.handlers.file_handlers import handle_image, handle_text, handle_zip, handle_default

#TODO: Refactor this so it works with photos and files
async def send_request_to_ai_api(
    prompts_data: List[PromptModel],
    model_info: str,
    user_message: str,
    user_id: str,
    conversation_id: str,
    files: List[Any] = None
) -> Dict[str, Any]:
    try:
        print("inside send_request_to_ai_api")

        # Structure that will store our request
        content = [{"type": "text", "text": user_message}]

        # Including files in the request. If files are provided.
        if files:
            for f in files:
                try:
                    if hasattr(f, 'info') and hasattr(f.info, 'type'):
                        if f.info.type.startswith("image/"):
                            handle_image(f, content)
                        elif f.info.type == "text/plain":
                            handle_text(f, content)
                        elif f.info.type == "application/pdf":
                            handle_pdf(f, content)
                        elif f.info.type == "application/zip":
                            handle_zip(f, content)
                        else:
                            handle_default(f, content)
                    else:
                        print(f"Warning: File object missing required attributes: {f}")
                except Exception as e:
                    print(f"Error processing file: {str(e)}")

        full_prompt = "\n\n".join([prompt.text for prompt in prompts_data]) + f"\n\n{user_message}"

        # Adding the content to the full prompt
        if len(content) == 1 and content[0]['type'] == 'text':
            full_prompt += f"\n\n{content[0]['text']}"

        asyncio.create_task(add_message_to_conversation(conversation_id, user_message, "user"))
        # Wybierz odpowiednie API na podstawie api_choice
        if model_info == "openai":
            #response = send_to_openai(full_prompt)
            response = send_to_gemini(full_prompt, conversation_id, user_id)
        elif model_info == "gemini":
            response = send_to_gemini(full_prompt, conversation_id, user_id)
        elif model_info == "huggingface":
            #response = send_to_hugging_face(full_prompt)
            response = send_to_gemini(full_prompt, conversation_id, user_id)
        else:
            raise ValueError(f"Invalid API choice: {model_info}. Please choose 'openai', 'gemini', or 'huggingface'.")

        # Zwróć odpowiedź
        return {
            "response": response,
        }

    except Exception as e:
        raise Exception(f"Error while processing request with {model_info}: {str(e)}")