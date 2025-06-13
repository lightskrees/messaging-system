from sqlmodel import Session, select, and_
from typing import List

from sqlmodel.ext.asyncio.session import AsyncSession

from src.base import ModelBase
from src.models import Conversation, ConversationParticipant, User


class ConversationManager(ModelBase[Conversation]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Conversation)

    async def get_by_user(self, user_id: str) -> List[Conversation]:
        statement = select(Conversation).join(ConversationParticipant).where(
            ConversationParticipant.user_id == user_id
        ).order_by(Conversation.last_activity.desc())
        result = await self.session.exec(statement)
        return result.all()


    async def get_or_create_private_conversation(self, user1_id: str, user2_id: str) -> Conversation:
        # Check if conversation already exists
        statement = select(Conversation).join(ConversationParticipant).where(
            and_(
                Conversation.is_group == False,
                ConversationParticipant.user_id.in_([user1_id, user2_id])
            )
        ).group_by(Conversation.id)

        conversation = (await self.session.exec(statement)).first()
        if conversation:
            return conversation

        user1_obj = (await self.session.exec(select(User).where(User.id==user1_id))).first()
        user2_obj = (await self.session.exec(select(User).where(User.id==user2_id))).first()

        # creating a new conversation if there is no current convo...
        conversation = Conversation(is_group=False, participants=[user1_obj, user2_obj])
        conversation = await self.create(conversation)

        return conversation

    async def add_participant(self, conversation_id: str, user_id: str) -> bool:
        participant = ConversationParticipant(conversation_id=conversation_id, user_id=user_id)
        self.session.add(participant)
        await self.session.commit()
        return True

    async def remove_participant(self, conversation_id: str, user_id: str) -> bool:
        statement = select(ConversationParticipant).where(
            and_(
                ConversationParticipant.conversation_id == conversation_id,
                ConversationParticipant.user_id == user_id
            )
        )
        result = await self.session.exec(statement)
        participant = result.first()
        if participant:
            await self.session.delete(participant)
            await self.session.commit()
            return True
        return False