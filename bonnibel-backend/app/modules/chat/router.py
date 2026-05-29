from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import get_current_user

from app.modules.chat.schemas import SendMessageRequest, UpdateMessageRequest
from app.modules.chat.service import ChatService

router = APIRouter()
service = ChatService()

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