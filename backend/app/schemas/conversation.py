from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional

from app.schemas.chat import MessageResponse


class ConversationCreate(BaseModel):
    title: Optional[str] = Field(default="새 대화", max_length=255)


class ConversationResponse(BaseModel):
    id: str
    user_id: str
    title: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ConversationListItem(BaseModel):
    id: str
    title: str
    updated_at: datetime
    last_message: Optional[str] = None

    class Config:
        from_attributes = True


class ConversationWithMessages(BaseModel):
    id: str
    user_id: str
    title: str
    created_at: datetime
    updated_at: datetime
    messages: List[MessageResponse]

    class Config:
        from_attributes = True


class ConversationTitleUpdate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
