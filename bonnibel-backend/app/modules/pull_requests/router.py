from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.dependencies.auth import CurrentUserId
from app.dependencies.db import get_db
from app.modules.pull_requests.schemas import PullRequestCreate, PullRequestRead
from app.modules.pull_requests.service import approve_pr, create_pr, decline_pr, list_prs

router = APIRouter(tags=["Pull Requests"])


@router.get("/projects/{project_id}/tasks/{task_id}/pull-requests", response_model=list[PullRequestRead])
def read_pull_requests(
    project_id: int,
    task_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> list[PullRequestRead]:
    return list_prs(db, project_id, task_id)


@router.post(
    "/projects/{project_id}/tasks/{task_id}/pull-requests",
    response_model=PullRequestRead,
    status_code=status.HTTP_201_CREATED,
)
async def open_pull_request(
    project_id: int,
    task_id: int,
    payload: PullRequestCreate,
    current_user_id: CurrentUserId,
    db: Annotated[Session, Depends(get_db)],
) -> PullRequestRead:
    return await create_pr(db, project_id, task_id, payload, current_user_id)


@router.post("/pull-requests/{pr_id}/approve", response_model=PullRequestRead)
async def approve_pull_request(
    pr_id: int,
    current_user_id: CurrentUserId,
    db: Annotated[Session, Depends(get_db)],
) -> PullRequestRead:
    return await approve_pr(db, pr_id, current_user_id)


@router.post("/pull-requests/{pr_id}/decline", response_model=PullRequestRead)
async def decline_pull_request(
    pr_id: int,
    current_user_id: CurrentUserId,
    db: Annotated[Session, Depends(get_db)],
) -> PullRequestRead:
    return await decline_pr(db, pr_id, current_user_id)
