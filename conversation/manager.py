from sqlmodel import Session, select, and_
from typing import List

from sqlmodel.ext.asyncio.session import AsyncSession

from src.base import ModelBase
from src.models import Conversation, ConversationParticipant, User


class ConversationRepository(ModelBase[Conversation]):
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
        ).group_by(Conversation.conversation_id)

        existing = await self.session.exec(statement).first()
        if existing:
            return existing

        # Create new conversation
        conversation = Conversation(is_group=False)
        conversation = await self.create(conversation)

        user_1_obj = self.session.get(User, user1_id)
        user_2_obj = self.session.get(User, user2_id)

        conversation.participants.append(user_1_obj)
        conversation.participants.append(user_2_obj)

        self.session.add(conversation)
        await self.session.refresh(conversation)

        #ToDo: to check if it is in sync with the link model.
        # # Add participants
        # self.session.add(ConversationParticipant(conversation_id=conversation.conversation_id, user_id=user1_id))
        # self.session.add(ConversationParticipant(conversation_id=conversation.conversation_id, user_id=user2_id))
        # await self.session.commit()

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
        participant = await self.session.exec(statement).first()
        if participant:
            await self.session.delete(participant)
            await self.session.commit()
            return True
        return False