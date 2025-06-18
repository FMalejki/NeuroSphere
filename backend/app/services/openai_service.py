"""
OpenAI Service Module
=====================

This module provides integration with various AI language model services including:
- OpenAI API
- Google Gemini API
- Hugging Face API

The module handles authentication, API key management, and provides a unified interface
for interacting with these AI services.
"""
import os
import logging
import time
from typing import List, Dict, Any, Optional

import requests
import openai
from dotenv import load_dotenv
from google import genai

from app.services.user_conversation_message_adder import add_message_to_conversation
from app.models.response_model import (
    AIResponse, AIResponseItem, ResponseStatus, 
    ResponseSource, ResponseMetadata
)

logger = logging.getLogger("app")

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

HUGGING_FACE_API_KEY = os.getenv("HUGGING_FACE_API_KEY")

logger.info("Loaded OpenAI API Key")
logger.info("Loaded Gemini API Key")
logger.info("Loaded Hugging Face API Key")

def build_payload(prompt: str, model: str = "gpt-3.5-turbo", max_tokens: int = 1000):
    """
    Build the payload for the OpenAI API request.
    """
    return {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.7
    }

def create_error_response(source: ResponseSource, message: str, conversation_id: Optional[str] = None, user_id: Optional[str] = None) -> AIResponse:
    """
    Create a standardized error response.
    """
    return AIResponse(
        status=ResponseStatus.ERROR,
        source=source,
        message=message,
        conversation_id=conversation_id,
        user_id=user_id
    )

async def add_message_safely(conversation_id: str, message: str, role: str):
    """
    Helper function to safely add a message to a conversation.
    """
    try:
        await add_message_to_conversation(conversation_id, message, role)
    except Exception as e:
        logger.error("Failed to add message to conversation: %s", str(e))

async def send_to_openai(prompt: str, conversation_id: str, user_id: str = None):
    """
    Send the prompt to OpenAI API.
    """
    try:
        start_time = time.time()
        payload = build_payload(prompt)
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(**payload)
        
        content = response.choices[0].message.content.strip()
        processing_time = (time.time() - start_time) * 1000  # convert to ms
        
        ai_response = AIResponse(
            status=ResponseStatus.SUCCESS,
            source=ResponseSource.OPENAI,
            items=[
                AIResponseItem(
                    content_type="text",
                    content=content,
                    role="assistant"
                )
            ],
            metadata=ResponseMetadata(
                model_name=response.model,
                tokens_used=response.usage.total_tokens,
                processing_time_ms=processing_time,
                prompt_tokens=response.usage.prompt_tokens,
                completion_tokens=response.usage.completion_tokens,
                raw_response=response.model_dump()
            ),
            conversation_id=conversation_id,
            user_id=user_id
        )
        
        await add_message_safely(conversation_id, content, "assistant")
        
        return ai_response.to_external_format()
        
    except (openai.OpenAIError, ValueError) as e:
        logger.error("Failed to connect to OpenAI API: %s", e)
        error_message = f"Failed to connect to OpenAI API: {e}"
        
        await add_message_safely(conversation_id, error_message, "error")
        
        error_response = create_error_response(
            ResponseSource.OPENAI, 
            error_message,
            conversation_id,
            user_id
        )
        
        return error_response.to_external_format()

async def send_to_gemini(prompt: str, conversation_id: str, user_id: str = None):
    """
    Send the prompt to Gemini API using Google GenAI.
    """
    try:
        start_time = time.time()
        
        client = genai.Client(api_key=GEMINI_API_KEY)
        
        model_name = "gemini-2.0-flash"
        response = client.models.generate_content(
            model=model_name,
            contents=prompt
        )
        
        content = response.text.strip()
        processing_time = (time.time() - start_time) * 1000  # convert to ms
        
        ai_response = AIResponse(
            status=ResponseStatus.SUCCESS,
            source=ResponseSource.GEMINI,
            items=[
                AIResponseItem(
                    content_type="text",
                    content=content,
                    role="assistant"
                )
            ],
            metadata=ResponseMetadata(
                model_name=model_name,
                processing_time_ms=processing_time,
                raw_response={"text": content}
            ),
            conversation_id=conversation_id,
            user_id=user_id
        )
        
        await add_message_safely(conversation_id, content, "assistant")
        
        return ai_response.to_external_format()
        
    except Exception as e:
        logger.error("Failed to connect to Gemini API: %s", e)
        error_message = f"Failed to connect to Gemini API: {e}"
        
        await add_message_safely(conversation_id, error_message, "error")
        
        error_response = create_error_response(
            ResponseSource.GEMINI, 
            error_message,
            conversation_id,
            user_id
        )
        
        return error_response.to_external_format()

async def send_to_hugging_face(prompt: str, conversation_id: str, user_id: str = None):
    """
    Send the prompt to Hugging Face API.
    """
    try:
        start_time = time.time()
        
        url = "https://api-inference.huggingface.co/models/bigscience/bloom"
        headers = {"Authorization": f"Bearer {HUGGING_FACE_API_KEY}"}
        data = {"inputs": prompt}
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        
        content = response.json()[0]["generated_text"].strip()
        processing_time = (time.time() - start_time) * 1000  # convert to ms
        
        ai_response = AIResponse(
            status=ResponseStatus.SUCCESS,
            source=ResponseSource.HUGGING_FACE,
            items=[
                AIResponseItem(
                    content_type="text",
                    content=content,
                    role="assistant"
                )
            ],
            metadata=ResponseMetadata(
                model_name="bigscience/bloom",
                processing_time_ms=processing_time,
                raw_response=response.json()
            ),
            conversation_id=conversation_id,
            user_id=user_id
        )
        
        await add_message_safely(conversation_id, content, "assistant")
        
        return ai_response.to_external_format()
        
    except (requests.RequestException, ValueError, KeyError, IndexError) as e:
        logger.error("Failed to connect to Hugging Face API: %s", e)
        error_message = f"Failed to connect to Hugging Face API: {e}"
        
        await add_message_safely(conversation_id, error_message, "error")
        
        error_response = create_error_response(
            ResponseSource.HUGGING_FACE, 
            error_message,
            conversation_id,
            user_id
        )
        
        return error_response.to_external_format()
    
async def send_to_openai_with_images(
    content: List[Dict[str, Any]], 
    conversation_id: str, 
    user_id: str = None
):
    """
    Send multimodal content (text + images) to OpenAI API.
    """
    try:
        start_time = time.time()
        logger.info("Sending multimodal request to OpenAI")
        
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        
        model_name = "gpt-4-vision-preview"
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "user", "content": content}
            ],
            max_tokens=1000
        )
        
        content = response.choices[0].message.content.strip()
        processing_time = (time.time() - start_time) * 1000  
        
        ai_response = AIResponse(
            status=ResponseStatus.SUCCESS,
            source=ResponseSource.OPENAI,
            items=[
                AIResponseItem(
                    content_type="text",
                    content=content,
                    role="assistant"
                )
            ],
            metadata=ResponseMetadata(
                model_name=model_name,
                tokens_used=response.usage.total_tokens,
                processing_time_ms=processing_time,
                prompt_tokens=response.usage.prompt_tokens,
                completion_tokens=response.usage.completion_tokens,
                raw_response=response.model_dump()
            ),
            conversation_id=conversation_id,
            user_id=user_id
        )
        
        await add_message_safely(conversation_id, content, "assistant")
        
        return ai_response.to_external_format()
        
    except (openai.OpenAIError, ValueError) as e:
        error_message = f"Failed to connect to OpenAI Vision API: {str(e)}"
        logger.error(error_message)
        
        await add_message_safely(conversation_id, error_message, "error")
        
        error_response = create_error_response(
            ResponseSource.OPENAI, 
            error_message,
            conversation_id,
            user_id
        )
        
        return error_response.to_external_format()

async def send_to_gemini_with_files(
    content: List[Dict[str, Any]],
    text_prompt: str,
    conversation_id: str,
    user_id: str = None
):
    """
    Send multimodal content (text + files of any type, base64 encoded) to Gemini API using direct REST API.
    """
    try:
        start_time = time.time()
        logger.info("Sending multimodal request to Gemini REST API (files supported)")

        parts = []
        if text_prompt:
            parts.append({"text": text_prompt})

        for item in content:
            if "data" in item and "info" in item and "type" in item["info"]:
                mime_type = item["info"]["type"]
                base64_data = item["data"]
                parts.append({
                    "inline_data": {
                        "mime_type": mime_type,
                        "data": base64_data
                    }
                })
            elif item.get("type") == "image_url" and "image_url" in item:
                image_url = item["image_url"]["url"]
                if image_url.startswith("data:"):
                    mime_type = image_url.split(";")[0].replace("data:", "")
                    base64_data = image_url.split(",")[1]
                    parts.append({
                        "inline_data": {
                            "mime_type": mime_type,
                            "data": base64_data
                        }
                    })

        payload = {
            "contents": [{
                "parts": parts
            }],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 2048
            }
        }

        model_name = "gemini-1.5-flash"
        api_url = (
            f"https://generativelanguage.googleapis.com/v1/models/"
            f"{model_name}:generateContent?key={GEMINI_API_KEY}"
        )
        response = requests.post(
            api_url,
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=30
        )

        processing_time = (time.time() - start_time) * 1000  

        if response.status_code == 200:
            result = response.json()
            if "candidates" in result and len(result["candidates"]) > 0:
                if "content" in result["candidates"][0]:
                    content_data = result["candidates"][0]["content"]
                    if "parts" in content_data and len(content_data["parts"]) > 0:
                        content = content_data["parts"][0].get("text", "")
                        
                        # Create standardized response
                        ai_response = AIResponse(
                            status=ResponseStatus.SUCCESS,
                            source=ResponseSource.GEMINI,
                            items=[
                                AIResponseItem(
                                    content_type="text",
                                    content=content,
                                    role="assistant"
                                )
                            ],
                            metadata=ResponseMetadata(
                                model_name=model_name,
                                processing_time_ms=processing_time,
                                raw_response=result
                            ),
                            conversation_id=conversation_id,
                            user_id=user_id
                        )
                        
                        await add_message_safely(conversation_id, content, "assistant")
                        
                        return ai_response.to_external_format()

            error_message = "Could not extract response text from Gemini API"
            logger.error(error_message)
            
            await add_message_safely(conversation_id, error_message, "error")
            
            error_response = create_error_response(
                ResponseSource.GEMINI, 
                error_message,
                conversation_id,
                user_id
            )
            
            return error_response.to_external_format()

        error_message = f"Gemini API returned error {response.status_code}: {response.text}"
        logger.error(error_message)
        
        await add_message_safely(conversation_id, error_message, "error")
        
        error_response = create_error_response(
            ResponseSource.GEMINI, 
            error_message,
            conversation_id,
            user_id
        )
        
        return error_response.to_external_format()

    except (requests.RequestException, ValueError, KeyError) as e:
        error_message = f"Failed to connect to Gemini Vision API: {str(e)}"
        logger.error(error_message)
        
        await add_message_safely(conversation_id, error_message, "error")
        
        error_response = create_error_response(
            ResponseSource.GEMINI, 
            error_message,
            conversation_id,
            user_id
        )
        
        return error_response.to_external_format()