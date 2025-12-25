from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import Optional, List

from app.models.message import Message, MessageRole


class MessageRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, message_id: str) -> Optional[Message]:
        result = await self.db.execute(
            select(Message).where(Message.id == message_id)
        )
        return result.scalar_one_or_none()

    async def get_by_conversation(
        self,
        conversation_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[Message]:
        result = await self.db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at)
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def get_recent_messages(
        self,
        conversation_id: str,
        limit: int = 20
    ) -> List[Message]:
        """Get the most recent messages for context."""
        result = await self.db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(desc(Message.created_at))
            .limit(limit)
        )
        messages = list(result.scalars().all())
        return list(reversed(messages))  # Return in chronological order

    async def create(
        self,
        conversation_id: str,
        role: str,
        content: str,
        chart_data: Optional[dict] = None
    ) -> Message:
        # Convert string to MessageRole enum
        role_enum = MessageRole(role.lower()) if isinstance(role, str) else role
        message = Message(
            conversation_id=conversation_id,
            role=role_enum,
            content=content,
            chart_data=chart_data
        )
        self.db.add(message)
        await self.db.flush()
        await self.db.refresh(message)
        return message

    async def delete(self, message: Message) -> None:
        await self.db.delete(message)
        await self.db.flush()
