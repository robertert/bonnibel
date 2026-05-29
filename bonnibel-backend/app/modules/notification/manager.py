from collections import defaultdict

from fastapi import WebSocket


class ChatConnectionManager:
    """Trzyma aktywne połączenia WebSocket pogrupowane po task_id."""

    def __init__(self) -> None:
        self._rooms: dict[int, list[WebSocket]] = defaultdict(list)

    async def connect(self, task_id: int, websocket: WebSocket) -> None:
        await websocket.accept()
        self._rooms[task_id].append(websocket)

    def disconnect(self, task_id: int, websocket: WebSocket) -> None:
        room = self._rooms.get(task_id)
        if not room:
            return
        if websocket in room:
            room.remove(websocket)
        if not room:
            self._rooms.pop(task_id, None)

    async def broadcast(self, task_id: int, payload: dict) -> None:
        for websocket in list(self._rooms.get(task_id, [])):
            try:
                await websocket.send_json(payload)
            except Exception:
                # Połączenie padło w trakcie wysyłki — sprzątamy.
                self.disconnect(task_id, websocket)


# Singleton współdzielony przez router WS i ChatService.
chat_manager = ChatConnectionManager()
