from typing import List, Optional
from datetime import datetime

from sqlmodel.ext.asyncio.session import AsyncSession

from src.models import Message, MessageType,Conversation
from .manager import MessageManager
from conversation.manager import  ConversationManager
from auth.manager import UserManager
from .schemas import MessageCreate


class MessageService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.message_manager = MessageManager(session)
        self.conversation_manager = ConversationManager(session)
        self.user_manager = UserManager(session)
        # self.notification_service = NotificationService()

    async def send_message(self, sender_id: str, message_data: MessageCreate) -> Message:
        # Get or create conversation
        conversation = await self.conversation_manager.get_or_create_private_conversation(
            sender_id, message_data.recipient_id
        )

        print("we got hereee")

        # Create messages with appropriate fields based on type
        message_dict = {
            "sender_id": sender_id,
            "recipient_id": message_data.recipient_id,
            "conversation_id": conversation.id,
            "message_type": message_data.message_type,
        }

        print("message dict", message_dict)

        # Add type-specific fields
        if message_data.message_type == MessageType.TEXT:
            message_dict["content"] = message_data.content
        elif message_data.message_type == MessageType.IMAGE:
            message_dict.update({
                "image_url": message_data.image_url,
                "image_filename": message_data.image_filename,
                "image_size": message_data.image_size,
            })
        elif message_data.message_type == MessageType.FILE:
            message_dict.update({
                "file_url": message_data.file_url,
                "file_filename": message_data.file_filename,
                "file_size": message_data.file_size,
                "file_mime_type": message_data.file_mime_type,
            })
        elif message_data.message_type == MessageType.VOICE:
            message_dict.update({
                "voice_url": message_data.voice_url,
                "voice_filename": message_data.voice_filename,
                "voice_duration": message_data.voice_duration,
            })
        elif message_data.message_type == MessageType.VIDEO:
            message_dict.update({
                "video_url": message_data.video_url,
                "video_filename": message_data.video_filename,
                "video_size": message_data.video_size,
                "video_duration": message_data.video_duration,
                "video_thumbnail_url": message_data.video_thumbnail_url,
            })

        # Add caption if provided
        if message_data.caption:
            message_dict["caption"] = message_data.caption


        message = Message(**message_dict)
        print("pro message dict", message)


        # Save message
        message = await self.message_manager.create(message)

        # Update conversation last activity
        conversation.last_activity = datetime.now()
        await self.conversation_manager.update(conversation)

        return message

    async def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        return await self.conversation_manager.get_by_id(conversation_id)

    async def get_conversation_messages(self, conversation_id: str) -> List[Message]:
        return await self.message_manager.get_by_conversation(conversation_id)

    async def mark_message_as_read(self, message_id: str) -> bool:
        return await self.message_manager.mark_as_read(message_id)

    async def delete_message(self, message_id: str) -> bool:
        return await self.message_manager.delete(message_id)

    async def get_user_conversations(self, user_id: str) -> List[Conversation]:
        return await self.conversation_manager.get_by_user(user_id)