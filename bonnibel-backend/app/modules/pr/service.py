from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.models import PullRequest, PullRequestStatus
from app.modules.docs.service import DocsService, api_error
from app.modules.pr.repository import PullRequestRepository, TaskLookupRepository

MOCK_ACTOR_ID = "mock-user"


@dataclass(frozen=True)
class GitPullRequestRef:
    pull_request_external_id: str
    task_id: int
    reviewer_id: Optional[str]
    status: PullRequestStatus
    title: str
    url: str
    created_at: datetime
    updated_at: datetime


class MockGitIntegrationClient:
    def create_pull_request(
        self,
        project_id: int,
        task_id: int,
        title: str,
        description: str,
        source_branch: str,
        target_branch: str,
        reviewer_id: Optional[str],
    ) -> GitPullRequestRef:
        now = datetime.utcnow()
        external_id = f"mock-pr-{project_id}-{task_id}"
        return GitPullRequestRef(
            pull_request_external_id=external_id,
            task_id=task_id,
            reviewer_id=reviewer_id,
            status=PullRequestStatus.OPEN,
            title=title,
            url=f"https://mock.git.local/projects/{project_id}/pull-requests/{external_id}",
            created_at=now,
            updated_at=now,
        )

    def merge_pull_request(self, project_id: int, pull_request_external_id: str) -> None:
        return None


class MockJiraIntegrationClient:
    def move_ticket_to_done(self, project_id: int, jira_ticket_key: Optional[str]) -> None:
        return None


class MockRoleService:
    def require_permission(self, *_args, **_kwargs) -> None:
        return None


class MockTaskHistoryService:
    def add_history(self, *_args, **_kwargs) -> None:
        return None


class MockNotificationService:
    def notify(self, *_args, **_kwargs) -> None:
        return None


class PullRequestService:
    def __init__(self, db: Session):
        self.pull_request_repository = PullRequestRepository(db)
        self.task_repository = TaskLookupRepository(db)
        self.docs_service = DocsService(db)
        self.role_service = MockRoleService()
        self.task_history_service = MockTaskHistoryService()
        self.notification_service = MockNotificationService()
        self.git_client = MockGitIntegrationClient()
        self.jira_client = MockJiraIntegrationClient()

    def create_pull_request(self, actor_id: str, project_id: int, task_id: int) -> PullRequest:
        self.role_service.require_permission(actor_id, project_id, "REVIEW_TASK")
        task = self.task_repository.find_by_project_and_id(project_id, task_id)
        if task is None:
            raise api_error(status.HTTP_404_NOT_FOUND, "TASK_NOT_FOUND", "Task was not found")
        self.docs_service.require_task_has_docs(task_id)
        if self.pull_request_repository.find_by_task_id(task_id) is not None:
            raise api_error(
                status.HTTP_409_CONFLICT,
                "PULL_REQUEST_ALREADY_EXISTS",
                "Pull request already exists for this task",
            )

        title = f"PR for task {task.task_id}: {task.title}"
        source_branch = task.git_branch_name or f"task-{task.task_id}"
        pr_ref = self.git_client.create_pull_request(
            project_id=project_id,
            task_id=task_id,
            title=title,
            description=task.description or "",
            source_branch=source_branch,
            target_branch="main",
            reviewer_id=task.reviewer_id,
        )
        pull_request = PullRequest(
            task_id=task_id,
            external_id=pr_ref.pull_request_external_id,
            title=pr_ref.title,
            url=pr_ref.url,
            reviewer_id=pr_ref.reviewer_id,
            status=pr_ref.status,
            created_at=pr_ref.created_at,
            updated_at=pr_ref.updated_at,
        )
        saved = self.pull_request_repository.save(pull_request)
        self.task_history_service.add_history(task_id, actor_id, "PULL_REQUEST_CREATED", title, saved.url)
        self.notification_service.notify("PULL_REQUEST_CREATED", task_id)
        return saved

    def get_pull_request(
        self,
        actor_id: str,
        project_id: int,
        pull_request_id: int,
    ) -> PullRequest:
        self.role_service.require_permission(actor_id, project_id, "VIEW_PROJECT_TASKS")
        pull_request = self.pull_request_repository.find_by_project_and_id(
            project_id,
            pull_request_id,
        )
        if pull_request is None:
            raise api_error(
                status.HTTP_404_NOT_FOUND,
                "PULL_REQUEST_NOT_FOUND",
                "Pull request was not found",
            )
        return pull_request

    def get_user_pull_requests(self, actor_id: str, user_id: str) -> list[PullRequest]:
        self.role_service.require_permission(actor_id, None, "VIEW_PROJECT_TASKS")
        return self.pull_request_repository.find_by_user_id(user_id)

    def get_project_pull_requests(
        self,
        actor_id: str,
        project_id: int,
        reviewer_id: Optional[str] = None,
        pr_status: Optional[PullRequestStatus] = None,
    ) -> list[PullRequest]:
        self.role_service.require_permission(actor_id, project_id, "VIEW_PROJECT_TASKS")
        return self.pull_request_repository.find_by_project(project_id, reviewer_id, pr_status)

    def get_reviews_scope_pull_requests(
        self,
        actor_id: str,
        user_id: str,
        pr_status: Optional[PullRequestStatus] = None,
    ) -> list[PullRequest]:
        self.role_service.require_permission(actor_id, None, "VIEW_PROJECT_TASKS")
        return self.pull_request_repository.find_for_reviews_scope(user_id, pr_status)

    def get_task_context(self, task_id: int):
        return self.task_repository.find_by_id(task_id)

    def accept_review(
        self,
        reviewer_id: str,
        project_id: int,
        pull_request_id: int,
    ) -> PullRequest:
        pull_request = self.get_pull_request(reviewer_id, project_id, pull_request_id)
        if pull_request.status != PullRequestStatus.OPEN:
            raise api_error(
                status.HTTP_409_CONFLICT,
                "PULL_REQUEST_NOT_OPEN",
                "Pull request is not open",
            )
        task = self.task_repository.find_by_project_and_id(project_id, pull_request.task_id)
        self.git_client.merge_pull_request(project_id, pull_request.external_id)
        self.jira_client.move_ticket_to_done(project_id, task.jira_issue_key if task else None)
        pull_request.status = PullRequestStatus.APPROVED
        pull_request.updated_at = datetime.utcnow()
        return self.pull_request_repository.save(pull_request)

    def reject_review(
        self,
        reviewer_id: str,
        project_id: int,
        pull_request_id: int,
        reason: str,
    ) -> PullRequest:
        pull_request = self.get_pull_request(reviewer_id, project_id, pull_request_id)
        if pull_request.status != PullRequestStatus.OPEN:
            raise api_error(
                status.HTTP_409_CONFLICT,
                "PULL_REQUEST_NOT_OPEN",
                "Pull request is not open",
            )
        pull_request.status = PullRequestStatus.REJECTED
        pull_request.updated_at = datetime.utcnow()
        saved = self.pull_request_repository.save(pull_request)
        self.task_history_service.add_history(
            pull_request.task_id,
            reviewer_id,
            "PULL_REQUEST_REJECTED",
            "Review rejected",
            reason,
        )
        return saved

    def apply_git_pull_request_created(self, event) -> PullRequest:
        existing = self.pull_request_repository.find_by_external_id(
            event.project_id,
            event.external_id,
        )
        if existing is not None:
            return existing
        pull_request = PullRequest(
            task_id=event.task_id,
            external_id=event.external_id,
            title=event.title,
            url=event.url,
            reviewer_id=getattr(event, "reviewer_id", None),
            status=PullRequestStatus.OPEN,
        )
        return self.pull_request_repository.save(pull_request)

    def apply_git_pull_request_merged(self, event) -> PullRequest:
        pull_request = self.pull_request_repository.find_by_external_id(
            event.project_id,
            event.external_id,
        )
        if pull_request is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pull request not found")
        pull_request.status = PullRequestStatus.MERGED
        pull_request.merged_at = datetime.utcnow()
        pull_request.updated_at = pull_request.merged_at
        return self.pull_request_repository.save(pull_request)
