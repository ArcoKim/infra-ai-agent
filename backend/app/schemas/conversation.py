from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import List, Optional

from app.schemas.chat import MessageResponse


class ConversationCreate(BaseModel):
    title: Optional[str] = Field(default="새 대화", max_length=255)


class ConversationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    title: str
    created_at: datetime
    updated_at: datetime


class ConversationListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    updated_at: datetime
    last_message: Optional[str] = None


class ConversationWithMessages(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    title: str
    created_at: datetime
    updated_at: datetime
    messages: List[MessageResponse]


class ConversationTitleUpdate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
