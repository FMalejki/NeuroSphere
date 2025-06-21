import os
import logging
import time
import openai
import base64
from dotenv import load_dotenv

from google import genai
from google.genai import types
from app.models.prompt_request_model import PromptRequestModel
from app.services.user_conversation_message_adder import add_message_with_files_to_conversation
from app.models.response_model import (
    AIResponse, AIResponseItem, ResponseStatus, 
    ResponseSource, ResponseMetadata
)
from app.services.openai_service import create_error_response, add_message_safely

load_dotenv()

logger = logging.getLogger("app")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


class ImageGenerationService:
    """
    Service for generating images using various AI models.
    """
    async def generate_image(self, prompt_request: PromptRequestModel) -> dict:
        """
        Generates an image based on the user's request and selected model.

        Args:
            prompt_request: The request model containing prompt, user, and conversation info.

        Returns:
            A dictionary containing the AI's response.
        """
        model_id = prompt_request.model_id
        logger.debug(f"Image generation requested for model: {model_id}")

        if model_id == "gemini":
            return await self._generate_with_gemini(prompt_request)
        elif model_id == "openai":
            return await self._generate_with_openai(prompt_request)
        else:
            error_msg = f"Image generation is not supported for model: {model_id}"
            return create_error_response(
                ResponseSource.UNKNOWN,
                error_msg,
                prompt_request.conversation_id,
                prompt_request.user_id
            ).to_external_format()

    async def _generate_with_gemini(self, prompt_request: PromptRequestModel) -> dict:
        """
        Generates an image using Google's Gemini model with Imagen 3.
        """
        try:
            start_time = time.time()
            prompt = prompt_request.user_message
            logger.info(f"Generating image with Gemini Imagen for prompt: '{prompt}'")

            client = genai.Client(api_key=GEMINI_API_KEY)
            
            config = types.GenerateImagesConfig(
                number_of_images=1,
                aspect_ratio="1:1",  # Valid options: "1:1", "3:4", "4:3", "9:16", "16:9"
                safety_filter_level="BLOCK_LOW_AND_ABOVE",  # Valid options per docs
                person_generation="ALLOW_ADULT"  # Valid options: "DONT_ALLOW", "ALLOW_ADULT"
            )
            
            response = client.models.generate_images(
                model='imagen-3.0-generate-002',
                prompt=prompt,
                config=config
            )
            
            if not response.generated_images:
                error_message = "Gemini API did not return any generated images."
                logger.error(error_message)
                await add_message_safely(prompt_request.conversation_id, error_message, "error")
                return create_error_response(
                    ResponseSource.GEMINI, error_message,
                    prompt_request.conversation_id, prompt_request.user_id
                ).to_external_format()
            
            # Get the first generated image
            generated_image = response.generated_images[0]
            image_bytes = generated_image.image.image_bytes
            
            if not image_bytes:
                error_message = "Gemini API did not return image data for the given prompt."
                logger.error(error_message)
                await add_message_safely(prompt_request.conversation_id, error_message, "error")
                return create_error_response(
                    ResponseSource.GEMINI, error_message,
                    prompt_request.conversation_id, prompt_request.user_id
                ).to_external_format()
            
            # Convert image bytes to base64
            b64_string = base64.b64encode(image_bytes).decode('utf-8')
            image_url_for_response = f"data:image/png;base64,{b64_string}"
            processing_time = (time.time() - start_time) * 1000
            
            text_content = f"Image generated from prompt: '{prompt}'"
            
            generated_file = {
                "data": b64_string,
                "info": {"type": "image/png", "name": f"generated_image_{int(time.time())}.png"}
            }
            
            await add_message_with_files_to_conversation(
                conversation_id=prompt_request.conversation_id,
                message=text_content,
                rol="assistant",
                files=[generated_file]
            )
            
            ai_response = AIResponse(
                status=ResponseStatus.SUCCESS,
                source=ResponseSource.GEMINI,
                items=[AIResponseItem(content_type="image_url", content=image_url_for_response, role="assistant")],
                metadata=ResponseMetadata(
                    model_name="imagen-3.0-generate-002",
                    processing_time_ms=processing_time,
                    raw_response={"text": text_content, "number_of_images": len(response.generated_images)}
                ),
                conversation_id=prompt_request.conversation_id,
                user_id=prompt_request.user_id
            )
            return ai_response.to_external_format()
            
        except Exception as e:
            error_message = f"Failed to generate image with Gemini: {str(e)}"
            logger.error(error_message, exc_info=True)
            await add_message_safely(prompt_request.conversation_id, error_message, "error")
            return create_error_response(
                ResponseSource.GEMINI, error_message,
                prompt_request.conversation_id, prompt_request.user_id
            ).to_external_format()

    async def _generate_with_openai(self, prompt_request: PromptRequestModel) -> dict:
        """
        Generates an image using OpenAI's DALL-E 3 model.
        """
        try:
            start_time = time.time()
            client = openai.OpenAI(api_key=OPENAI_API_KEY)
            logger.info(f"Generating image with DALL-E 3 for prompt: '{prompt_request.user_message}'")

            response = client.images.generate(
                model="dall-e-3",
                prompt=prompt_request.user_message,
                size="1024x1024",
                quality="standard",
                n=1,
                response_format="b64_json"
            )

            b64_json = response.data[0].b64_json
            image_url_for_response = f"data:image/png;base64,{b64_json}"
            processing_time = (time.time() - start_time) * 1000

            generated_file = {
                "data": b64_json,
                "info": {"type": "image/png", "name": f"generated_image_{int(time.time())}.png"}
            }
            await add_message_with_files_to_conversation(
                conversation_id=prompt_request.conversation_id,
                message=f"Image generated from prompt: '{prompt_request.user_message}'",
                rol="assistant",
                files=[generated_file]
            )

            ai_response = AIResponse(
                status=ResponseStatus.SUCCESS,
                source=ResponseSource.OPENAI,
                items=[AIResponseItem(content_type="image_url", content=image_url_for_response, role="assistant")],
                metadata=ResponseMetadata(
                    model_name="dall-e-3",
                    processing_time_ms=processing_time,
                    raw_response=response.model_dump()
                ),
                conversation_id=prompt_request.conversation_id,
                user_id=prompt_request.user_id
            )
            return ai_response.to_external_format()

        except (openai.OpenAIError, ValueError) as e:
            error_message = f"Failed to generate image with OpenAI: {str(e)}"
            logger.error(error_message)
            await add_message_safely(prompt_request.conversation_id, error_message, "error")
            return create_error_response(
                ResponseSource.OPENAI, error_message,
                prompt_request.conversation_id, prompt_request.user_id
            ).to_external_format()