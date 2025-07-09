import json
import os
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from auth.manager import UserManager
from auth.routes import get_current_user
from message.schemas import MessageResponse
from message.service import MessageService
from src.db_config import SessionDep, get_sessions, user_log_file
from src.models import User

from .manager import ConversationManager
from .schemas import ConversationResponse

router = APIRouter(prefix="/conversations", tags=["conversations"])

# authentication dependency
UserAuthentication = Annotated[User, Depends(get_current_user)]


@router.get("/", response_model=List[ConversationResponse])
async def get_user_conversations(
    current_user: UserAuthentication,
    session: SessionDep = Depends(get_sessions),
):
    message_service = MessageService(session)
    conversations = await message_service.get_user_conversations(str(current_user.id))
    return conversations


@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(conversation_id: str, _: UserAuthentication, session: SessionDep = Depends(get_sessions)):
    message_service = MessageService(session)
    conversation = await message_service.get_conversation(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation


# @router.get("/{conversation_id}/messages", response_model=List[MessageResponse])
# async def get_conversation_messages(
#     conversation_id: str,
#     session: SessionDep,
#     _: UserAuthentication,
# ):
#     message_service = MessageService(session)
#     messages = await message_service.get_conversation_messages(conversation_id)
#     return messages


@router.get("/{recipient_id}/messages")
async def get_conversation_messages(
    recipient_id: str, auth_user: UserAuthentication, session: SessionDep = Depends(get_sessions)
):
    user_manager = UserManager(session)
    recipient = await user_manager.get_by_id(recipient_id)

    if not recipient:
        raise HTTPException(status_code=404, detail="Recipient not found")

    path = user_log_file(str(auth_user.id), str(recipient.id))

    if not os.path.exists(path):
        return {"messages": []}
    with open(path, "r") as f:
        messages = json.load(f)
    return {"messages": messages}


@router.get("/{conversation_id}/received_messages")
async def get_conversation_messages(
    conversation_id: str,
    _: UserAuthentication,
    session: SessionDep = Depends(get_sessions),
) -> List[MessageResponse]:
    message_service = MessageService(session)

    messages = await message_service.get_conversation_messages(conversation_id)

    return messages


@router.post("/{conversation_id}/participants", status_code=status.HTTP_200_OK)
async def add_participant(
    conversation_id: str,
    user_id: str,
    _: User = Depends(get_current_user),
    session: SessionDep = Depends(get_sessions),
):
    conversation_manager = ConversationManager(session)
    success = await conversation_manager.add_participant(conversation_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Conversation or user not found")
    return {"status": "participant added"}


@router.get("/{recipient_id}/local_messages")
async def get_local_conversation_messages(
    recipient_id: str, auth_user: UserAuthentication, session: SessionDep = Depends(get_sessions)
):
    """
    Get conversation messages from local storage between the authenticated user
    and the recipient.
    """
    user_manager = UserManager(session)
    recipient = await user_manager.get_by_id(recipient_id)

    if not recipient:
        raise HTTPException(status_code=404, detail="Recipient not found")

    message_service = MessageService(session)
    messages = await message_service.get_local_conversation_messages(str(auth_user.id), recipient_id)

    return {"messages": [message.model_dump() for message in messages]}
