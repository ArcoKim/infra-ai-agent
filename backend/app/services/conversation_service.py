from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from typing import List, Optional

from app.repositories.conversation_repo import ConversationRepository
from app.repositories.message_repo import MessageRepository
from app.schemas.conversation import (
    ConversationResponse,
    ConversationListItem,
    ConversationWithMessages,
)
from app.schemas.chat import MessageResponse


class ConversationService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.conversation_repo = ConversationRepository(db)
        self.message_repo = MessageRepository(db)

    async def get_user_conversations(self, user_id: str) -> List[ConversationListItem]:
        conversations = await self.conversation_repo.get_user_conversations(user_id)

        result = []
        for conv in conversations:
            # Get last message preview
            messages = await self.message_repo.get_by_conversation(conv.id, limit=1)
            last_message = messages[0].content[:100] if messages else None

            result.append(ConversationListItem(
                id=conv.id,
                title=conv.title,
                updated_at=conv.updated_at,
                last_message=last_message
            ))

        return result

    async def get_conversation(
        self,
        user_id: str,
        conversation_id: str
    ) -> ConversationWithMessages:
        conversation = await self.conversation_repo.get_by_id_with_messages(conversation_id)

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )

        if conversation.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )

        return ConversationWithMessages(
            id=conversation.id,
            user_id=conversation.user_id,
            title=conversation.title,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
            messages=[MessageResponse.model_validate(m) for m in conversation.messages]
        )

    async def create_conversation(
        self,
        user_id: str,
        title: Optional[str] = None
    ) -> ConversationResponse:
        conversation = await self.conversation_repo.create(
            user_id=user_id,
            title=title or "새 대화"
        )
        return ConversationResponse.model_validate(conversation)

    async def update_title(
        self,
        user_id: str,
        conversation_id: str,
        title: str
    ) -> ConversationResponse:
        conversation = await self.conversation_repo.get_by_id(conversation_id)

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )

        if conversation.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )

        updated = await self.conversation_repo.update_title(conversation, title)
        return ConversationResponse.model_validate(updated)

    async def delete_conversation(
        self,
        user_id: str,
        conversation_id: str
    ) -> None:
        conversation = await self.conversation_repo.get_by_id(conversation_id)

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )

        if conversation.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )

        await self.conversation_repo.delete(conversation)
