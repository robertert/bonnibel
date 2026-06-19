import pytest
from fastapi import HTTPException

from app.core.models import Docs, PullRequest, PullRequestStatus, Task, User
from app.modules.docs.service import MOCK_ACTOR_ID as DOCS_ACTOR_ID
from app.modules.docs.service import DocsService
from app.modules.pr.service import MOCK_ACTOR_ID as PR_ACTOR_ID
from app.modules.pr.service import PullRequestService


def add_docs(db_session):
    return DocsService(db_session).add_task_docs(
        DOCS_ACTOR_ID,
        1,
        1,
        "Task docs",
        "https://docs.example/task-1",
    )


def create_pr(db_session):
    return PullRequestService(db_session).create_pull_request(PR_ACTOR_ID, 1, 1)


def test_create_pr_requires_docs(db_session, seeded_task):
    with pytest.raises(HTTPException) as exc:
        create_pr(db_session)

    assert exc.value.status_code == 409
    assert exc.value.detail["errorCode"] == "TASK_DOCS_REQUIRED"


def test_create_pr_for_task_with_docs(db_session, seeded_task):
    add_docs(db_session)

    pull_request = create_pr(db_session)

    assert pull_request.pull_request_id == 1
    assert pull_request.task_id == seeded_task.task_id
    assert pull_request.external_id == "local-pr-1-1"
    assert pull_request.reviewer_id == "reviewer-1"
    assert pull_request.status.value == "OPEN"


def test_duplicate_pr_returns_conflict(db_session, seeded_task):
    add_docs(db_session)
    create_pr(db_session)

    with pytest.raises(HTTPException) as exc:
        create_pr(db_session)

    assert exc.value.status_code == 409
    assert exc.value.detail["errorCode"] == "PULL_REQUEST_ALREADY_EXISTS"


def test_get_pr_by_id(db_session, seeded_task):
    add_docs(db_session)
    created = create_pr(db_session)

    pull_request = PullRequestService(db_session).get_pull_request(
        PR_ACTOR_ID,
        1,
        created.pull_request_id,
    )

    assert pull_request.external_id == "local-pr-1-1"


def test_get_user_pull_requests_returns_reviewer_and_assignee_prs(db_session, seeded_task):
    other_user = User(
        user_id="other-1",
        email="other@example.com",
        name="Other",
        surname="User",
    )
    assigned_task = Task(
        task_id=2,
        project_id=1,
        title="Assigned task",
        description="Assigned task description",
        assignee_id="reviewer-1",
        reviewer_id="other-1",
    )
    unrelated_task = Task(
        task_id=3,
        project_id=1,
        title="Unrelated task",
        description="Unrelated task description",
        assignee_id="owner-1",
        reviewer_id="other-1",
    )
    db_session.add_all([other_user, assigned_task, unrelated_task])
    db_session.commit()
    db_session.add_all(
        [
            Docs(docs_id=1, task_id=1, title="Docs 1", url="https://docs.example/1"),
            Docs(docs_id=2, task_id=2, title="Docs 2", url="https://docs.example/2"),
            Docs(docs_id=3, task_id=3, title="Docs 3", url="https://docs.example/3"),
            PullRequest(
                pull_request_id=1,
                task_id=1,
                external_id="pr-1",
                title="Reviewer PR",
                url="https://git.example/pr-1",
                reviewer_id="reviewer-1",
                status=PullRequestStatus.OPEN,
            ),
            PullRequest(
                pull_request_id=2,
                task_id=2,
                external_id="pr-2",
                title="Assignee PR",
                url="https://git.example/pr-2",
                reviewer_id="other-1",
                status=PullRequestStatus.OPEN,
            ),
            PullRequest(
                pull_request_id=3,
                task_id=3,
                external_id="pr-3",
                title="Unrelated PR",
                url="https://git.example/pr-3",
                reviewer_id="other-1",
                status=PullRequestStatus.OPEN,
            ),
        ]
    )
    db_session.commit()

    pull_requests = PullRequestService(db_session).get_user_pull_requests(
        PR_ACTOR_ID,
        "reviewer-1",
    )

    assert {pull_request.external_id for pull_request in pull_requests} == {"pr-1", "pr-2"}


def test_accept_open_pr_changes_status_to_merged(db_session, seeded_task):
    add_docs(db_session)
    created = create_pr(db_session)

    pull_request = PullRequestService(db_session).accept_review(
        PR_ACTOR_ID,
        1,
        created.pull_request_id,
    )

    assert pull_request.status.value == "MERGED"


def test_reject_open_pr_changes_status_to_closed(db_session, seeded_task):
    add_docs(db_session)
    created = create_pr(db_session)

    pull_request = PullRequestService(db_session).reject_review(
        PR_ACTOR_ID,
        1,
        created.pull_request_id,
        "Needs changes",
    )

    assert pull_request.status.value == "CLOSED"


def test_accept_non_open_pr_returns_conflict(db_session, seeded_task):
    add_docs(db_session)
    created = create_pr(db_session)
    service = PullRequestService(db_session)
    service.accept_review(PR_ACTOR_ID, 1, created.pull_request_id)

    with pytest.raises(HTTPException) as exc:
        service.accept_review(PR_ACTOR_ID, 1, created.pull_request_id)

    assert exc.value.status_code == 409
    assert exc.value.detail["errorCode"] == "PULL_REQUEST_NOT_OPEN"


def test_reject_non_open_pr_returns_conflict(db_session, seeded_task):
    add_docs(db_session)
    created = create_pr(db_session)
    service = PullRequestService(db_session)
    service.reject_review(PR_ACTOR_ID, 1, created.pull_request_id, "No")

    with pytest.raises(HTTPException) as exc:
        service.reject_review(PR_ACTOR_ID, 1, created.pull_request_id, "Still no")

    assert exc.value.status_code == 409
    assert exc.value.detail["errorCode"] == "PULL_REQUEST_NOT_OPEN"
