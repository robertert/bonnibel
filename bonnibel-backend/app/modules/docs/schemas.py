from typing import Optional

from pydantic import BaseModel, Field


class DocsCreate(BaseModel):
    title: str = Field(min_length=1)
    url: str = Field(min_length=1)


class DocsResponse(BaseModel):
    docsId: int
    taskId: int
    title: str
    url: str
    externalId: Optional[str] = None

