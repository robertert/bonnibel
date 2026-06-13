from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.models import Project, Task, TaskEventType, TaskHistory


def _resolve_actor(db: Session, task: Task) -> str | None:
    """Zadaniowe endpointy są bez auth, więc aktora wybieramy z kontekstu zadania."""
    if task.assignee_id:
        return task.assignee_id
    project = db.get(Project, task.project_id)
    return project.owner_id if project else None


def record_event(
    db: Session,
    task: Task,
    event_type: TaskEventType,
    title: str,
    description: str | None = None,
    url: str | None = None,
    actor_id: str | None = None,
) -> TaskHistory | None:
    """Zapisuje zdarzenie w historii zadania. Bez aktora nie zapisuje (FK NOT NULL)."""
    actor = actor_id or _resolve_actor(db, task)
    if actor is None:
        return None
    event = TaskHistory(
        task_id=task.task_id,
        type=event_type,
        actor_id=actor,
        title=title,
        description=description,
        url=url,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def list_history(db: Session, project_id: int, task_id: int) -> list[TaskHistory]:
    task = db.get(Task, task_id)
    if task is None or task.project_id != project_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nie znaleziono zadania")
    return list(
        db.scalars(
            select(TaskHistory)
            .where(TaskHistory.task_id == task_id)
            .order_by(TaskHistory.event_id.asc())
        ).all()
    )
