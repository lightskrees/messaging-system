from typing import List

from sqlmodel import Session, select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.base import BaseManager
from src.models import Message


class MessageManager(BaseManager[Message]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Message)

    async def get_by_conversation(self, conversation_id: str) -> List[Message]:
        statement = select(Message).where(Message.conversation_id == conversation_id).order_by(Message.timestamp)
        result = await self.session.exec(statement)
        return result.all()

    async def get_unread_messages(self, user_id: str) -> List[Message]:
        statement = (
            select(Message)
            .where(Message.recipient_id == user_id, Message.is_read == False)
            .order_by(Message.timestamp)
        )
        result = await self.session.exec(statement)
        return result.all()

    async def mark_as_read(self, message_id: str) -> bool:
        message = await self.get_by_id(message_id)
        if message:
            message.is_read = True
            await self.update(message)
            return True
        return False
