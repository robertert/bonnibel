from __future__ import annotations

from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.tasks_and_users.models import Project, Task, User
from app.modules.tasks_and_users.schemas import (
    CreateTaskRequest,
    TaskOut,
    UpdateProfileRequest,
    UpdateStatusRequest,
    UpdateTaskAssigneeRequest,
    UpdateTaskReviewerRequest,
    UpdateTaskStatusRequest,
    UserOut,
)


def _to_user_out(user: User) -> UserOut:
    return UserOut(
        userId=user.user_id,
        email=user.email,
        name=user.name,
        surname=user.surname,
        status=user.status,
        isOnline=user.is_online,
    )


def _to_task_out(task: Task) -> TaskOut:
    return TaskOut(
        taskId=task.task_id,
        projectId=task.project_id,
        title=task.title,
        description=task.description,
        status=task.status,
        assigneeId=task.assignee_id,
        reviewerId=task.reviewer_id,
        gitBranchName=task.git_branch_name,
        jiraIssueKey=task.jira_issue_key,
        createdAt=task.created_at,
        updatedAt=task.updated_at,
        closedAt=task.closed_at,
    )


def get_user(db: Session, user_id: str) -> UserOut:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nie znaleziono użytkownika")
    return _to_user_out(user)


def update_profile(db: Session, user_id: str, payload: UpdateProfileRequest) -> UserOut:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nie znaleziono użytkownika")

    user.email = payload.email
    user.name = payload.name
    user.surname = payload.surname
    db.commit()
    db.refresh(user)
    return _to_user_out(user)


def update_status(db: Session, user_id: str, payload: UpdateStatusRequest) -> UserOut:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nie znaleziono użytkownika")

    user.status = payload.status
    db.commit()
    db.refresh(user)
    return _to_user_out(user)


def list_tasks(
    db: Session,
    project_id: int,
    status_filter: str | None = None,
    assignee_id: str | None = None,
    reviewer_id: str | None = None,
    only_subscribed: bool | None = None,
) -> list[TaskOut]:
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nie znaleziono projektu")

    query = select(Task).where(Task.project_id == project_id)
    if status_filter:
        query = query.where(Task.status == status_filter)
    if assignee_id is not None:
        query = query.where(Task.assignee_id == assignee_id)
    if reviewer_id is not None:
        query = query.where(Task.reviewer_id == reviewer_id)

    tasks = db.scalars(query.order_by(Task.task_id.asc())).all()
    if only_subscribed is True:
        tasks = [task for task in tasks if assignee_id is not None and task.assignee_id == assignee_id]

    return [_to_task_out(task) for task in tasks]


def get_task(db: Session, project_id: int, task_id: int) -> TaskOut:
    task = db.get(Task, task_id)
    if task is None or task.project_id != project_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nie znaleziono zadania")
    return _to_task_out(task)


def create_task(db: Session, project_id: int, payload: CreateTaskRequest) -> TaskOut:
    if db.get(Project, project_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nie znaleziono projektu")

    now = datetime.now(timezone.utc)
    task = Task(
        project_id=project_id,
        title=payload.title,
        description=payload.description,
        status="TODO",
        assignee_id=payload.assigneeId,
        reviewer_id=payload.reviewerId,
        git_branch_name=None,
        jira_issue_key=None,
        created_at=now,
        updated_at=now,
        closed_at=None,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    task.jira_issue_key = f"BON-{task.task_id}"
    db.commit()
    db.refresh(task)
    return _to_task_out(task)


def update_task_status(db: Session, project_id: int, task_id: int, payload: UpdateTaskStatusRequest) -> TaskOut:
    task = db.get(Task, task_id)
    if task is None or task.project_id != project_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nie znaleziono zadania")

    task.status = payload.status
    task.updated_at = payload.updatedAt or datetime.now(timezone.utc)
    task.closed_at = task.updated_at if task.status in {"DONE", "CLOSED"} else None
    db.commit()
    db.refresh(task)
    return _to_task_out(task)


def assign_task(db: Session, project_id: int, task_id: int, payload: UpdateTaskAssigneeRequest) -> TaskOut:
    task = db.get(Task, task_id)
    if task is None or task.project_id != project_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nie znaleziono zadania")

    task.assignee_id = payload.assigneeId
    task.updated_at = payload.updatedAt or datetime.now(timezone.utc)
    db.commit()
    db.refresh(task)
    return _to_task_out(task)


def assign_reviewer(db: Session, project_id: int, task_id: int, payload: UpdateTaskReviewerRequest) -> TaskOut:
    task = db.get(Task, task_id)
    if task is None or task.project_id != project_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nie znaleziono zadania")

    task.reviewer_id = payload.reviewerId
    task.updated_at = payload.updatedAt or datetime.now(timezone.utc)
    db.commit()
    db.refresh(task)
    return _to_task_out(task)


def request_close(db: Session, project_id: int, task_id: int) -> None:
    task = db.get(Task, task_id)
    if task is None or task.project_id != project_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nie znaleziono zadania")

    task.status = "CLOSED"
    task.updated_at = datetime.now(timezone.utc)
    task.closed_at = task.updated_at
    db.commit()
