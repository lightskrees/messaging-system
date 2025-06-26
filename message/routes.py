from datetime import datetime

from fastapi import (APIRouter, Depends, HTTPException, WebSocket,
                     WebSocketDisconnect, status)

from auth.manager import UserManager
from auth.routes import decode_token, get_current_user
from src.db_config import SessionDep
from src.models import User
from src.websockets_conn import manager

from .schemas import MessageCreate, MessageResponse
from .service import MessageService

router = APIRouter(prefix="/messages", tags=["messages"])


@router.websocket("/{conversation_with}")
async def websocket_endpoint(websocket: WebSocket, conversation_with: str, session: SessionDep):
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
            data = await websocket.receive_json()

            message_service = MessageService(session)

            message_create = MessageCreate(
                message_type=data.get("message_type"),
                content=data.get("content"),
                recipient_id=conversation_with,
                image_url=data.get("image_url"),
                image_filename=data.get("image_filename"),
                image_size=data.get("image_size"),
                file_url=data.get("file_url"),
                file_filename=data.get("file_filename"),
                file_size=data.get("file_size"),
                file_mime_type=data.get("file_mime_type"),
                voice_url=data.get("voice_url"),
                voice_filename=data.get("voice_filename"),
            )

            message = await message_service.send_message(sender_id=str(user_id), message_data=message_create)

            message_payload = {
                "type": "new_message",
                "data": {
                    "content": str(message_create.content),
                    "sender_id": str(user_id),
                    "recipient_id": str(message_create.recipient_id),
                    "created_at": (
                        message.created_at.isoformat()
                        if hasattr(message, "created_at")
                        else datetime.now().isoformat()
                    ),
                },
            }

            await manager.send_personal_message(
                message=message_payload, user_id=str(message.recipient_id), sender_id=str(user_id)
            )

            # Send confirmation back to sender
            await websocket.send_json({"type": "message_sent", "data": message_payload})

    except WebSocketDisconnect:
        manager.disconnect(str(user_obj.id))
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
    message_service = MessageService(session)
    message = await message_service.send_message(sender_id=str(current_user.id), message_data=message_create)

    message_payload = {
        "type": "new_message",
        "data": {
            # "id": str(message.id),
            "content": str(message.content),
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
