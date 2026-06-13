from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from app.core.database import SessionLocal
from app.core.models import User
from app.core.security import decode_access_token
from app.modules.notification.manager import connection_manager

router = APIRouter(tags=["notifications"])


def _set_online(user_id: str, online: bool) -> None:
    """Utrwala status online użytkownika w bazie (presence)."""
    with SessionLocal() as db:
        user = db.get(User, user_id)
        if user is not None:
            user.is_online = online
            db.commit()


@router.websocket("/ws/notifications")
async def notifications_websocket(
    websocket: WebSocket,
    token: str | None = Query(default=None),
    user_id: str | None = Query(default=None, alias="userId"),
) -> None:
    authenticated_user_id = None
    if token:
        try:
            authenticated_user_id = decode_access_token(token).get("sub")
        except Exception:
            authenticated_user_id = None
    authenticated_user_id = authenticated_user_id or user_id

    if not authenticated_user_id:
        await websocket.close(code=1008)
        return

    await connection_manager.connect(authenticated_user_id, websocket)
    _set_online(authenticated_user_id, True)
    try:
        await websocket.send_json({"event": "connected", "data": {"userId": authenticated_user_id}})
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        connection_manager.disconnect(authenticated_user_id, websocket)
        if not connection_manager.is_online(authenticated_user_id):
            _set_online(authenticated_user_id, False)
