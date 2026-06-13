from pydantic import BaseModel, ConfigDict, Field


class DocCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    title: str = Field(min_length=1, max_length=255)
    url: str | None = None
    content: str | None = None


class DocRead(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    docs_id: int = Field(alias="docsId")
    task_id: int = Field(alias="taskId")
    title: str
    url: str
    external_id: str | None = Field(default=None, alias="externalId")
