from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from typing import Optional

from app.core.models import PullRequest, PullRequestStatus
from app.modules.pr.schemas import PullRequestResponse, RejectReviewRequest
from app.modules.pr.service import MOCK_ACTOR_ID, PullRequestService

router = APIRouter()


def to_response(pull_request: PullRequest) -> PullRequestResponse:
    return to_response_with_context(pull_request, None)


def to_response_with_context(pull_request: PullRequest, task) -> PullRequestResponse:
    return PullRequestResponse(
        pullRequestId=pull_request.pull_request_id,
        projectId=task.project_id if task else None,
        taskId=pull_request.task_id,
        externalId=pull_request.external_id,
        title=pull_request.title,
        url=pull_request.url,
        assigneeId=task.assignee_id if task else None,
        reviewerId=pull_request.reviewer_id,
        status=pull_request.status.value,
        createdAt=pull_request.created_at,
        updatedAt=pull_request.updated_at,
        mergedAt=pull_request.merged_at,
    )


@router.post(
    "/projects/{projectId}/tasks/{taskId}/pull-requests",
    response_model=PullRequestResponse,
    status_code=201,
)
async def create_pull_request(projectId: int, taskId: int, db: Session = Depends(get_db)):
    pull_request = PullRequestService(db).create_pull_request(MOCK_ACTOR_ID, projectId, taskId)
    return to_response(pull_request)


@router.get(
    "/projects/{projectId}/pull-requests/{pullRequestId}",
    response_model=PullRequestResponse,
)
async def get_pull_request(projectId: int, pullRequestId: int, db: Session = Depends(get_db)):
    pull_request = PullRequestService(db).get_pull_request(
        MOCK_ACTOR_ID,
        projectId,
        pullRequestId,
    )
    return to_response(pull_request)


@router.get("/projects/{projectId}/pull-requests", response_model=list[PullRequestResponse])
async def get_project_pull_requests(
    projectId: int,
    reviewerId: Optional[str] = None,
    status: Optional[PullRequestStatus] = None,
    db: Session = Depends(get_db),
):
    pull_requests = PullRequestService(db).get_project_pull_requests(
        MOCK_ACTOR_ID,
        projectId,
        reviewer_id=reviewerId,
        pr_status=status,
    )
    return [to_response(pull_request) for pull_request in pull_requests]


@router.get("/users/{userId}/pull-requests", response_model=list[PullRequestResponse])
async def get_user_pull_requests(
    userId: str,
    status: Optional[PullRequestStatus] = None,
    mode: Optional[str] = None,
    db: Session = Depends(get_db),
):
    service = PullRequestService(db)
    if mode == "reviews":
        pull_requests = service.get_reviews_scope_pull_requests(
            MOCK_ACTOR_ID,
            userId,
            pr_status=status,
        )
    else:
        pull_requests = service.get_user_pull_requests(MOCK_ACTOR_ID, userId)
        if status is not None:
            pull_requests = [
                pull_request
                for pull_request in pull_requests
                if pull_request.status == status
            ]

    return [
        to_response_with_context(pull_request, service.get_task_context(pull_request.task_id))
        for pull_request in pull_requests
    ]


@router.post(
    "/projects/{projectId}/pull-requests/{pullRequestId}/accept",
    response_model=PullRequestResponse,
)
async def accept_review(projectId: int, pullRequestId: int, db: Session = Depends(get_db)):
    pull_request = PullRequestService(db).accept_review(MOCK_ACTOR_ID, projectId, pullRequestId)
    return to_response(pull_request)


@router.post(
    "/projects/{projectId}/pull-requests/{pullRequestId}/reject",
    response_model=PullRequestResponse,
)
async def reject_review(
    projectId: int,
    pullRequestId: int,
    reject_in: RejectReviewRequest,
    db: Session = Depends(get_db),
):
    pull_request = PullRequestService(db).reject_review(
        MOCK_ACTOR_ID,
        projectId,
        pullRequestId,
        reject_in.reason,
    )
    return to_response(pull_request)
