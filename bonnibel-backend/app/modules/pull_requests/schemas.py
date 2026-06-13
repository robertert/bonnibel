from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.core.models import PullRequestStatus


class PullRequestCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    source_branch: str | None = Field(default=None, alias="sourceBranch")
    target_branch: str = Field(default="main", alias="targetBranch")
    reviewer_id: str | None = Field(default=None, alias="reviewerId")


class PullRequestRead(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    pull_request_id: int = Field(alias="pullRequestId")
    task_id: int = Field(alias="taskId")
    external_id: str = Field(alias="externalId")
    title: str
    url: str
    reviewer_id: str | None = Field(default=None, alias="reviewerId")
    status: PullRequestStatus
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    merged_at: datetime | None = Field(default=None, alias="mergedAt")
