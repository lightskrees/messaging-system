from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime
from src.models.message import MessageType


class MessageCreate(BaseModel):
    recipient_id: str
    message_type: MessageType = MessageType.TEXT

    # Content fields - only populate based on message_type
    content: Optional[str] = None  # For TEXT messages

    # Image message fields
    image_url: Optional[str] = None
    image_filename: Optional[str] = None
    image_size: Optional[int] = None

    # File message fields
    file_url: Optional[str] = None
    file_filename: Optional[str] = None
    file_size: Optional[int] = None
    file_mime_type: Optional[str] = None

    # Voice message fields
    voice_url: Optional[str] = None
    voice_filename: Optional[str] = None
    voice_duration: Optional[int] = None

    # Video message fields
    video_url: Optional[str] = None
    video_filename: Optional[str] = None
    video_size: Optional[int] = None
    video_duration: Optional[int] = None
    video_thumbnail_url: Optional[str] = None

    # Optional caption for media messages
    caption: Optional[str] = None

    @field_validator('content')
    @classmethod
    def validate_text_content(cls, v, info):
        message_type = info.data.get('message_type')
        if message_type == MessageType.TEXT and not v:
            raise ValueError('Content is required for text messages')
        elif message_type != MessageType.TEXT and v:
            raise ValueError('Content should only be provided for text messages')
        return v

    @field_validator('image_url')
    @classmethod
    def validate_image_url(cls, v, info):
        message_type = info.data.get('message_type')
        if message_type == MessageType.IMAGE and not v:
            raise ValueError('Image URL is required for image messages')
        elif message_type != MessageType.IMAGE and v:
            raise ValueError('Image URL should only be provided for image messages')
        return v

    @field_validator('file_url')
    @classmethod
    def validate_file_url(cls, v, info):
        message_type = info.data.get('message_type')
        if message_type == MessageType.FILE and not v:
            raise ValueError('File URL is required for file messages')
        elif message_type != MessageType.FILE and v:
            raise ValueError('File URL should only be provided for file messages')
        return v

    @field_validator('voice_url')
    @classmethod
    def validate_voice_url(cls, v, info):
        message_type = info.data.get('message_type')
        if message_type == MessageType.VOICE and not v:
            raise ValueError('Voice URL is required for voice messages')
        elif message_type != MessageType.VOICE and v:
            raise ValueError('Voice URL should only be provided for voice messages')
        return v

    @field_validator('video_url')
    @classmethod
    def validate_video_url(cls, v, info):
        message_type = info.data.get('message_type')
        if message_type == MessageType.VIDEO and not v:
            raise ValueError('Video URL is required for video messages')
        elif message_type != MessageType.VIDEO and v:
            raise ValueError('Video URL should only be provided for video messages')
        return v


class MessageResponse(BaseModel):
    message_id: str
    timestamp: datetime
    message_type: MessageType
    is_read: bool
    sender_id: str
    recipient_id: str
    conversation_id: str

    # Content fields
    content: Optional[str] = None
    image_url: Optional[str] = None
    image_filename: Optional[str] = None
    image_size: Optional[int] = None
    file_url: Optional[str] = None
    file_filename: Optional[str] = None
    file_size: Optional[int] = None
    file_mime_type: Optional[str] = None
    voice_url: Optional[str] = None
    voice_filename: Optional[str] = None
    voice_duration: Optional[int] = None
    video_url: Optional[str] = None
    video_filename: Optional[str] = None
    video_size: Optional[int] = None
    video_duration: Optional[int] = None
    video_thumbnail_url: Optional[str] = None
    caption: Optional[str] = None
