import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

import sqlalchemy.dialects.postgresql as pg
from sqlmodel import Column, Field, Relationship, SQLModel


class MessageType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    FILE = "file"
    VOICE = "voice"
    VIDEO = "video"


class Message(SQLModel, table=True):
    id: uuid.UUID = Field(sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4))
    timestamp: datetime = Field(default_factory=datetime.now)
    message_type: MessageType = Field(default=MessageType.TEXT)
    is_read: bool = Field(default=False)
    sender_id: Optional[uuid.UUID] = Field(foreign_key="user.id")
    recipient_id: Optional[uuid.UUID] = Field(foreign_key="user.id")
    conversation_id: Optional[uuid.UUID] = Field(foreign_key="conversation.id")

    #################
    # MEDIA METADATA
    ################

    # Content field populated only for text message types.
    # For TEXT messages
    content: Optional[str] = Field(default=None)

    # For IMAGE messages
    image_url: Optional[str] = Field(default=None)
    image_filename: Optional[str] = Field(default=None)
    image_size: Optional[int] = Field(default=None)  # Size in bytes

    # For FILE messages
    file_url: Optional[str] = Field(default=None)
    file_filename: Optional[str] = Field(default=None)
    file_size: Optional[int] = Field(default=None)  # Size in bytes
    file_mime_type: Optional[str] = Field(default=None)

    # For VOICE messages
    voice_url: Optional[str] = Field(default=None)
    voice_filename: Optional[str] = Field(default=None)
    voice_duration: Optional[int] = Field(default=None)  # Duration in seconds

    # For VIDEO messages
    video_url: Optional[str] = Field(default=None)
    video_filename: Optional[str] = Field(default=None)
    video_size: Optional[int] = Field(default=None)  # Size in bytes
    video_duration: Optional[int] = Field(default=None)  # Duration in seconds
    video_thumbnail_url: Optional[str] = Field(default=None)

    # Optional caption for media messages
    caption: Optional[str] = Field(default=None)

    # Relationships
    sender: Optional["User"] = Relationship(
        back_populates="sent_messages", sa_relationship_kwargs={"foreign_keys": "Message.sender_id"}
    )
    recipient: Optional["User"] = Relationship(
        back_populates="received_messages", sa_relationship_kwargs={"foreign_keys": "Message.recipient_id"}
    )
    conversation: Optional["Conversation"] = Relationship(back_populates="messages")
