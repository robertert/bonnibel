from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.core.models import NotificationType


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
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "text": "Hej, wrzuciłem zmiany do review. Możesz zerknąć?",
                }
            ]
        }
    )

    text: str = Field(min_length=1, max_length=4000)


class TaskSubscriptionRead(CamelModel):
    task_id: int = Field(alias="taskId")
    user_id: str = Field(alias="userId")
    created_at: datetime = Field(alias="createdAt")


class NotificationEventCreate(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "examples": [
                {
                    "type": "TASK_UPDATED",
                    "taskId": 102,
                    "projectId": 1,
                    "actorId": "user-1",
                    "title": "Zmieniono status zadania",
                    "message": "Zadanie BON-102 przeszło do review.",
                    "linkUrl": "/projects/1/tasks/102",
                },
                {
                    "type": "PR_CREATED",
                    "taskId": 102,
                    "projectId": 1,
                    "actorId": "user-2",
                    "ownerId": "user-1",
                    "assigneeId": "user-2",
                    "reviewerId": "user-1",
                    "title": "Utworzono pull request",
                    "message": "Użytkownik user-2 utworzył PR dla zadania BON-102.",
                    "linkUrl": "/projects/1/tasks/102",
                },
                {
                    "type": "PR_REVIEWED",
                    "taskId": 102,
                    "projectId": 1,
                    "actorId": "user-1",
                    "ownerId": "user-1",
                    "assigneeId": "user-2",
                    "title": "Review zaakceptowane",
                    "message": "Pull request dla BON-102 został zaakceptowany.",
                    "linkUrl": "/projects/1/tasks/102",
                },
                {
                    "type": "TASK_ASSIGNED",
                    "taskId": 103,
                    "projectId": 1,
                    "actorId": "user-1",
                    "assigneeId": "user-3",
                    "reviewerId": "user-1",
                    "title": "Przypisano zadanie",
                    "message": "Zadanie BON-103 zostało przypisane do user-3.",
                    "linkUrl": "/projects/1/tasks/103",
                },
                {
                    "type": "CHAT_MESSAGE",
                    "taskId": 102,
                    "projectId": 1,
                    "actorId": "user-2",
                    "recipientIds": ["user-1", "user-3"],
                    "title": "Nowa wiadomość",
                    "message": "Użytkownik user-2 dodał wiadomość do zadania BON-102.",
                    "linkUrl": "/projects/1/tasks/102",
                },
            ]
        },
    )

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
    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "examples": [
                {
                    "taskId": 103,
                    "projectId": 1,
                    "ownerId": "user-1",
                    "assigneeId": "user-3",
                    "reviewerId": "user-1",
                    "title": "Stworzenie widoku Tablicy Zadań",
                },
                {
                    "taskId": 102,
                    "projectId": 1,
                    "ownerId": "user-1",
                    "assigneeId": "user-2",
                    "reviewerId": "user-1",
                    "title": "Integracja Auth Module z frontendem",
                },
            ]
        },
    )

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
