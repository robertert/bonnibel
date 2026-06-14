from __future__ import annotations

import logging

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.models import Docs, Task, TaskEventType
from app.modules.docs.schemas import DocCreate
from app.modules.integration.gateway import IntegrationGateway
from app.modules.integration.models import IntegrationProvider
from app.modules.task_history.service import record_event

logger = logging.getLogger(__name__)


def _require_task(db: Session, project_id: int, task_id: int) -> Task:
    task = db.get(Task, task_id)
    if task is None or task.project_id != project_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nie znaleziono zadania")
    return task


def list_docs(db: Session, project_id: int, task_id: int) -> list[Docs]:
    _require_task(db, project_id, task_id)
    return list(
        db.scalars(select(Docs).where(Docs.task_id == task_id).order_by(Docs.docs_id.asc())).all()
    )


def create_doc(db: Session, project_id: int, task_id: int, payload: DocCreate, author_id: str) -> Docs:
    task = _require_task(db, project_id, task_id)

    url = payload.url
    external_id: str | None = None

    # Best-effort: jeśli projekt ma aktywną integrację Confluence, utwórz stronę zdalnie.
    gateway = IntegrationGateway(db)
    if url is None and gateway.has(project_id, IntegrationProvider.CONFLUENCE):
        try:
            ref = gateway.confluence.create_task_page(
                project_id=project_id,
                task_id=task_id,
                task_title=payload.title,
                content=payload.content or "",
                author_id=author_id,
            )
            url = ref.url
            external_id = ref.page_external_id
        except Exception as exc:
            url = None  # integracja niedostępna — zapisujemy lokalnie
            logger.warning("Confluence create_task_page nie powiódł się dla zadania %s: %r", task_id, exc)

    if not url:
        url = f"local://projects/{project_id}/tasks/{task_id}/docs"

    doc = Docs(task_id=task_id, title=payload.title, url=url, external_id=external_id)
    db.add(doc)
    db.commit()
    db.refresh(doc)

    record_event(
        db, task, TaskEventType.UPDATED,
        title="Dodano dokumentację", description=payload.title, url=url, actor_id=author_id,
    )
    return doc
