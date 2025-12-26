from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional, Literal


class ChatRequest(BaseModel):
    conversation_id: Optional[str] = None
    message: str = Field(..., min_length=1)


class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    conversation_id: str
    role: str
    content: str
    chart_data: Optional[dict] = None
    created_at: datetime


class ChatResponse(BaseModel):
    conversation_id: str
    message: MessageResponse
    assistant_message: MessageResponse


class StreamChunk(BaseModel):
    type: Literal["content", "chart", "done", "error"]
    content: Optional[str] = None
    chart_data: Optional[dict] = None
    conversation_id: Optional[str] = None
    error: Optional[str] = None
