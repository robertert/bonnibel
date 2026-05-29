from datetime import datetime
from pydantic import BaseModel, ConfigDict


class SendMessageRequest(BaseModel):
    text: str


class UpdateMessageRequest(BaseModel):
    text: str


class ChatMessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    messageId: int
    taskId: int
    authorId: str
    authorEmail: str | None = None
    text: str
    createdAt: datetime