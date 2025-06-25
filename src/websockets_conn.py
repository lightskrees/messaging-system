from dataclasses import dataclass
from typing import Dict

from fastapi import WebSocket


@dataclass
class ConnectionInfo:
    websocket: WebSocket
    active_conversation_with: str | None = None


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Dict[WebSocket, ConnectionInfo]] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = {}
        self.active_connections[user_id][websocket] = ConnectionInfo(websocket=websocket)

    async def set_active_conversation(self, websocket: WebSocket, user_id: str, conversation_with: str):
        if user_id in self.active_connections and websocket in self.active_connections[user_id]:

            self.active_connections[user_id][websocket].active_conversation_with = conversation_with

    async def disconnect(self, websocket: WebSocket, user_id: str):
        if user_id in self.active_connections:
            self.active_connections[user_id].pop(websocket, None)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

    async def send_personal_message(self, message: dict, user_id: str, sender_id: str):
        if user_id in self.active_connections:
            for connection_info in self.active_connections[user_id].values():
                is_active_conversation = connection_info.active_conversation_with == sender_id

                message_with_status = {**message, "is_active_conversation": is_active_conversation}

                await connection_info.websocket.send_json(message_with_status)


manager = ConnectionManager()
