from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from bson import ObjectId
from app.models.prompt_model import PromptModel
from datetime import datetime

class Message(BaseModel):
    role: str  #user, error, system
    content: str
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat()) 
    #timestamp: Optional[str] = Field(default_factory=lambda: datetime.now().isoformat())  

class Conversation(BaseModel):
    id: str
    user_id: str
    chosen_model: Optional[str] = "gemini" #"gpt-3.5"
    chosen_prompts: Optional[List[str]] = [] ##do fr
    conversation_title: Optional[str] = "conversation"
    messages: List[Message] = []
    parameters: Optional[Dict[str, Any]] = {} 

class ConversationCreate(BaseModel):
    user_id: str
    chosen_model: Optional[str] = "gemini" #"gpt-3.5"
    chosen_prompts: Optional[List[str]] = []
    conversation_title: Optional[str] = "New Conversation"
    parameters: Optional[Dict[str, Any]] = {}


