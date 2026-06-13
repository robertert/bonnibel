from pydantic import BaseModel, ConfigDict, Field

from app.core.models import TaskEventType


class TaskHistoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    event_id: int = Field(alias="eventId")
    task_id: int = Field(alias="taskId")
    type: TaskEventType
    actor_id: str = Field(alias="actorId")
    title: str
    description: str | None = None
    url: str | None = None
