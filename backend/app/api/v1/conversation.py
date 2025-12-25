from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_mysql_session
from app.core.security import get_current_user_id
from app.services.conversation_service import ConversationService
from app.schemas.conversation import (
    ConversationResponse,
    ConversationListItem,
    ConversationWithMessages,
    ConversationTitleUpdate,
)

router = APIRouter()


@router.get("/", response_model=List[ConversationListItem])
async def get_conversations(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_mysql_session)
):
    """Get all conversations for the current user."""
    service = ConversationService(db)
    return await service.get_user_conversations(user_id)


@router.get("/{conversation_id}", response_model=ConversationWithMessages)
async def get_conversation(
    conversation_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_mysql_session)
):
    """Get a specific conversation with messages."""
    service = ConversationService(db)
    return await service.get_conversation(user_id, conversation_id)


@router.post("/", response_model=ConversationResponse)
async def create_conversation(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_mysql_session)
):
    """Create a new conversation."""
    service = ConversationService(db)
    return await service.create_conversation(user_id)


@router.patch("/{conversation_id}/title", response_model=ConversationResponse)
async def update_conversation_title(
    conversation_id: str,
    request: ConversationTitleUpdate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_mysql_session)
):
    """Update conversation title."""
    service = ConversationService(db)
    return await service.update_title(user_id, conversation_id, request.title)


@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_mysql_session)
):
    """Delete a conversation."""
    service = ConversationService(db)
    await service.delete_conversation(user_id, conversation_id)
    return {"message": "Conversation deleted"}
