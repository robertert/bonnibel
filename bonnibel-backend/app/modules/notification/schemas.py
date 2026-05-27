from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.modules.notification.models import NotificationType


class CamelModel(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class NotificationRead(CamelModel):
    notification_id: int = Field(alias="notificationId")
    user_id: str = Field(alias="userId")
    type: NotificationType
    title: str
    message: str
    link_url: str | None = Field(alias="linkUrl")
    is_read: bool = Field(alias="isRead")
    is_delivered: bool = Field(alias="isDelivered")
    created_at: datetime = Field(alias="createdAt")


class ChatMessageRead(CamelModel):
    message_id: int = Field(alias="messageId")
    task_id: int = Field(alias="taskId")
    author_id: str = Field(alias="authorId")
    text: str
    created_at: datetime = Field(alias="createdAt")


class ChatMessageCreate(BaseModel):
    text: str = Field(min_length=1, max_length=4000)


class TaskSubscriptionRead(CamelModel):
    task_id: int = Field(alias="taskId")
    user_id: str = Field(alias="userId")
    created_at: datetime = Field(alias="createdAt")


class NotificationEventCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    type: NotificationType
    task_id: int | None = None
    project_id: int | None = None
    actor_id: str | None = None
    owner_id: str | None = None
    assignee_id: str | None = None
    reviewer_id: str | None = None
    title: str | None = None
    message: str | None = None
    link_url: str | None = None
    recipient_ids: list[str] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def accept_camel_case(cls, data):
        if not isinstance(data, dict):
            return data
        aliases = {
            "taskId": "task_id",
            "projectId": "project_id",
            "actorId": "actor_id",
            "ownerId": "owner_id",
            "assigneeId": "assignee_id",
            "reviewerId": "reviewer_id",
            "linkUrl": "link_url",
            "recipientIds": "recipient_ids",
        }
        return {aliases.get(key, key): value for key, value in data.items()}


class TaskRecipientSnapshotUpsert(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    task_id: int
    project_id: int | None = None
    owner_id: str | None = None
    assignee_id: str | None = None
    reviewer_id: str | None = None
    title: str | None = None

    @model_validator(mode="before")
    @classmethod
    def accept_camel_case(cls, data):
        if not isinstance(data, dict):
            return data
        aliases = {
            "taskId": "task_id",
            "projectId": "project_id",
            "ownerId": "owner_id",
            "assigneeId": "assignee_id",
            "reviewerId": "reviewer_id",
        }
        return {aliases.get(key, key): value for key, value in data.items()}


class UnreadCountRead(BaseModel):
    unread_count: int = Field(alias="unreadCount")


class WebSocketEvent(BaseModel):
    event: str
    data: dict
