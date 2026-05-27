from collections import defaultdict
from typing import Any

from fastapi import WebSocket
from sqlalchemy import and_, delete, func, or_, select
from sqlalchemy.orm import Session

from app.modules.notification.models import (
    ChatMessage,
    Notification,
    NotificationType,
    TaskRecipientSnapshot,
    TaskSubscription,
)
from app.modules.notification.schemas import NotificationEventCreate


class ConnectionManager:
    def __init__(self) -> None:
        self._connections: dict[str, set[WebSocket]] = defaultdict(set)

    async def connect(self, user_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections[user_id].add(websocket)

    def disconnect(self, user_id: str, websocket: WebSocket) -> None:
        sockets = self._connections.get(user_id)
        if not sockets:
            return
        sockets.discard(websocket)
        if not sockets:
            self._connections.pop(user_id, None)

    def is_online(self, user_id: str) -> bool:
        return bool(self._connections.get(user_id))

    async def send_to_user(self, user_id: str, payload: dict[str, Any]) -> bool:
        sockets = list(self._connections.get(user_id, set()))
        delivered = False
        for websocket in sockets:
            try:
                await websocket.send_json(payload)
                delivered = True
            except RuntimeError:
                self.disconnect(user_id, websocket)
        return delivered


connection_manager = ConnectionManager()


class RecipientResolver:
    def resolve(self, db: Session, event: NotificationEventCreate) -> set[str]:
        recipients = set(event.recipient_ids)

        snapshot = None
        if event.task_id is not None:
            snapshot = db.get(TaskRecipientSnapshot, event.task_id)

        assignee_id = event.assignee_id or (snapshot.assignee_id if snapshot else None)
        reviewer_id = event.reviewer_id or (snapshot.reviewer_id if snapshot else None)
        owner_id = event.owner_id or (snapshot.owner_id if snapshot else None)

        if event.type == NotificationType.TASK_ASSIGNED:
            recipients.update(user_id for user_id in [assignee_id, reviewer_id] if user_id)
        elif event.type == NotificationType.TASK_UPDATED:
            recipients.update(user_id for user_id in [assignee_id, reviewer_id, owner_id] if user_id)
            recipients.update(self._subscribers(db, event.task_id))
        elif event.type == NotificationType.PR_CREATED:
            recipients.update(user_id for user_id in [reviewer_id, owner_id] if user_id)
        elif event.type == NotificationType.PR_REVIEWED:
            recipients.update(user_id for user_id in [assignee_id, owner_id] if user_id)
        elif event.type == NotificationType.CHAT_MESSAGE:
            recipients.update(self._subscribers(db, event.task_id))

        if event.actor_id:
            recipients.discard(event.actor_id)

        return recipients

    def _subscribers(self, db: Session, task_id: int | None) -> set[str]:
        if task_id is None:
            return set()
        rows = db.scalars(
            select(TaskSubscription.user_id).where(TaskSubscription.task_id == task_id)
        )
        return set(rows.all())


class NotificationService:
    def __init__(self, manager: ConnectionManager, resolver: RecipientResolver | None = None) -> None:
        self.manager = manager
        self.resolver = resolver or RecipientResolver()

    def list_notifications(
        self,
        db: Session,
        user_id: str,
        only_unread: bool = False,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Notification]:
        stmt = select(Notification).where(Notification.user_id == user_id)
        if only_unread:
            stmt = stmt.where(Notification.is_read.is_(False))
        stmt = stmt.order_by(Notification.created_at.desc(), Notification.notification_id.desc())
        stmt = stmt.limit(limit).offset(offset)
        return list(db.scalars(stmt).all())

    def unread_count(self, db: Session, user_id: str) -> int:
        stmt = select(func.count()).select_from(Notification).where(
            and_(Notification.user_id == user_id, Notification.is_read.is_(False))
        )
        return int(db.scalar(stmt) or 0)

    def mark_read(self, db: Session, notification_id: int, user_id: str) -> Notification | None:
        notification = db.get(Notification, notification_id)
        if notification is None or notification.user_id != user_id:
            return None
        notification.is_read = True
        db.commit()
        db.refresh(notification)
        return notification

    def mark_all_read(self, db: Session, user_id: str) -> int:
        notifications = db.scalars(
            select(Notification).where(
                and_(Notification.user_id == user_id, Notification.is_read.is_(False))
            )
        ).all()
        for notification in notifications:
            notification.is_read = True
        db.commit()
        return len(notifications)

    def list_subscriptions(self, db: Session, user_id: str) -> list[TaskSubscription]:
        return list(
            db.scalars(
                select(TaskSubscription)
                .where(TaskSubscription.user_id == user_id)
                .order_by(TaskSubscription.created_at.desc(), TaskSubscription.task_id.desc())
            ).all()
        )

    def subscribe(self, db: Session, task_id: int, user_id: str) -> TaskSubscription:
        existing = db.get(TaskSubscription, {"task_id": task_id, "user_id": user_id})
        if existing:
            return existing
        subscription = TaskSubscription(task_id=task_id, user_id=user_id)
        db.add(subscription)
        db.commit()
        db.refresh(subscription)
        return subscription

    def unsubscribe(self, db: Session, task_id: int, user_id: str) -> bool:
        result = db.execute(
            delete(TaskSubscription).where(
                and_(TaskSubscription.task_id == task_id, TaskSubscription.user_id == user_id)
            )
        )
        db.commit()
        return bool(result.rowcount)

    def list_messages(self, db: Session, task_id: int, limit: int = 100, before_id: int | None = None) -> list[ChatMessage]:
        stmt = select(ChatMessage).where(ChatMessage.task_id == task_id)
        if before_id is not None:
            stmt = stmt.where(ChatMessage.message_id < before_id)
        stmt = stmt.order_by(ChatMessage.message_id.desc()).limit(limit)
        return list(reversed(db.scalars(stmt).all()))

    async def send_message(self, db: Session, task_id: int, author_id: str, text: str) -> ChatMessage:
        self.subscribe(db, task_id, author_id)
        message = ChatMessage(task_id=task_id, author_id=author_id, text=text)
        db.add(message)
        db.commit()
        db.refresh(message)

        snapshot = db.get(TaskRecipientSnapshot, task_id)
        event = NotificationEventCreate(
            type=NotificationType.CHAT_MESSAGE,
            task_id=task_id,
            project_id=snapshot.project_id if snapshot else None,
            actor_id=author_id,
            title="Nowa wiadomość",
            message=f"Użytkownik {author_id} dodał wiadomość do zadania #{task_id}",
            link_url=self._task_link(task_id, snapshot.project_id if snapshot else None),
        )
        await self.create_from_event(db, event)
        await self._broadcast_chat_message(message)
        return message

    def upsert_task_snapshot(
        self,
        db: Session,
        task_id: int,
        project_id: int | None,
        owner_id: str | None,
        assignee_id: str | None,
        reviewer_id: str | None,
        title: str | None,
    ) -> TaskRecipientSnapshot:
        snapshot = db.get(TaskRecipientSnapshot, task_id)
        if snapshot is None:
            snapshot = TaskRecipientSnapshot(task_id=task_id)
            db.add(snapshot)

        snapshot.project_id = project_id
        snapshot.owner_id = owner_id
        snapshot.assignee_id = assignee_id
        snapshot.reviewer_id = reviewer_id
        snapshot.title = title

        db.commit()
        db.refresh(snapshot)

        for user_id in [assignee_id, reviewer_id]:
            if user_id:
                self.subscribe(db, task_id, user_id)

        return snapshot

    async def create_from_event(self, db: Session, event: NotificationEventCreate) -> list[Notification]:
        if event.task_id is not None and any([event.owner_id, event.assignee_id, event.reviewer_id, event.project_id]):
            snapshot = db.get(TaskRecipientSnapshot, event.task_id)
            self.upsert_task_snapshot(
                db=db,
                task_id=event.task_id,
                project_id=event.project_id or (snapshot.project_id if snapshot else None),
                owner_id=event.owner_id or (snapshot.owner_id if snapshot else None),
                assignee_id=event.assignee_id or (snapshot.assignee_id if snapshot else None),
                reviewer_id=event.reviewer_id or (snapshot.reviewer_id if snapshot else None),
                title=event.title or (snapshot.title if snapshot else None),
            )

        recipients = self.resolver.resolve(db, event)
        notifications: list[Notification] = []
        for user_id in recipients:
            notification = Notification(
                user_id=user_id,
                type=event.type,
                title=event.title or self._default_title(event.type),
                message=event.message or self._default_message(event),
                link_url=event.link_url or self._task_link(event.task_id, event.project_id),
                is_read=False,
                is_delivered=False,
            )
            db.add(notification)
            notifications.append(notification)

        db.commit()
        for notification in notifications:
            db.refresh(notification)
            delivered = await self.manager.send_to_user(
                notification.user_id,
                {
                    "event": "notification_created",
                    "data": self._notification_payload(notification),
                },
            )
            if delivered:
                notification.is_delivered = True

        if notifications:
            db.commit()
            for notification in notifications:
                db.refresh(notification)

        return notifications

    def seed_demo_data(self, db: Session) -> None:
        self.upsert_task_snapshot(
            db,
            task_id=101,
            project_id=1,
            owner_id="user-1",
            assignee_id="user-3",
            reviewer_id="user-1",
            title="Konfiguracja boilerplate projektu",
        )
        self.upsert_task_snapshot(
            db,
            task_id=102,
            project_id=1,
            owner_id="user-1",
            assignee_id="user-2",
            reviewer_id="user-1",
            title="Integracja Auth Module z frontendem",
        )
        self.upsert_task_snapshot(
            db,
            task_id=103,
            project_id=1,
            owner_id="user-1",
            assignee_id="user-3",
            reviewer_id="user-1",
            title="Stworzenie widoku Tablicy Zadań",
        )

        for task_id, user_id in [
            (101, "user-2"),
            (102, "user-3"),
            (103, "user-1"),
        ]:
            self.subscribe(db, task_id, user_id)

        self._ensure_demo_notification(
            db,
            user_id="user-1",
            notification_type=NotificationType.PR_CREATED,
            title="Nowy pull request",
            message="Użytkownik user-2 utworzył PR dla zadania BON-102.",
            link_url="/projects/1/tasks/102",
        )
        self._ensure_demo_notification(
            db,
            user_id="user-2",
            notification_type=NotificationType.PR_REVIEWED,
            title="Review zaakceptowane",
            message="Pull request dla BON-102 został zaakceptowany.",
            link_url="/projects/1/tasks/102",
        )
        self._ensure_demo_notification(
            db,
            user_id="user-2",
            notification_type=NotificationType.CHAT_MESSAGE,
            title="Nowa wiadomość",
            message="Użytkownik user-1 dodał wiadomość do zadania BON-102.",
            link_url="/projects/1/tasks/102",
            is_read=True,
        )
        self._ensure_demo_notification(
            db,
            user_id="user-3",
            notification_type=NotificationType.TASK_ASSIGNED,
            title="Przypisano zadanie",
            message="Zadanie BON-103 zostało przypisane do user-3.",
            link_url="/projects/1/tasks/103",
        )
        self._ensure_demo_notification(
            db,
            user_id="user-3",
            notification_type=NotificationType.TASK_UPDATED,
            title="Zaktualizowano zadanie",
            message="Zadanie BON-101 zmieniło status na DONE.",
            link_url="/projects/1/tasks/101",
        )

        self._ensure_demo_message(
            db,
            task_id=101,
            author_id="user-3",
            text="Boilerplate jest gotowy, proszę o review.",
        )
        self._ensure_demo_message(
            db,
            task_id=101,
            author_id="user-1",
            text="Sprawdziłem, wygląda dobrze. Zamykamy temat.",
        )
        self._ensure_demo_message(
            db,
            task_id=102,
            author_id="user-2",
            text="Frontend auth jest podpięty, potrzebuję potwierdzenia kontraktu API.",
        )

    def _ensure_demo_notification(
        self,
        db: Session,
        user_id: str,
        notification_type: NotificationType,
        title: str,
        message: str,
        link_url: str,
        is_read: bool = False,
    ) -> None:
        existing = db.scalar(
            select(Notification).where(
                and_(
                    Notification.user_id == user_id,
                    Notification.type == notification_type,
                    Notification.title == title,
                    Notification.link_url == link_url,
                )
            )
        )
        if existing:
            return

        db.add(
            Notification(
                user_id=user_id,
                type=notification_type,
                title=title,
                message=message,
                link_url=link_url,
                is_read=is_read,
                is_delivered=False,
            )
        )
        db.commit()

    def _ensure_demo_message(
        self,
        db: Session,
        task_id: int,
        author_id: str,
        text: str,
    ) -> None:
        existing = db.scalar(
            select(ChatMessage).where(
                and_(
                    ChatMessage.task_id == task_id,
                    ChatMessage.author_id == author_id,
                    ChatMessage.text == text,
                )
            )
        )
        if existing:
            return

        db.add(ChatMessage(task_id=task_id, author_id=author_id, text=text))
        db.commit()

    async def _broadcast_chat_message(self, message: ChatMessage) -> None:
        payload = {
            "event": "chat_message_created",
            "data": {
                "messageId": message.message_id,
                "taskId": message.task_id,
                "authorId": message.author_id,
                "text": message.text,
                "createdAt": message.created_at.isoformat(),
            },
        }
        recipients = list(self.manager._connections.keys())
        for user_id in recipients:
            await self.manager.send_to_user(user_id, payload)

    def _default_title(self, notification_type: NotificationType) -> str:
        return {
            NotificationType.TASK_ASSIGNED: "Przypisano zadanie",
            NotificationType.TASK_UPDATED: "Zaktualizowano zadanie",
            NotificationType.PR_CREATED: "Utworzono pull request",
            NotificationType.PR_REVIEWED: "Zmieniono status review",
            NotificationType.CHAT_MESSAGE: "Nowa wiadomość",
        }[notification_type]

    def _default_message(self, event: NotificationEventCreate) -> str:
        subject = f"zadania #{event.task_id}" if event.task_id is not None else "projektu"
        return f"Wystąpiło zdarzenie {event.type.value} dotyczące {subject}."

    def _task_link(self, task_id: int | None, project_id: int | None) -> str | None:
        if task_id is None:
            return None
        if project_id is None:
            return f"/tasks/{task_id}"
        return f"/projects/{project_id}/tasks/{task_id}"

    def _notification_payload(self, notification: Notification) -> dict[str, Any]:
        return {
            "notificationId": notification.notification_id,
            "userId": notification.user_id,
            "type": notification.type.value,
            "title": notification.title,
            "message": notification.message,
            "linkUrl": notification.link_url,
            "isRead": notification.is_read,
            "isDelivered": notification.is_delivered,
            "createdAt": notification.created_at.isoformat(),
        }


notification_service = NotificationService(connection_manager)
