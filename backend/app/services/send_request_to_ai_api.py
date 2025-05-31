from typing import Dict, List, Any
import asyncio
import os

from app.models.prompt_model import PromptModel
from app.services.openai_service import (
    send_to_openai, 
    send_to_gemini, 
    send_to_hugging_face,
    send_to_openai_with_images,
    send_to_gemini_with_images
)
from app.services.user_conversation_message_adder import add_message_to_conversation
from app.handlers.file_handlers import handle_image, handle_text, handle_zip, handle_default

async def send_request_to_ai_api(
    prompts_data: List[PromptModel],
    model_info: str,
    user_message: str,
    user_id: str,
    conversation_id: str,
    files: List[Dict[str, Any]] = None
) -> Dict[str, Any]:
    try:
        print("inside send_request_to_ai_api")

        # Structure that will store our request
        content = [{"type": "text", "text": user_message}]

        # Flag to track if we have images
        has_images = False
        
        # Including files in the request. If files are provided.
        if files:
            print(f"Processing {len(files)} files")
            for f in files:
                try:
                    # Get info from file dictionary
                    info = f.get("info", {})
                    file_type = info.get("type", "")
                    print(f"Processing file of type: {file_type}")
                    
                    # Process based on file type
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
                    print(f"Error processing file: {str(e)}")

        # Create the full text prompt
        full_prompt = "\n\n".join([prompt.text for prompt in prompts_data]) + f"\n\n{user_message}"
        print(f"Full prompt: {full_prompt}")
        
        # Add user message to conversation
        asyncio.create_task(add_message_to_conversation(conversation_id, user_message, "user"))
        
        # Route to appropriate AI service based on model and content
        if model_info == "openai":
            if has_images:
                print("Sending to OpenAI with images")
                response = send_to_openai_with_images(content, conversation_id, user_id)
            else:
                response = send_to_openai(full_prompt, conversation_id, user_id)
                
        elif model_info == "gemini":
            if has_images:
                print("Sending to Gemini with images")
                response = send_to_gemini_with_images(content, full_prompt, conversation_id, user_id)
            else:
                response = send_to_gemini(full_prompt, conversation_id, user_id)
                
        elif model_info == "huggingface":
            # Huggingface doesn't support images in the same way
            response = send_to_hugging_face(full_prompt, conversation_id, user_id)
            
        else:
            raise ValueError(f"Invalid API choice: {model_info}")

        # Return the response
        return {
            "response": response,
        }

    except Exception as e:
        print(f"Error in send_request_to_ai_api: {str(e)}")
        raise Exception(f"Error while processing request with {model_info}: {str(e)}")