from __future__ import annotations

import logging
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.models import (
    Project,
    PullRequest,
    PullRequestStatus,
    Task,
    TaskEventType,
    NotificationType,
)
from app.modules.integration.gateway import IntegrationGateway
from app.modules.integration.models import IntegrationProvider
from app.modules.notification.manager import notification_service
from app.modules.notification.schemas import NotificationEventCreate
from app.modules.pull_requests.schemas import PullRequestCreate
from app.modules.task_history.service import record_event

logger = logging.getLogger(__name__)


def _require_task(db: Session, project_id: int, task_id: int) -> Task:
    task = db.get(Task, task_id)
    if task is None or task.project_id != project_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nie znaleziono zadania")
    return task


def _require_pr(db: Session, pr_id: int) -> PullRequest:
    pr = db.get(PullRequest, pr_id)
    if pr is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nie znaleziono pull requesta")
    return pr


async def _notify(db: Session, task: Task, ntype: NotificationType, actor_id: str, title: str, message: str) -> None:
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
        logger.warning("Wysłanie powiadomienia PR nie powiodło się dla zadania %s: %r", task.task_id, exc)


def list_prs(db: Session, project_id: int, task_id: int) -> list[PullRequest]:
    _require_task(db, project_id, task_id)
    return list(
        db.scalars(
            select(PullRequest).where(PullRequest.task_id == task_id).order_by(PullRequest.pull_request_id.asc())
        ).all()
    )


async def create_pr(db: Session, project_id: int, task_id: int, payload: PullRequestCreate, author_id: str) -> PullRequest:
    task = _require_task(db, project_id, task_id)

    source_branch = payload.source_branch or task.git_branch_name or (task.jira_issue_key or f"task-{task_id}").lower()
    reviewer_id = payload.reviewer_id or task.reviewer_id

    external_id = f"local-{task_id}"
    url = f"local://projects/{project_id}/tasks/{task_id}/pull-requests"

    # Best-effort: utwórz PR w GitHub jeśli projekt ma aktywną integrację.
    gateway = IntegrationGateway(db)
    if gateway.has(project_id, IntegrationProvider.GITHUB):
        try:
            ref = gateway.git.create_pull_request(
                project_id=project_id,
                task_id=task_id,
                title=payload.title,
                description=payload.description or "",
                source_branch=source_branch,
                target_branch=payload.target_branch,
                reviewer_id=reviewer_id,
            )
            external_id = ref.pull_request_external_id or external_id
            url = ref.url or url
        except Exception as exc:
            logger.warning("GitHub create_pull_request nie powiódł się dla zadania %s: %r", task_id, exc)

    now = datetime.now(timezone.utc)
    pr = PullRequest(
        task_id=task_id,
        external_id=external_id,
        title=payload.title,
        url=url,
        reviewer_id=reviewer_id,
        status=PullRequestStatus.OPEN,
        created_at=now,
        updated_at=now,
    )
    db.add(pr)

    # PR przenosi zadanie do review.
    task.status = "IN_REVIEW"
    task.updated_at = now
    db.commit()
    db.refresh(pr)

    record_event(db, task, TaskEventType.UPDATED, title="Utworzono pull request", description=payload.title, url=url, actor_id=author_id)
    await _notify(db, task, NotificationType.PR_CREATED, author_id, "Nowy pull request", f"Utworzono PR dla zadania #{task_id}")
    return pr


async def approve_pr(db: Session, pr_id: int, reviewer_id: str) -> PullRequest:
    pr = _require_pr(db, pr_id)
    task = db.get(Task, pr.task_id)
    now = datetime.now(timezone.utc)

    pr.status = PullRequestStatus.MERGED
    pr.merged_at = now
    pr.updated_at = now
    if task is not None:
        task.status = "DONE"
        task.closed_at = now
        task.updated_at = now

    # Best-effort: merge + usunięcie gałęzi w GitHub.
    if task is not None:
        gateway = IntegrationGateway(db)
        if gateway.has(task.project_id, IntegrationProvider.GITHUB):
            try:
                gateway.git.merge_pull_request(task.project_id, pr.external_id)
                if task.git_branch_name:
                    gateway.git.delete_branch(task.project_id, task.git_branch_name)
            except Exception as exc:
                logger.warning("GitHub merge/delete_branch nie powiódł się dla PR %s: %r", pr.pull_request_id, exc)

    db.commit()
    db.refresh(pr)

    if task is not None:
        record_event(db, task, TaskEventType.STATUS_CHANGED, title="Zaakceptowano pull request", actor_id=reviewer_id)
        await _notify(db, task, NotificationType.PR_REVIEWED, reviewer_id, "Review zaakceptowane", f"PR dla zadania #{task.task_id} zaakceptowany")
    return pr


async def decline_pr(db: Session, pr_id: int, reviewer_id: str) -> PullRequest:
    pr = _require_pr(db, pr_id)
    task = db.get(Task, pr.task_id)
    now = datetime.now(timezone.utc)

    pr.status = PullRequestStatus.CLOSED
    pr.updated_at = now
    if task is not None:
        task.status = "IN_PROGRESS"
        task.updated_at = now

    db.commit()
    db.refresh(pr)

    if task is not None:
        record_event(db, task, TaskEventType.STATUS_CHANGED, title="Odrzucono pull request", actor_id=reviewer_id)
        await _notify(db, task, NotificationType.PR_REVIEWED, reviewer_id, "Review odrzucone", f"PR dla zadania #{task.task_id} wymaga poprawek")
    return pr
