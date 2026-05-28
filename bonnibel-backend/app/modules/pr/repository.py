from typing import Optional

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.core.models import PullRequest, Task


class PullRequestRepository:
    def __init__(self, db: Session):
        self.db = db

    def save(self, pull_request: PullRequest) -> PullRequest:
        if (
            pull_request.pull_request_id is None
            and self.db.bind
            and self.db.bind.dialect.name == "sqlite"
        ):
            max_id = self.db.query(func.max(PullRequest.pull_request_id)).scalar() or 0
            pull_request.pull_request_id = max_id + 1
        self.db.add(pull_request)
        self.db.commit()
        self.db.refresh(pull_request)
        return pull_request

    def find_by_id(self, pull_request_id: int) -> Optional[PullRequest]:
        return (
            self.db.query(PullRequest)
            .filter(PullRequest.pull_request_id == pull_request_id)
            .first()
        )

    def find_by_project_and_id(
        self,
        project_id: int,
        pull_request_id: int,
    ) -> Optional[PullRequest]:
        return (
            self.db.query(PullRequest)
            .join(Task, PullRequest.task_id == Task.task_id)
            .filter(
                Task.project_id == project_id,
                PullRequest.pull_request_id == pull_request_id,
            )
            .first()
        )

    def find_by_task_id(self, task_id: int) -> Optional[PullRequest]:
        return self.db.query(PullRequest).filter(PullRequest.task_id == task_id).first()

    def find_by_external_id(self, project_id: int, external_id: str) -> Optional[PullRequest]:
        return (
            self.db.query(PullRequest)
            .join(Task, PullRequest.task_id == Task.task_id)
            .filter(Task.project_id == project_id, PullRequest.external_id == external_id)
            .first()
        )

    def find_by_user_id(self, user_id: str) -> list[PullRequest]:
        return (
            self.db.query(PullRequest)
            .join(Task, PullRequest.task_id == Task.task_id)
            .filter(or_(PullRequest.reviewer_id == user_id, Task.assignee_id == user_id))
            .order_by(PullRequest.created_at.desc(), PullRequest.pull_request_id.desc())
            .all()
        )


class TaskLookupRepository:
    def __init__(self, db: Session):
        self.db = db

    def find_by_project_and_id(self, project_id: int, task_id: int) -> Optional[Task]:
        return (
            self.db.query(Task)
            .filter(Task.project_id == project_id, Task.task_id == task_id)
            .first()
        )
