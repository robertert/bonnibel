from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import get_current_user

from app.modules.chat.schemas import SendMessageRequest, UpdateMessageRequest
from app.modules.chat.service import ChatService
from app.modules.notification.manager import chat_manager
from app.core.models import ProjectRole
from app.core.security import RoleChecker

require_owner = RoleChecker([ProjectRole.OWNER])
require_developer_or_owner = RoleChecker([ProjectRole.OWNER, ProjectRole.DEVELOPER])
require_any_member = RoleChecker([ProjectRole.OWNER, ProjectRole.DEVELOPER, ProjectRole.REVIEWER])

router = APIRouter()
service = ChatService()


@router.websocket("/ws/tasks/{task_id}/chat")
async def chat_ws(websocket: WebSocket, task_id: int):
    # Połączenie nasłuchujące — nowe wiadomości są rozgłaszane po POST /messages.
    # Token (?token=) jest opcjonalny; odczyt czatu jest publiczny jak w GET.
    await chat_manager.connect(task_id, websocket)
    try:
        while True:
            # Utrzymujemy połączenie; ewentualne wiadomości od klienta ignorujemy.
            await websocket.receive_text()
    except WebSocketDisconnect:
        chat_manager.disconnect(task_id, websocket)

@router.get("/projects/{project_id}/tasks/{task_id}/messages",)
async def get_messages(project_id: int, task_id: int, db: Session = Depends(get_db),):
    return await service.get_messages(db, task_id)


@router.post("/projects/{project_id}/tasks/{task_id}/messages",)
async def send_message(project_id: int, task_id: int, payload: SendMessageRequest, 
                       db: Session = Depends(get_db), current_user=Depends(get_current_user),):

    return await service.send_message(db=db, task_id=task_id, 
                                      author_id=current_user.user_id, text=payload.text)


@router.patch("/projects/{project_id}/tasks/{task_id}/messages/{message_id}",)
async def update_message(project_id: int, task_id: int, message_id: int, payload: UpdateMessageRequest,
                         db: Session = Depends(get_db), current_user=Depends(get_current_user)):

    return await service.update_message(db=db, message_id=message_id, 
                                        current_user_id=current_user.user_id, text=payload.text,)


@router.delete("/projects/{project_id}/tasks/{task_id}/messages/{message_id}", status_code=204)
async def delete_message(project_id: int, task_id: int, message_id: int, 
                         db: Session = Depends(get_db), current_user=Depends(get_current_user)):

    await service.delete_message(db=db, message_id=message_id, current_user_id=current_user.user_id)