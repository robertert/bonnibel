from pydantic import BaseModel, ConfigDict, Field


class WebhookEvent(BaseModel):
    """Uproszczony payload webhooka przetwarzany po weryfikacji podpisu."""

    model_config = ConfigDict(populate_by_name=True)

    task_id: int | None = Field(default=None, alias="taskId")
    type: str | None = None
    title: str | None = None
    message: str | None = None
