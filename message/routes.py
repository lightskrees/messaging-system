from fastapi import APIRouter, Depends, HTTPException

from src.db_config import SessionDep
from .service import MessageService
from .schemas import MessageCreate, MessageResponse
from src.models import User
from auth.routes import get_current_user

router = APIRouter(prefix="/messages", tags=["messages"])

@router.post("/", response_model=MessageResponse)
async def send_message(
    message_create: MessageCreate,
    session: SessionDep,
    current_user: User = Depends(get_current_user),
):
    message_service = MessageService(session)
    message = await message_service.send_message(
        sender_id=str(current_user.id),
        message_data=message_create
    )
    return message

@router.put("/{message_id}/read")
async def mark_message_as_read(
    message_id: str,
    session : SessionDep,
    _: User = Depends(get_current_user),
):
    message_service = MessageService(session)
    success = await message_service.mark_message_as_read(message_id)
    if not success:
        raise HTTPException(status_code=404, detail="Message not found")
    return {"status": "success"}

@router.delete("/{message_id}")
async def delete_message(
    message_id: str,
    session: SessionDep,
    _: User = Depends(get_current_user),
):
    message_service = MessageService(session)
    success = await message_service.delete_message(message_id)
    if not success:
        raise HTTPException(status_code=404, detail="Message not found")
    return {"status": "success"}