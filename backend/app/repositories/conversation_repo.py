from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload
from typing import Optional, List

from app.models.conversation import Conversation
from app.models.message import Message


class ConversationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, conversation_id: str) -> Optional[Conversation]:
        result = await self.db.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        return result.scalar_one_or_none()

    async def get_by_id_with_messages(self, conversation_id: str) -> Optional[Conversation]:
        result = await self.db.execute(
            select(Conversation)
            .options(selectinload(Conversation.messages))
            .where(Conversation.id == conversation_id)
        )
        return result.scalar_one_or_none()

    async def get_user_conversations(self, user_id: str, limit: int = 50) -> List[Conversation]:
        result = await self.db.execute(
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(desc(Conversation.updated_at))
            .limit(limit)
        )
        return list(result.scalars().all())

    async def create(self, user_id: str, title: str = "새 대화") -> Conversation:
        conversation = Conversation(
            user_id=user_id,
            title=title
        )
        self.db.add(conversation)
        await self.db.flush()
        await self.db.refresh(conversation)
        return conversation

    async def update_title(self, conversation: Conversation, title: str) -> Conversation:
        conversation.title = title
        await self.db.flush()
        await self.db.refresh(conversation)
        return conversation

    async def touch(self, conversation: Conversation) -> None:
        """Update the updated_at timestamp."""
        await self.db.execute(
            Conversation.__table__.update()
            .where(Conversation.id == conversation.id)
            .values(updated_at=None)  # triggers onupdate
        )

    async def delete(self, conversation: Conversation) -> None:
        await self.db.delete(conversation)
        await self.db.flush()
