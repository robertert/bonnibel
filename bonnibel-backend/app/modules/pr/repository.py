from typing import Optional

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.core.models import Project, ProjectMember, ProjectRole, PullRequest, PullRequestStatus, Task


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

    def find_by_project(
        self,
        project_id: int,
        reviewer_id: Optional[str] = None,
        status: Optional[PullRequestStatus] = None,
    ) -> list[PullRequest]:
        query = (
            self.db.query(PullRequest)
            .join(Task, PullRequest.task_id == Task.task_id)
            .filter(Task.project_id == project_id)
        )
        if reviewer_id is not None:
            query = query.filter(PullRequest.reviewer_id == reviewer_id)
        if status is not None:
            query = query.filter(PullRequest.status == status)
        return query.order_by(PullRequest.created_at.desc(), PullRequest.pull_request_id.desc()).all()

    def find_by_user_id(self, user_id: str) -> list[PullRequest]:
        return (
            self.db.query(PullRequest)
            .join(Task, PullRequest.task_id == Task.task_id)
            .filter(or_(PullRequest.reviewer_id == user_id, Task.assignee_id == user_id))
            .order_by(PullRequest.created_at.desc(), PullRequest.pull_request_id.desc())
            .all()
        )

    def find_for_reviews_scope(
        self,
        user_id: str,
        status: Optional[PullRequestStatus] = None,
    ) -> list[PullRequest]:
        owner_project_ids = {
            project_id
            for (project_id,) in (
                self.db.query(Project.project_id)
                .outerjoin(
                    ProjectMember,
                    Project.project_id == ProjectMember.project_id,
                )
                .filter(
                    or_(
                        Project.owner_id == user_id,
                        (ProjectMember.user_id == user_id)
                        & (ProjectMember.role == ProjectRole.OWNER),
                    )
                )
                .all()
            )
        }

        reviewer_project_ids = {
            project_id
            for (project_id,) in (
                self.db.query(ProjectMember.project_id)
                .filter(
                    ProjectMember.user_id == user_id,
                    ProjectMember.role == ProjectRole.REVIEWER,
                )
                .all()
            )
        }

        developer_project_ids = {
            project_id
            for (project_id,) in (
                self.db.query(ProjectMember.project_id)
                .filter(
                    ProjectMember.user_id == user_id,
                    ProjectMember.role == ProjectRole.DEVELOPER,
                )
                .all()
            )
        }

        query = self.db.query(PullRequest).join(Task, PullRequest.task_id == Task.task_id)
        filters = []
        if owner_project_ids:
            filters.append(Task.project_id.in_(owner_project_ids))
        if reviewer_project_ids:
            filters.append(
                (Task.project_id.in_(reviewer_project_ids))
                & (PullRequest.reviewer_id == user_id)
            )
        if developer_project_ids:
            filters.append(
                (Task.project_id.in_(developer_project_ids))
                & (Task.assignee_id == user_id)
            )
        if not filters:
            filters.append(or_(PullRequest.reviewer_id == user_id, Task.assignee_id == user_id))

        query = query.filter(or_(*filters))
        if status is not None:
            query = query.filter(PullRequest.status == status)

        return query.order_by(PullRequest.created_at.desc(), PullRequest.pull_request_id.desc()).all()


class TaskLookupRepository:
    def __init__(self, db: Session):
        self.db = db

    def find_by_project_and_id(self, project_id: int, task_id: int) -> Optional[Task]:
        return (
            self.db.query(Task)
            .filter(Task.project_id == project_id, Task.task_id == task_id)
            .first()
        )

    def find_by_id(self, task_id: int) -> Optional[Task]:
        return self.db.query(Task).filter(Task.task_id == task_id).first()
