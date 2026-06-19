from __future__ import annotations

import logging
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.models import NotificationType, Project, Task, TaskEventType, User
from app.modules.integration.gateway import IntegrationGateway
from app.modules.integration.models import IntegrationProvider
from app.modules.notification.manager import notification_service
from app.modules.notification.schemas import NotificationEventCreate
from app.modules.task_history.service import record_event
from app.modules.tasks_and_users.schemas import (
    CreateTaskRequest,
    ProjectOut,
    TaskOut,
    UpdateProfileRequest,
    UpdateStatusRequest,
    UpdateTaskAssigneeRequest,
    UpdateTaskReviewerRequest,
    UpdateTaskStatusRequest,
    UserOut,
)

logger = logging.getLogger(__name__)


async def _notify_task(
    db: Session,
    task: Task,
    ntype: NotificationType,
    actor_id: str | None,
    title: str,
    message: str,
) -> None:
    """Best-effort: wyślij powiadomienie o zdarzeniu na zadaniu (owner/assignee/reviewer/subskrybenci)."""
    project = db.get(Project, task.project_id)
    event = NotificationEventCreate(
        type=ntype,
        task_id=task.task_id,
        project_id=task.project_id,
        actor_id=actor_id,
        owner_id=project.owner_id if project else None,
        assignee_id=task.assignee_id,
        reviewer_id=task.reviewer_id,
        title=title,
        message=message,
        link_url=f"/projects/{task.project_id}/tasks/{task.task_id}",
    )
    try:
        await notification_service.create_from_event(db, event)
    except Exception as exc:
        logger.warning("Wysłanie powiadomienia dla zadania %s nie powiodło się: %r", task.task_id, exc)


def _to_user_out(user: User) -> UserOut:
    return UserOut(
        userId=user.user_id,
        email=user.email,
        name=user.name,
        surname=user.surname,
        status=user.status,
        isOnline=user.is_online,
    )


def _to_project_out(project: Project) -> ProjectOut:
    return ProjectOut(
        projectId=project.project_id,
        name=project.name,
        description=project.description,
        ownerId=project.owner_id,
    )


def list_projects(db: Session) -> list[ProjectOut]:
    projects = db.scalars(select(Project).order_by(Project.project_id.asc())).all()
    return [_to_project_out(project) for project in projects]


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


def list_users(db: Session) -> list[UserOut]:
    users = db.scalars(select(User).order_by(User.email.asc())).all()
    return [_to_user_out(user) for user in users]


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


async def create_task(db: Session, project_id: int, payload: CreateTaskRequest, actor_id: str | None = None) -> TaskOut:
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
    record_event(db, task, TaskEventType.CREATED, title="Utworzono zadanie", description=task.title)
    if task.assignee_id or task.reviewer_id:
        await _notify_task(
            db, task, NotificationType.TASK_ASSIGNED, actor_id,
            "Przypisano zadanie", f"Przypisano Cię do zadania #{task.task_id}: {task.title}",
        )
    return _to_task_out(task)


async def update_task_status(db: Session, project_id: int, task_id: int, payload: UpdateTaskStatusRequest, actor_id: str | None = None) -> TaskOut:
    task = db.get(Task, task_id)
    if task is None or task.project_id != project_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nie znaleziono zadania")

    task.status = payload.status
    task.updated_at = payload.updatedAt or datetime.now(timezone.utc)
    task.closed_at = task.updated_at if task.status in {"DONE", "CLOSED"} else None
    db.commit()
    db.refresh(task)
    _sync_jira_status(db, task)
    record_event(
        db, task, TaskEventType.STATUS_CHANGED,
        title="Zmieniono status", description=f"Nowy status: {task.status}",
    )
    await _notify_task(
        db, task, NotificationType.TASK_UPDATED, actor_id,
        "Zaktualizowano zadanie", f"Zadanie #{task.task_id} zmieniło status na {task.status}",
    )
    return _to_task_out(task)


async def assign_task(db: Session, project_id: int, task_id: int, payload: UpdateTaskAssigneeRequest, actor_id: str | None = None) -> TaskOut:
    task = db.get(Task, task_id)
    if task is None or task.project_id != project_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nie znaleziono zadania")

    task.assignee_id = payload.assigneeId
    task.updated_at = payload.updatedAt or datetime.now(timezone.utc)
    db.commit()
    db.refresh(task)
    _ensure_git_branch(db, task)
    record_event(
        db, task, TaskEventType.UPDATED,
        title="Przypisano wykonawcę", description=task.assignee_id,
        actor_id=task.assignee_id,
    )
    await _notify_task(
        db, task, NotificationType.TASK_ASSIGNED, actor_id,
        "Przypisano zadanie", f"Przypisano Cię do zadania #{task.task_id}: {task.title}",
    )
    return _to_task_out(task)


async def assign_reviewer(db: Session, project_id: int, task_id: int, payload: UpdateTaskReviewerRequest, actor_id: str | None = None) -> TaskOut:
    task = db.get(Task, task_id)
    if task is None or task.project_id != project_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nie znaleziono zadania")

    task.reviewer_id = payload.reviewerId
    task.updated_at = payload.updatedAt or datetime.now(timezone.utc)
    db.commit()
    db.refresh(task)
    record_event(
        db, task, TaskEventType.UPDATED,
        title="Przypisano recenzenta", description=task.reviewer_id,
        actor_id=task.reviewer_id,
    )
    await _notify_task(
        db, task, NotificationType.TASK_ASSIGNED, actor_id,
        "Przypisano jako recenzenta", f"Jesteś recenzentem zadania #{task.task_id}: {task.title}",
    )
    return _to_task_out(task)


def request_close(db: Session, project_id: int, task_id: int) -> None:
    task = db.get(Task, task_id)
    if task is None or task.project_id != project_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nie znaleziono zadania")

    task.status = "CLOSED"
    task.updated_at = datetime.now(timezone.utc)
    task.closed_at = task.updated_at
    db.commit()
    db.refresh(task)
    record_event(db, task, TaskEventType.STATUS_CHANGED, title="Zadanie zamknięte")


def _ensure_git_branch(db: Session, task: Task) -> None:
    """Best-effort: tworzy gałąź Git dla przypisanego zadania, jeśli jest integracja."""
    if task.git_branch_name or not task.assignee_id:
        return
    gateway = IntegrationGateway(db)
    if not gateway.has(task.project_id, IntegrationProvider.GITHUB):
        return
    try:
        ref = gateway.git.create_branch(
            project_id=task.project_id,
            task_id=task.task_id,
            jira_ticket_key=task.jira_issue_key or f"BON-{task.task_id}",
            assignee_name=task.assignee_id,
        )
        task.git_branch_name = ref.branch_name
        db.commit()
    except Exception as exc:
        db.rollback()
        logger.warning("GitHub create_branch nie powiódł się dla zadania %s: %r", task.task_id, exc)


def _sync_jira_status(db: Session, task: Task) -> None:
    """Best-effort: przenosi ticket w Jira zgodnie ze statusem zadania."""
    if not task.jira_issue_key:
        return
    gateway = IntegrationGateway(db)
    if not gateway.has(task.project_id, IntegrationProvider.JIRA):
        return
    try:
        if task.status == "IN_PROGRESS":
            gateway.jira.move_ticket_to_in_progress(task.project_id, task.jira_issue_key)
        elif task.status in {"DONE", "CLOSED"}:
            gateway.jira.move_ticket_to_done(task.project_id, task.jira_issue_key)
    except Exception as exc:
        logger.warning("Jira sync statusu nie powiódł się dla zadania %s: %r", task.task_id, exc)
