from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.modules.chat.repository import ChatRepository


class ChatService:

    def __init__(self):
        self.repo = ChatRepository()

    async def get_messages(self, db: Session, task_id: int):
        return await self.repo.get_task_messages(db, task_id)

    async def send_message(self, db: Session, task_id: int, author_id: str, text: str):

        message = await self.repo.create(db=db, task_id=task_id, author_id=author_id, text=text,)

        payload = {
            "messageId": message.message_id,
            "taskId": message.task_id,
            "authorId": message.author_id,
            "text": message.text,
            "createdAt": message.created_at.isoformat(),
        }

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

        return {
            "messageId": message.message_id,
            "taskId": message.task_id,
            "authorId": message.author_id,
            "text": message.text,
            "createdAt": message.created_at.isoformat(),
        }

    async def delete_message(self, db: Session, message_id: int, current_user_id: str,):
        message = await self.repo.get_by_id(db, message_id)

        if not message:
            raise HTTPException(404, "Message not found")

        if message.author_id != current_user_id:
            raise HTTPException(403, "Forbidden")

        await self.repo.delete(db, message)