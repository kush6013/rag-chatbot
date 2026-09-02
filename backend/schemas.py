from pydantic import BaseModel, Field
from typing import List, Any


class ChatRequest(BaseModel):
    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
    )

    conversation_id: str = "default"
    language: str = "en"
    model: str = "gemma"


class ChatResponse(BaseModel):
    answer: str

    sources: List[Any] = []

