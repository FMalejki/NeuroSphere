"""
Module for sending user requests to various AI models and handling responses.
"""
from typing import Dict, List, Any
import logging

from app.models.prompt_model import PromptModel
from app.services.openai_service import (
    send_to_openai,
    send_to_gemini,
    send_to_openai_with_images,
    send_to_gemini_with_images
)
from app.services.user_conversation_message_adder import (
    add_message_with_files_to_conversation,
    add_message_to_conversation
)
from app.handlers.file_handlers import handle_image, handle_text, handle_zip, handle_default

logger = logging.getLogger("app")

async def send_request_to_ai_api(
    prompts_data: List[PromptModel],
    model_info: str,
    user_message: str,
    user_id: str,
    conversation_id: str,
    files: List[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Send user's request to the selected AI API with any attached files.

    Args:
        prompts_data: List of prompt models containing system instructions
        model_info: The AI model to use (openai, gemini, etc.)
        user_message: The user's message text
        user_id: The ID of the user
        conversation_id: The ID of the conversation
        files: Optional list of file dictionaries

    Returns:
        Dictionary containing the AI's response

    Raises:
        ValueError: If an invalid model is specified
        Exception: If there's an error processing the request
    """
    try:
        logger.debug("Inside send_request_to_ai_api")

        content = [{"type": "text", "text": user_message}]

        has_images = False
        file_count = 0
        
        if files:
            logger.debug("Processing %d files", len(files))
            await add_message_with_files_to_conversation(
                conversation_id=conversation_id,
                message=user_message if user_message else "Image uploaded",
                rol="user",
                files=files
            )
            for f in files:
                try:
                    file_count += 1
                    info = f.get("info", {})
                    file_type = info.get("type", "")
                    file_name = info.get("name", f"file-{file_count}")
                    logger.debug(
                        "Processing file %s of type: %s", file_name, file_type
                    )
                    
                    if file_type.startswith("image/"):
                        handle_image(f, content)
                        has_images = True
                    elif file_type == "text/plain":
                        handle_text(f, content)
                    elif file_type == "application/zip":
                        handle_zip(f, content)
                    else:
                        handle_default(f, content)
                except Exception as e:
                    logger.error("Error processing file: %s", str(e))
        else:
            add_message_to_conversation(
                conversation_id=conversation_id,
                message=user_message if user_message else "Image uploaded",
                rol="user",
            )

        full_prompt = "\n\n".join([prompt.text for prompt in prompts_data]) + f"\n\n{user_message}"
        logger.debug("Full prompt: %s", full_prompt)
        
        response = None
        if model_info == "openai":
            if has_images or file_count > 0:
                logger.debug(
                    "Sending to OpenAI with %d files (including %s images)", file_count, has_images
                )
                response = send_to_openai_with_images(content, conversation_id, user_id)
            else:
                response = send_to_openai(full_prompt, conversation_id, user_id)
        elif model_info == "gemini":
            if has_images or file_count > 0:
                logger.debug(
                    "Sending to Gemini with %d files (including %s images)", file_count, has_images
                )
                response = send_to_gemini_with_images(content, full_prompt, conversation_id, user_id)
            else:
                response = send_to_gemini(full_prompt, conversation_id, user_id)
        elif model_info == "huggingface":
            # Currently not implemented
            raise ValueError("Hugging Face integration not yet implemented")
        else:
            raise ValueError(f"Invalid API choice: {model_info}")

        return {
            "response": response,
        }

    except Exception as e:
        logger.error("Error in send_request_to_ai_api: %s", str(e))
        raise Exception(f"Error while processing request with {model_info}: {str(e)}") from e