from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.models import PullRequest
from app.modules.pr.schemas import PullRequestResponse, RejectReviewRequest
from app.modules.pr.service import MOCK_ACTOR_ID, PullRequestService

router = APIRouter()


def to_response(pull_request: PullRequest) -> PullRequestResponse:
    return PullRequestResponse(
        pullRequestId=pull_request.pull_request_id,
        taskId=pull_request.task_id,
        externalId=pull_request.external_id,
        title=pull_request.title,
        url=pull_request.url,
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


@router.get("/users/{userId}/pull-requests", response_model=list[PullRequestResponse])
async def get_user_pull_requests(userId: str, db: Session = Depends(get_db)):
    pull_requests = PullRequestService(db).get_user_pull_requests(MOCK_ACTOR_ID, userId)
    return [to_response(pull_request) for pull_request in pull_requests]


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
