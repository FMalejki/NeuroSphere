"""This module defines the Pydantic model for prompt requests in the application."""
from typing import List, Optional, Any
from pydantic import BaseModel


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
    """
    prompt_ids: List[str]
    model_id: str
    user_message: str
    user_id: str
    conversation_id: str
    files: Optional[List[Any]]
