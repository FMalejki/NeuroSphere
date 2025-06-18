"""Module for defining the prompt data model used in the application."""

from pydantic import BaseModel

class PromptModel(BaseModel):
    """
    Data model representing a prompt.
    
    Attributes:
        id: Unique identifier for the prompt
        text: The content of the prompt
    """
    id: str
    text: str
