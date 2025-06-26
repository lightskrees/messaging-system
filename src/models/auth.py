import uuid
from datetime import datetime
from typing import List, Optional

import sqlalchemy.dialects.postgresql as pg
from sqlmodel import Column, Field, Relationship, SQLModel

from src.models.conversation import ConversationParticipant


class User(SQLModel, table=True):
    id: uuid.UUID = Field(sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4))
    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True, index=True)
    phone_number: str = Field(unique=True, index=True)
    password_hash: str
    is_online: bool = Field(default=False)
    last_seen: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.now)

    # Relationships
    sent_messages: List["Message"] = Relationship(
        back_populates="sender", sa_relationship_kwargs={"foreign_keys": "Message.sender_id", "lazy": "selectin"}
    )
    received_messages: List["Message"] = Relationship(
        back_populates="recipient", sa_relationship_kwargs={"foreign_keys": "Message.recipient_id", "lazy": "selectin"}
    )

    conversations: List["Conversation"] = Relationship(
        back_populates="participants", link_model=ConversationParticipant, sa_relationship_kwargs={"lazy": "selectin"}
    )


# FOR CRYPTOGRAPHIC KEYS STORAGE
class UserKey(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id")
    public_key: bytes = Field(sa_column=Column(pg.BYTEA, nullable=False))
    algorithm: str  # Example: 'ECDH_SECP384R1'
    created_at: datetime = Field(default_factory=datetime.now)
    revoked: bool = Field(default=False)
