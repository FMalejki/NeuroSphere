"""Module for storing API information for different AI models."""
from typing import Optional, Dict
from pydantic import BaseModel


class ModelApiInfo(BaseModel):
    """
    Data model for storing API information required to interact with AI models.

    Attributes:
        id: Unique identifier for the model
        name: Display name of the model
        api_endpoint: URL endpoint for API calls
        api_key: Authentication key for the API (optional)
        api_version: Version of the API (optional)
        parameters: Additional parameters for API requests (optional)
        headers: HTTP headers for API requests (optional)
    """
    id: str
    name: str
    api_endpoint: str
    api_key: Optional[str] = None
    api_version: Optional[str] = None
    parameters: Optional[Dict[str, str]] = None
    headers: Optional[Dict[str, str]] = None
