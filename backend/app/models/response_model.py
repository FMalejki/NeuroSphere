"""
Response models for AI API interactions (internal use only).

This module defines Pydantic models that standardize the structure of responses
from various AI services internally, while maintaining backward compatibility
with the existing API contracts.
"""
from typing import Optional, List, Dict, Any, Union
from enum import Enum
from pydantic import BaseModel, Field

class ResponseStatus(str, Enum):
    """Enum representing possible response statuses."""
    SUCCESS = "success"
    ERROR = "error"
    PARTIAL = "partial"  

class ResponseSource(str, Enum):
    """Enum representing the source of the AI response."""
    OPENAI = "openai"
    GEMINI = "gemini"
    HUGGING_FACE = "huggingface"
    CUSTOM = "custom"
    UNKNOWN = "unknown"

class ResponseMetadata(BaseModel):
    """Metadata associated with an AI response."""
    model_name: Optional[str] = None
    tokens_used: Optional[int] = None
    processing_time_ms: Optional[float] = None
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    raw_response: Optional[Dict[str, Any]] = Field(default_factory=dict)
    additional_info: Optional[Dict[str, Any]] = Field(default_factory=dict)

class AIResponseItem(BaseModel):
    """
    Represents a single response item from an AI model.
    """
    content_type: str = "text"  
    content: Union[str, Dict[str, Any]]
    role: str = "assistant"  

class AIResponse(BaseModel):
    """
    Internal standardized model for AI responses across different providers.
    
    This model is for internal use only and will be converted to the expected
    format before being returned to the client.
    """
    status: ResponseStatus
    source: ResponseSource
    items: List[AIResponseItem] = Field(default_factory=list)
    message: Optional[str] = None 
    metadata: ResponseMetadata = Field(default_factory=ResponseMetadata)
    conversation_id: Optional[str] = None
    user_id: Optional[str] = None
    
    def to_external_format(self) -> str:
        """
        Convert the internal response model to the external format expected by the frontend.
        
        Returns:
            A string representation of the response as expected by the frontend.
        """
        if self.status == ResponseStatus.ERROR:
            return self.message or "An error occurred"
        
        for item in self.items:
            if item.content_type == "text" and isinstance(item.content, str):
                return item.content
        
        return ""
