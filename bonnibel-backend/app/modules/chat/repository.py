from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.models import ChatMessage


class ChatRepository:
    async def create(self, db: Session, task_id: int, author_id: str, text: str,) -> ChatMessage:
        message = ChatMessage(task_id=task_id, author_id=author_id, text=text)
        db.add(message)
        db.commit()
        db.refresh(message)
        return message

    async def get_task_messages(self, db: Session, task_id: int,) -> list[ChatMessage]:
        query = (select(ChatMessage).where(ChatMessage.task_id == task_id)
                 .order_by(ChatMessage.created_at.asc()))

        result = db.execute(query)
        return list(result.scalars().all())

    async def get_by_id(self, db: Session, message_id: int,) -> ChatMessage | None:
        query = (select(ChatMessage).where(ChatMessage.message_id == message_id))
        result = db.execute(query)

        return result.scalar_one_or_none()

    async def delete(self, db: Session, message: ChatMessage,):
        db.delete(message)
        db.commit()