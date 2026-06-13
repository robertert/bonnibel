from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.models import NotificationType, Task, TaskEventType
from app.modules.hook_auth.schemas import WebhookEvent
from app.modules.hook_auth.service import HookAuthService, resolve_provider
from app.modules.notification.manager import notification_service
from app.modules.notification.schemas import NotificationEventCreate
from app.modules.task_history.service import record_event

router = APIRouter(tags=["Webhooks"])


@router.post("/hooks/{provider}/{project_id}", status_code=status.HTTP_202_ACCEPTED)
async def receive_webhook(
    provider: str,
    project_id: int,
    request: Request,
    db: Session = Depends(get_db),
) -> dict[str, str]:
    try:
        resolved = resolve_provider(provider)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported provider")

    raw_body = await request.body()
    signature = (
        request.headers.get("X-Hub-Signature-256")
        or request.headers.get("X-Hub-Signature")
        or ""
    )

    # Krok 1: weryfikacja autentyczności (Hook Auth).
    if not HookAuthService(db).verify(resolved, project_id, raw_body, signature):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid webhook signature")

    # Krok 2: przetworzenie zdarzenia (historia + powiadomienie).
    try:
        event = WebhookEvent.model_validate(json.loads(raw_body or b"{}"))
    except (json.JSONDecodeError, ValueError):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid payload")

    if event.task_id is not None:
        task = db.get(Task, event.task_id)
        if task is not None and task.project_id == project_id:
            record_event(
                db, task, TaskEventType.UPDATED,
                title=event.title or f"Zdarzenie z {resolved.value}",
                description=event.message,
            )
            try:
                await notification_service.create_from_event(
                    db,
                    NotificationEventCreate(
                        type=NotificationType.TASK_UPDATED,
                        task_id=task.task_id,
                        project_id=project_id,
                        title=event.title or f"Aktualizacja z {resolved.value}",
                        message=event.message or "Otrzymano zdarzenie z systemu zewnętrznego",
                        link_url=f"/projects/{project_id}/tasks/{task.task_id}",
                    ),
                )
            except Exception:
                pass

    return {"status": "accepted"}
