from pydantic import BaseModel, Field
from typing import Optional


class CategorizeRequest(BaseModel):
    description: str = Field(min_length=1, max_length=500)


class CategorizeResponse(BaseModel):
    category: str
    type: str
    amount: Optional[float]
    confidence: str
    ai_available: bool


class AssistantRequest(BaseModel):
    question: str = Field(min_length=1, max_length=1000)


class AssistantResponse(BaseModel):
    answer: str
    ai_available: bool
