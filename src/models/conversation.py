import uuid
from datetime import datetime
from typing import List, Optional

import sqlalchemy.dialects.postgresql as pg
from fastapi import HTTPException
from sqlmodel import Column, Field, Relationship, SQLModel
from starlette import status


class ConversationParticipant(SQLModel, table=True):
    conversation_id: uuid.UUID = Field(foreign_key="conversation.id", primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", primary_key=True)


class Conversation(SQLModel, table=True):
    id: uuid.UUID = Field(sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4))
    conversation_name: Optional[str] = Field(default=None)
    is_group: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.now)
    last_activity: datetime = Field(default_factory=datetime.now)

    # Relationships
    messages: List["Message"] = Relationship(
        back_populates="conversation", sa_relationship_kwargs={"lazy": "selectin"}
    )
    participants: List["User"] = Relationship(back_populates="conversations", link_model=ConversationParticipant)

    def validate_conversation(self):
        if not self.is_group and len(self.participants) > 2:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Private conversation cannot have more than 2 participants",
            )
