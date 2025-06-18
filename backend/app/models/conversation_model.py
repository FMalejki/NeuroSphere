"""
Data models for conversations, messages, and related functionality.
This module defines the structure for conversation data in the application.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field


class FileData(BaseModel):
    """Represents a file uploaded in a conversation with metadata and content."""
    name: str
    type: str
    size: int
    data: str


class Message(BaseModel):
    """Represents a single message in a conversation with role and timestamp information."""
    role: str  #user, error, system
    content: str
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    #timestamp: Optional[str] = Field(default_factory=lambda: datetime.now().isoformat())


class Conversation(BaseModel):
    """Represents a complete conversation with its messages and metadata."""
    id: str
    user_id: str
    chosen_model: Optional[str] = "gemini" #"gpt-3.5"
    chosen_prompts: Optional[List[str]] = [] ##do fr
    conversation_title: Optional[str] = "conversation"
    messages: List[Message] = []
    parameters: Optional[Dict[str, Any]] = {}


class ConversationCreate(BaseModel):
    """Model for creating a new conversation with required and optional fields."""
    user_id: str
    chosen_model: Optional[str] = "gemini" #"gpt-3.5"
    chosen_prompts: Optional[List[str]] = []
    conversation_title: Optional[str] = "New Conversation"
    parameters: Optional[Dict[str, Any]] = {}
