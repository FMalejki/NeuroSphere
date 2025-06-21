"""This module defines the Pydantic model for prompt requests in the application."""
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field

class PromptRequestModel(BaseModel):
    """
    Pydantic model for prompt requests.
    
    Attributes:
        prompt_ids: List of prompt identifiers
        model_id: Identifier for the model to be used
        user_message: Message provided by the user
        user_id: Identifier for the user
        conversation_id: Identifier for the conversation
        files: Optional list of files provided with the request
        generate_image: Optional flag to indicate if an image should be generated
    """
    prompt_ids: List[str] = Field(..., description="List of prompt IDs to use")
    model_id: str = Field(..., description="ID of the AI model to use")
    user_message: str = Field(..., description="User's input message")
    user_id: str = Field(..., description="ID of the user making the request")
    conversation_id: str = Field(..., description="ID of the conversation")
    files: Optional[List[Dict[str, Any]]] = Field(None, description="List of files to process")
    generate_image: Optional[bool] = Field(False, description="Flag to indicate if an image should be generated")