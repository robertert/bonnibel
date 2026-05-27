from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    userId: str
    email: str
    name: str
    surname: str
    status: str
    isOnline: bool


class UpdateProfileRequest(BaseModel):
    email: str
    name: str
    surname: str


class UpdateStatusRequest(BaseModel):
    status: str


class TaskOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    taskId: int
    projectId: int
    title: str
    description: str
    status: str
    assigneeId: str | None
    reviewerId: str | None
    gitBranchName: str | None
    jiraIssueKey: str | None
    createdAt: datetime
    updatedAt: datetime
    closedAt: datetime | None


class CreateTaskRequest(BaseModel):
    title: str
    description: str
    assigneeId: str | None = None
    reviewerId: str | None = None


class UpdateTaskStatusRequest(BaseModel):
    status: str
    updatedAt: datetime | None = None


class UpdateTaskAssigneeRequest(BaseModel):
    assigneeId: str | None = None
    updatedAt: datetime | None = None


class UpdateTaskReviewerRequest(BaseModel):
    reviewerId: str | None = None
    updatedAt: datetime | None = None
