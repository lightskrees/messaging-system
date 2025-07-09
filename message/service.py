import base64
from datetime import datetime
from typing import List, Optional

from cryptography.hazmat.primitives import serialization
from fastapi import HTTPException
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette import status

from auth.manager import UserManager
from auth.utils import load_private_key
from conversation.manager import ConversationManager
from encryption import decrypt_message, encrypt_message, get_session_key
from src.db_config import SessionDep, register_sent_messages
from src.models import Conversation, Message, MessageType, UserKey

from .manager import MessageManager
from .schemas import MessageCreate


class MessageService:
    def __init__(self, session: SessionDep):
        self.session, self.local_session = session
        self.message_manager = MessageManager(session)
        self.conversation_manager = ConversationManager(session)
        self.user_manager = UserManager(session)
        # self.notification_service = NotificationService()

    async def send_message(self, sender_id: str, message_data: MessageCreate) -> Message:

        recipient_userkey = (
            await self.session.exec(select(UserKey).where(UserKey.user_id == message_data.recipient_id))
        ).first()
        if not recipient_userkey:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="the recipient does not use our messaging system.",
            )
        # Get or create a conversation if the user is registered with our system.
        conversation = await self.conversation_manager.get_or_create_private_conversation(
            sender_id, message_data.recipient_id
        )

        # Create messages with appropriate fields based on type
        message_dict = {
            "sender_id": sender_id,
            "recipient_id": message_data.recipient_id,
            "conversation_id": conversation.id,
            "message_type": message_data.message_type,
        }
        nonce = None

        session_key = await get_session_key(sender_id, recipient_userkey)

        # Add type-specific fields
        if message_data.message_type == MessageType.TEXT:
            nonce, cipher_text = await encrypt_message(message_data.content, session_key=session_key)

            # message_dict["content"] = base64.b64encode(cipher_text).decode("utf-8")
            message_dict["content"] = cipher_text.hex()
        elif message_data.message_type == MessageType.IMAGE:
            message_dict.update(
                {
                    "image_url": message_data.image_url,
                    "image_filename": message_data.image_filename,
                    "image_size": message_data.image_size,
                }
            )
        elif message_data.message_type == MessageType.FILE:
            message_dict.update(
                {
                    "file_url": message_data.file_url,
                    "file_filename": message_data.file_filename,
                    "file_size": message_data.file_size,
                    "file_mime_type": message_data.file_mime_type,
                }
            )
        elif message_data.message_type == MessageType.VOICE:
            message_dict.update(
                {
                    "voice_url": message_data.voice_url,
                    "voice_filename": message_data.voice_filename,
                    "voice_duration": message_data.voice_duration,
                }
            )
        elif message_data.message_type == MessageType.VIDEO:
            message_dict.update(
                {
                    "video_url": message_data.video_url,
                    "video_filename": message_data.video_filename,
                    "video_size": message_data.video_size,
                    "video_duration": message_data.video_duration,
                    "video_thumbnail_url": message_data.video_thumbnail_url,
                }
            )

        # Add caption if provided
        if message_data.caption:
            message_dict["caption"] = message_data.caption

        message = Message(nonce=nonce.hex(), **message_dict)
        message = await self.message_manager.create(message)

        register_sent_messages(sender_id, message_data.recipient_id, message_data.content)

        # Update conversation last activity
        conversation.last_activity = datetime.now()
        await self.conversation_manager.update(conversation)

        return message

    async def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        return await self.conversation_manager.get_by_id(conversation_id)

    async def get_conversation_messages(self, conversation_id: str) -> List[Message]:
        received_messages = await self.message_manager.get_by_conversation(conversation_id)

        # sent_messages = []
        # recipient_id = None
        # sender_id = None
        # read_participants = False

        for message in received_messages:

            if message.message_type == MessageType.TEXT and message.content:
                recipient_userkey = await self.user_manager.get_user_key(message.recipient_id)
                session_key = await get_session_key(str(message.sender_id), recipient_userkey)

                # Decrypt the message content
                message_content = bytes.fromhex(message.content)
                nonce = bytes.fromhex(message.nonce)
                decrypted_message = await decrypt_message(message_content, session_key, nonce)
                message.content = decrypted_message

        # ToDo: logic of merging local-based and database message for displaying...

        # json_file = user_log_file(sender_id, recipient_id)
        #
        # if not os.path.exists(json_file):
        #     return []
        #
        # async with aiofiles.open(json_file, 'r') as f:
        #     content = await f.read()
        #     print("\n the content is: ", type(content), "\n")
        #     messages = content.splitlines()
        #     for message in messages:
        #         message_dict = json.loads(message)
        #         sent_messages.append(Message(**message_dict))
        #
        # messages = sent_messages + received_messages
        # messages.sort(key=lambda x: x.timestamp, reverse=True)

        return received_messages

    async def mark_message_as_read(self, message_id: str) -> bool:
        return await self.message_manager.mark_as_read(message_id)

    async def delete_message(self, message_id: str) -> bool:
        return await self.message_manager.delete(message_id)

    async def get_user_conversations(self, user_id: str) -> List[Conversation]:
        return await self.conversation_manager.get_by_user(user_id)
