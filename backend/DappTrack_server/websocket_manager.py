from typing import Dict
from fastapi import WebSocket, WebSocketDisconnect

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
       
        self.active_connections[user_id] = websocket
        print("ACTIVE WS:", self.active_connections.keys())

    def disconnect(self, user_id: int):
        self.active_connections.pop(user_id, None)
        print("ACTIVE WS after disconnect:", self.active_connections.keys())

    async def send_personal_message(self, message: str, user_id: int):
        ws = self.active_connections.get(user_id)
        if ws:
            await ws.send_text(message)

    async def broadcast(self, message: str):
        for ws in self.active_connections.values():
            await ws.send_text(message)


manager = ConnectionManager()
