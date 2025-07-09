from datetime import datetime
from typing import Annotated

from fastapi import (APIRouter, Depends, HTTPException, WebSocket,
                     WebSocketDisconnect, status)

from auth.manager import UserManager
from auth.routes import decode_token, get_current_user
from src.db_config import SessionDep, get_sessions
from src.models import User
from src.websockets_conn import manager

from .schemas import MessageCreate, MessageResponse
from .service import MessageService

router = APIRouter(prefix="/messages", tags=["messages"])

SessionDep = Annotated[SessionDep, Depends(get_sessions)]


@router.websocket("/")
async def websocket_endpoint(websocket: WebSocket, session: SessionDep):
    print("in websocket endpoint")
    token_data = decode_token(websocket.headers.get("Authorization"))
    if not token_data:
        print("no token data")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    user_manager = UserManager(session)

    username = token_data.get("sub")
    user_obj = await user_manager.get_by_username(username)

    user_id = str(user_obj.id)

    await manager.connect(websocket, str(user_id))

    try:
        while True:
            await websocket.receive_json()

            # Send confirmation back to the sender
            await websocket.send_text("message sent!")

    except WebSocketDisconnect:
        await manager.disconnect(websocket, user_id)
    except Exception as e:
        print(f"WebSocket error: {e}")
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR)


# @router.websocket("/ws/{conversation_with}/")
# async def websocket_endpoint(
#     websocket: WebSocket,
#     conversation_with: str,
#     session: SessionDep,
# ):
#     # if str(current_user.id) != user_id:
#     #     await websocket.close(code=4003)
#     #     return
#     token_data = decode_token(websocket.headers.get("Authorization"))
#     if not token_data:
#         print("no token data")
#         await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
#         return
#
#     user_manager = UserManager(session)
#
#     username = token_data.get("sub")
#     user_obj = await user_manager.get_by_username(username)
#
#     user_id = str(user_obj.id)
#
#     await manager.connect(websocket, user_id)
#     await websocket.send_text("connected")
#     try:
#         while True:
#             await websocket.receive_json()
#             await manager.set_active_conversation(websocket, user_id, conversation_with)
#     except WebSocketDisconnect:
#         await manager.disconnect(websocket, user_id)


# @router.post("/", response_model=MessageResponse)
# async def send_message(
#     message_create: MessageCreate,
#     session: SessionDep,
#     current_user: User = Depends(get_current_user),
# ):
#     message_service = MessageService(session)
#     message = await message_service.send_message(sender_id=str(current_user.id), message_data=message_create)
#     return message


@router.post("/send_message/", response_model=MessageResponse)
async def send_message(
    message_create: MessageCreate,
    session: SessionDep,
    current_user: User = Depends(get_current_user),
):
    user_manager = UserManager(session)

    connected_userkey = await user_manager.get_user_key(current_user.id)

    if not connected_userkey:
        raise HTTPException(
            status_code=404,
            detail="Something is wrong with your account settings. Please contact support.",
        )

    recipient_key = await user_manager.get_user_key(message_create.recipient_id)
    if not recipient_key:
        raise HTTPException(
            status_code=404,
            detail="the user does not use our messaging system.",
        )

    message_service = MessageService(session)
    message = await message_service.send_message(sender_id=str(current_user.id), message_data=message_create)

    message_payload = {
        "type": "new_message",
        "data": {
            # "id": str(message.id),
            "content": str(message_create.content),
            "sender_id": str(current_user.id),
            "recipient_id": str(message.recipient_id),
            "created_at": (
                message.created_at.isoformat() if hasattr(message, "created_at") else datetime.now().isoformat()
            ),
        },
    }

    try:
        await manager.send_personal_message(
            message=message_payload, user_id=str(message.recipient_id), sender_id=str(current_user.id)
        )
    except Exception as e:
        print(f"Error sending WebSocket message: {e}")

    return message


@router.put("/{message_id}/read")
async def mark_message_as_read(
    message_id: str,
    session: SessionDep,
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
