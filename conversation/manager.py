from typing import List

from sqlalchemy.orm import selectinload
from sqlmodel import Session, and_, select
from sqlmodel.ext.asyncio.session import AsyncSession

from auth.manager import UserManager
from src.base import BaseManager
from src.models import Conversation, ConversationParticipant, User


class ConversationManager(BaseManager[Conversation]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Conversation)
        self.user_manager = UserManager(session)

    async def get_by_user(self, user_id: str) -> List[Conversation]:
        statement = (
            select(Conversation)
            .join(ConversationParticipant)
            .where(ConversationParticipant.user_id == user_id)
            .order_by(Conversation.last_activity.desc())
        )
        result = await self.session.exec(statement)
        return result.all()

    async def get_or_create_private_conversation(self, user1_id: str, user2_id: str) -> Conversation:
        # Check if conversation already exists
        statement = (
            select(Conversation)
            .join(ConversationParticipant)
            .where(and_(Conversation.is_group == False, ConversationParticipant.user_id.in_([user1_id, user2_id])))
            .group_by(Conversation.id)
        )

        conversation = (await self.session.exec(statement)).first()
        if conversation:
            return conversation

        user1_obj = await self.user_manager.get_by_id(user1_id)
        user2_obj = await self.user_manager.get_by_id(user2_id)

        # creating a new conversation if there is no current convo...
        conversation = Conversation(is_group=False, participants=[user1_obj, user2_obj])
        conversation = await self.create(conversation)

        return conversation

    async def add_participant(self, conversation_id: str, user_id: str) -> bool:

        user = await self.user_manager.get_by_id(user_id)

        # fetching the conversation using selectinload to avoid lazy loadings in related objects.
        # lazy loading is not allowed outside an async context; it triggers errors.
        statement = (
            select(Conversation)
            .options(selectinload(Conversation.participants))
            .where(Conversation.id == conversation_id)
        )

        conversation = (await self.session.exec(statement)).first()
        if not conversation:
            return False

        conversation.participants.append(user)

        # ToDo: to be used later...
        # conversation.validate_conversation()

        self.session.add(conversation)
        await self.session.commit()
        return True

    async def remove_participant(self, conversation_id: str, user_id: str) -> bool:

        user = self.user_manager.get_by_id(user_id)
        conversation = self.get_by_id(conversation_id)

        statement = select(ConversationParticipant).where(
            and_(
                ConversationParticipant.conversation_id == conversation_id, ConversationParticipant.user_id == user_id
            )
        )
        participant = (await self.session.exec(statement)).first()
        if participant:
            conversation.participants.remove(user)
            self.session.add(conversation)
            await self.session.commit(conversation)
            return True
        return False
