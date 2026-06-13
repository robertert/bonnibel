from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.dependencies.auth import CurrentUserId
from app.dependencies.db import get_db
from app.modules.notification.manager import notification_service
from app.modules.notification.schemas import (
    NotificationEventCreate,
    NotificationRead,
    TaskRecipientSnapshotUpsert,
    TaskSubscriptionRead,
    UnreadCountRead,
)

router = APIRouter(tags=["notifications"])


@router.get("/tasks/subscriptions", response_model=list[TaskSubscriptionRead])
async def get_subscriptions(
    current_user_id: CurrentUserId,
    db: Annotated[Session, Depends(get_db)],
) -> list[TaskSubscriptionRead]:
    return notification_service.list_subscriptions(db, current_user_id)


@router.post(
    "/tasks/{task_id}/subscribe",
    response_model=TaskSubscriptionRead,
    status_code=status.HTTP_201_CREATED,
)
async def subscribe_task(
    task_id: int,
    current_user_id: CurrentUserId,
    db: Annotated[Session, Depends(get_db)],
):
    return notification_service.subscribe(db, task_id, current_user_id)


@router.delete("/tasks/{task_id}/subscribe", status_code=status.HTTP_204_NO_CONTENT)
async def unsubscribe_task(
    task_id: int,
    current_user_id: CurrentUserId,
    db: Annotated[Session, Depends(get_db)],
) -> Response:
    notification_service.unsubscribe(db, task_id, current_user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/notifications", response_model=list[NotificationRead])
async def get_notifications(
    current_user_id: CurrentUserId,
    db: Annotated[Session, Depends(get_db)],
    unread: bool = False,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[NotificationRead]:
    return notification_service.list_notifications(
        db=db,
        user_id=current_user_id,
        only_unread=unread,
        limit=limit,
        offset=offset,
    )


@router.get("/notifications/unread-count", response_model=UnreadCountRead)
async def get_unread_count(
    current_user_id: CurrentUserId,
    db: Annotated[Session, Depends(get_db)],
) -> dict[str, int]:
    return {"unreadCount": notification_service.unread_count(db, current_user_id)}


@router.patch("/notifications/{notification_id}/read", response_model=NotificationRead)
async def mark_notification_read(
    notification_id: int,
    current_user_id: CurrentUserId,
    db: Annotated[Session, Depends(get_db)],
):
    notification = notification_service.mark_read(db, notification_id, current_user_id)
    if notification is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    return notification


@router.patch("/notifications/read-all")
async def mark_all_notifications_read(
    current_user_id: CurrentUserId,
    db: Annotated[Session, Depends(get_db)],
) -> dict[str, int]:
    updated = notification_service.mark_all_read(db, current_user_id)
    return {"updated": updated}


@router.post("/notifications/events", response_model=list[NotificationRead], status_code=status.HTTP_201_CREATED)
async def create_notification_event(
    payload: NotificationEventCreate,
    current_user_id: CurrentUserId,
    db: Annotated[Session, Depends(get_db)],
):
    if payload.actor_id is None:
        payload.actor_id = current_user_id
    return await notification_service.create_from_event(db, payload)


@router.post("/notifications/task-snapshots", status_code=status.HTTP_204_NO_CONTENT)
async def upsert_task_snapshot(
    payload: TaskRecipientSnapshotUpsert,
    current_user_id: CurrentUserId,
    db: Annotated[Session, Depends(get_db)],
) -> Response:
    notification_service.upsert_task_snapshot(
        db=db,
        task_id=payload.task_id,
        project_id=payload.project_id,
        owner_id=payload.owner_id or current_user_id,
        assignee_id=payload.assignee_id,
        reviewer_id=payload.reviewer_id,
        title=payload.title,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
