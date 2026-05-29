from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.models import User
from app.modules.chat.repository import ChatRepository


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
        return self._serialize(message, emails.get(author_id))

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
        return self._serialize(message, emails.get(message.author_id))

    async def delete_message(self, db: Session, message_id: int, current_user_id: str,):
        message = await self.repo.get_by_id(db, message_id)

        if not message:
            raise HTTPException(404, "Message not found")

        if message.author_id != current_user_id:
            raise HTTPException(403, "Forbidden")

        await self.repo.delete(db, message)
