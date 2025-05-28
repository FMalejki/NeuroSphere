from typing import List, Optional, Any
from pydantic import BaseModel


class PromptRequestModel(BaseModel):
    prompt_ids: List[str]
    model_id: str
    user_message: str
    user_id: str
    conversation_id: str
    files: Optional[List[Any]]