import asyncio
import os
import openai
from dotenv import load_dotenv
from google import genai  
import requests
from app.db.get_conversation_info import update_message_to_conversation
from app.services.user_conversation_message_adder import add_message_to_conversation
from typing import List, Dict, Any
import base64

# Load environment variables
load_dotenv()

# OpenAI API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# Gemini API Key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Hugging Face API Key
HUGGING_FACE_API_KEY = os.getenv("HUGGING_FACE_API_KEY")

# Debugging: Print confirmation of loaded API keys
print("\nLoaded OpenAI API Key\n")
print("Loaded Gemini API Key\n")
print("Loaded Hugging Face API Key\n")

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

def parse_response(response):
    """
    Parse the response from the OpenAI API.
    """
    try:
        return response["choices"][0]["message"]["content"].strip() #######!!
    except (KeyError, IndexError) as e:
        raise ValueError(f"Failed to parse OpenAI response: {e}")

def send_to_openai(prompt: str, conversation_id: str, user_id: str):
    """
    Send the prompt to OpenAI API.
    """
    try:
        payload = build_payload(prompt)
        response = openai.ChatCompletion.create(**payload)

        return parse_response(response)
    except Exception as e:

        # conversation_id  # Replace with actual user ID when possi'bl
        asyncio.create_task(add_message_to_conversation(conversation_id, "Failed to connect to OpenAI API", "error"))

        return f"Failed to connect to OpenAI API: {e}"

def send_to_gemini(prompt: str, conversation_id: str, user_id: str):
    """
    Send the prompt to Gemini API using Google GenAI.
    """
    try:
        # Initialize the GenAI client
        client = genai.Client(api_key=GEMINI_API_KEY)
        
        # Generate content using the Gemini model
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        
        #return response..
        #user_id = conversation_id  # Replace with actual user ID when possi'bl
        print("before add message")
        asyncio.create_task(add_message_to_conversation(conversation_id, response.text.strip(), "assistant"))

        return response.text.strip()
    except Exception as e:

        #user_id = conversation_id  # Replace with actual user ID when possi'bl
        asyncio.create_task(add_message_to_conversation(conversation_id, "Failed to connect to Gemini API", "error"))
        
        return f"Failed to connect to Gemini API: {e}"

def send_to_hugging_face(prompt: str, conversation_id: str, user_id: str):
    """
    Send the prompt to Hugging Face API.
    """
    try:
        # Użyj poprawnego modelu z Hugging Face
        url = "https://api-inference.huggingface.co/models/bigscience/bloom"  # Przykładowy model
        headers = {"Authorization": f"Bearer {HUGGING_FACE_API_KEY}"}
        data = {"inputs": prompt}
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()  # Raise an error for HTTP codes 4xx/5xx
        #user_id = conversation_id  # Replace with actual user ID when possi'bl
        asyncio.create_task(add_message_to_conversation(conversation_id, response.json()[0]["generated_text"].strip(), "assistant"))

        return response.json()[0]["generated_text"].strip()
    except Exception as e:

        #user_id = conversation_id  # Replace with actual user ID when possi'bl
        asyncio.create_task(add_message_to_conversation(conversation_id, "Failed to connect to Hugging Face API", "error"))

        return f"Failed to connect to Hugging Face API: {e}"
    
def send_to_openai_with_images(content: List[Dict[str, Any]], conversation_id: str, user_id: str):
    """
    Send multimodal content (text + images) to OpenAI API.
    """
    try:
        print("Sending multimodal request to OpenAI")
        
        # Use the OpenAI client
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        
        # Format the request for OpenAI
        response = client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[
                {"role": "user", "content": content}
            ],
            max_tokens=1000
        )
        
        # Extract the response text
        ai_response = response.choices[0].message.content.strip()
        
        # Add to conversation history
        asyncio.create_task(add_message_to_conversation(conversation_id, ai_response, "assistant"))
        
        return ai_response
    except Exception as e:
        error_msg = f"Failed to connect to OpenAI Vision API: {str(e)}"
        print(error_msg)
        asyncio.create_task(add_message_to_conversation(conversation_id, error_msg, "error"))
        return error_msg

def send_to_gemini_with_images(content: List[Dict[str, Any]], text_prompt: str, conversation_id: str, user_id: str):
    """
    Sending multimodal content (text + images + files) to Gemini API using direct REST API
    """
    try:
        print("Sending multimodal request to Gemini REST API")
        
        parts = []
        
        parts.append({
            "text": text_prompt
        })
        
        for item in content:
            if item.get("type") == "image_url" and "image_url" in item:
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
        
        api_url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"        
        import requests
        response = requests.post(
            api_url,
            headers={"Content-Type": "application/json"},
            json=payload
        )
        
        if response.status_code == 200:
            result = response.json()
            
            if "candidates" in result and len(result["candidates"]) > 0:
                if "content" in result["candidates"][0]:
                    content = result["candidates"][0]["content"]
                    if "parts" in content and len(content["parts"]) > 0:
                        ai_response = content["parts"][0].get("text", "")
                        
                        asyncio.create_task(add_message_to_conversation(conversation_id, ai_response, "assistant"))
                        
                        return ai_response
            
            error_msg = "Could not extract response text from Gemini API"
            print(error_msg)
            print("API response:", result)
            asyncio.create_task(add_message_to_conversation(conversation_id, error_msg, "error"))
            return error_msg
        else:
            error_msg = f"Gemini API returned error {response.status_code}: {response.text}"
            print(error_msg)
            asyncio.create_task(add_message_to_conversation(conversation_id, error_msg, "error"))
            return error_msg
            
    except Exception as e:
        error_msg = f"Failed to connect to Gemini Vision API: {str(e)}"
        print(error_msg)
        asyncio.create_task(add_message_to_conversation(conversation_id, error_msg, "error"))
        return error_msg

def test_all_apis():
    """
    Test all APIs (OpenAI, Gemini, Hugging Face) with the same prompt and display their responses.
    """
    prompt = "Introduce yourself in 1 sentence as a language model."
    print("\nTesting OpenAI API...\n")
    openai_response = send_to_openai(prompt, "1", "1")
    print(f"OpenAI Response: {openai_response}\n")

    print("\nTesting Gemini API...\n")
    gemini_response = send_to_gemini(prompt, "1", "1")
    print(f"Gemini Response: {gemini_response}\n")

    print("\nTesting Hugging Face API...\n")
    hugging_face_response = send_to_hugging_face(prompt, "1", "1")
    print(f"Hugging Face Response: {hugging_face_response}\n")
