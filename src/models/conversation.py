from sqlmodel import SQLModel, Field, Relationship, Column
import sqlalchemy.dialects.postgresql as pg
from typing import Optional, List
from datetime import datetime
import uuid


class ConversationParticipant(SQLModel, table=True):
    conversation_id: uuid.UUID = Field(foreign_key="conversation.id", primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", primary_key=True)


class Conversation(SQLModel, table=True):
    id : uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )
    conversation_name: Optional[str] = Field(default=None)
    is_group: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.now)
    last_activity: datetime = Field(default_factory=datetime.now)

    # Relationships
    messages: List["Message"] = Relationship(back_populates="conversation", link_model=ConversationParticipant)
    participants : List["User"] = Relationship(back_populates="conversations", link_model=ConversationParticipant)

    def validate_private_conversation(self):
        if not self.is_group and len(self.participants) > 2:
            raise ValueError("conversation cannot have more than 2 participants")