from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from app.core.security import decode_access_token
from app.modules.notification.manager import connection_manager

router = APIRouter(tags=["notifications"])


@router.websocket("/ws/notifications")
async def notifications_websocket(
    websocket: WebSocket,
    token: str | None = Query(default=None),
    user_id: str | None = Query(default=None, alias="userId"),
) -> None:
    authenticated_user_id = decode_access_token(token) if token else None
    authenticated_user_id = authenticated_user_id or user_id

    if not authenticated_user_id:
        await websocket.close(code=1008)
        return

    await connection_manager.connect(authenticated_user_id, websocket)
    try:
        await websocket.send_json({"event": "connected", "data": {"userId": authenticated_user_id}})
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        connection_manager.disconnect(authenticated_user_id, websocket)
