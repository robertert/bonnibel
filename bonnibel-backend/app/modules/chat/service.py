from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.models import NotificationType, Task, User
from app.modules.chat.repository import ChatRepository
from app.modules.notification.manager import chat_manager, notification_service
from app.modules.notification.schemas import NotificationEventCreate


class ChatService:

    def __init__(self):
        self.repo = ChatRepository()

    def _author_emails(self, db: Session, author_ids) -> dict[str, str]:
        ids = {aid for aid in author_ids if aid}
        if not ids:
            return {}
        rows = db.query(User.user_id, User.email).filter(User.user_id.in_(ids)).all()
        return {user_id: email for user_id, email in rows}

    def _serialize(self, message, email: str | None):
        return {
            "messageId": message.message_id,
            "taskId": message.task_id,
            "authorId": message.author_id,
            "authorEmail": email,
            "text": message.text,
            "createdAt": message.created_at.isoformat(),
        }

    async def get_messages(self, db: Session, task_id: int):
        messages = await self.repo.get_task_messages(db, task_id)
        emails = self._author_emails(db, (m.author_id for m in messages))
        return [self._serialize(m, emails.get(m.author_id)) for m in messages]

    async def send_message(self, db: Session, task_id: int, author_id: str, text: str):
        message = await self.repo.create(db=db, task_id=task_id, author_id=author_id, text=text,)
        emails = self._author_emails(db, [author_id])
        payload = self._serialize(message, emails.get(author_id))
        # Rozgłoś nową wiadomość do wszystkich nasłuchujących WS na tym zadaniu.
        await chat_manager.broadcast(task_id, {"type": "created", "message": payload})
        # Powiadom obserwatorów zadania (autor jest wykluczony przez resolver).
        task = db.get(Task, task_id)
        event = NotificationEventCreate(
            type=NotificationType.CHAT_MESSAGE,
            task_id=task_id,
            project_id=task.project_id if task else None,
            actor_id=author_id,
            title="Nowa wiadomość",
            message=f"Nowa wiadomość w zadaniu #{task_id}",
            link_url=f"/projects/{task.project_id}/tasks/{task_id}" if task else f"/tasks/{task_id}",
        )
        try:
            await notification_service.create_from_event(db, event)
        except Exception:
            # Powiadomienie jest best-effort — nie blokuj wysłania wiadomości.
            pass
        return payload

    async def update_message(self, db: Session, message_id: int, current_user_id: str, text: str,):
        message = await self.repo.get_by_id(db, message_id)

        if not message:
            raise HTTPException(404, "Message not found")

        if message.author_id != current_user_id:
            raise HTTPException(403, "Forbidden")

        message.text = text

        db.commit()
        db.refresh(message)

        emails = self._author_emails(db, [message.author_id])
        payload = self._serialize(message, emails.get(message.author_id))
        await chat_manager.broadcast(message.task_id, {"type": "updated", "message": payload})
        return payload

    async def delete_message(self, db: Session, message_id: int, current_user_id: str,):
        message = await self.repo.get_by_id(db, message_id)

        if not message:
            raise HTTPException(404, "Message not found")

        if message.author_id != current_user_id:
            raise HTTPException(403, "Forbidden")

        task_id = message.task_id
        await self.repo.delete(db, message)
        await chat_manager.broadcast(task_id, {"type": "deleted", "messageId": message_id})
