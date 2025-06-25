from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from auth.routes import get_current_user
from message.schemas import MessageResponse
from message.service import MessageService
from src.db_config import SessionDep
from src.models import User

from .manager import ConversationManager
from .schemas import ConversationResponse

router = APIRouter(prefix="/conversations", tags=["conversations"])

# authentication dependency
UserAuthentication = Annotated[User, Depends(get_current_user)]


@router.get("/", response_model=List[ConversationResponse])
async def get_user_conversations(
    session: SessionDep,
    current_user: UserAuthentication,
):
    message_service = MessageService(session)
    conversations = await message_service.get_user_conversations(str(current_user.id))
    return conversations


@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: str,
    session: SessionDep,
    _: UserAuthentication,
):
    message_service = MessageService(session)
    conversation = message_service.get_conversation(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation


@router.get("/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_conversation_messages(
    conversation_id: str,
    session: SessionDep,
    _: UserAuthentication,
):
    message_service = MessageService(session)
    messages = message_service.get_conversation_messages(conversation_id)
    return messages


@router.post("/{conversation_id}/participants", status_code=status.HTTP_200_OK)
async def add_participant(
    conversation_id: str,
    user_id: str,
    session: SessionDep,
    _: User = Depends(get_current_user),
):
    conversation_manager = ConversationManager(session)
    success = await conversation_manager.add_participant(conversation_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Conversation or user not found")
    return {"status": "participant added"}
