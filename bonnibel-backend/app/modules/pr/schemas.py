from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class PullRequestResponse(BaseModel):
    pullRequestId: int
    taskId: int
    externalId: str
    title: str
    url: str
    reviewerId: Optional[str] = None
    status: str
    createdAt: datetime
    updatedAt: Optional[datetime] = None
    mergedAt: Optional[datetime] = None


class RejectReviewRequest(BaseModel):
    reason: str = Field(min_length=1)

