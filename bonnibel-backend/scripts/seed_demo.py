"""Idempotentny seed danych demo dla Bonnibel.

Uruchomienie (z katalogu bonnibel-backend, baza musi działać + alembic upgrade head):
    ./venv/bin/python scripts/seed_demo.py

Tworzy loginowalnych użytkowników (hasło: password123) oraz spójny zestaw
wypełniający WSZYSTKIE tabele, tak by przeklikać aplikację. Bezpieczny do
ponownego uruchamiania (stałe ID + merge).
"""
from __future__ import annotations

import os
import sys
from datetime import datetime, timedelta

# Pozwól uruchamiać jako `python scripts/seed_demo.py`.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text  # noqa: E402

from app.core.database import SessionLocal  # noqa: E402
from app.core.security import get_password_hash  # noqa: E402
from app.core.models import (  # noqa: E402
    Auth,
    ChatMessage,
    Docs,
    IntegrationProvider,
    Notification,
    NotificationType,
    Project,
    ProjectIntegration,
    ProjectMember,
    ProjectRole,
    PullRequest,
    PullRequestStatus,
    Task,
    TaskEventType,
    TaskHistory,
    TaskRecipientSnapshot,
    TaskStatus,
    TaskSubscription,
    User,
    UserStatus,
    WebhookSecret,
)

PASSWORD = "password123"
NOW = datetime.utcnow()


def ago(days=0, hours=0):
    return NOW - timedelta(days=days, hours=hours)


USERS = [
    # user_id, email, name, surname, online
    ("user-1", "owner@bonnibel.dev", "Pavel", "Kapitsa", True),
    ("user-2", "dev@bonnibel.dev", "Jan", "Jedra", True),
    ("user-3", "reviewer@bonnibel.dev", "Kinga", "Kowal", False),
    ("user-4", "dev2@bonnibel.dev", "Maciej", "Jamrozy", False),
]

# task_id, title, status, assignee, reviewer, branch, closed_at
TASKS = [
    (101, "Konfiguracja boilerplate projektu", TaskStatus.DONE, "user-3", "user-1", "bon-101-user3", ago(5)),
    (102, "Integracja Auth Module z frontendem", TaskStatus.IN_REVIEW, "user-2", "user-1", "bon-102-user2", None),
    (103, "Stworzenie widoku Tablicy Zadań", TaskStatus.IN_PROGRESS, "user-3", "user-1", "bon-103-user3", None),
    (104, "Moduł powiadomień WebSocket", TaskStatus.TODO, "user-2", "user-1", None, None),
    (105, "Analityka — wykresy statusów", TaskStatus.DONE, "user-4", "user-1", None, ago(1)),
    (106, "Integracja z Jira (backlog)", TaskStatus.TODO, None, None, None, None),
]


def seed(db) -> None:
    # --- Users + Auth ---
    for uid, email, name, surname, online in USERS:
        db.merge(User(user_id=uid, email=email, name=name, surname=surname,
                      status=UserStatus.ACTIVE, is_online=online))
        db.merge(Auth(user_id=uid, pass_hash=get_password_hash(PASSWORD)))
    db.commit()  # użytkownicy muszą istnieć przed rekordami z FK

    # --- Project + members ---
    db.merge(Project(project_id=1, owner_id="user-1", name="Bonnibel Core",
                     description="System zarządzania postępem prac zespołu"))
    members = [("user-1", ProjectRole.OWNER), ("user-2", ProjectRole.DEVELOPER),
               ("user-3", ProjectRole.REVIEWER), ("user-4", ProjectRole.DEVELOPER)]
    for uid, role in members:
        db.merge(ProjectMember(project_id=1, user_id=uid, role=role))

    # --- Integration + webhook secret ---
    db.merge(ProjectIntegration(integration_id=1, project_id=1, external_id="bonnibel/core",
                                provider=IntegrationProvider.GITHUB,
                                access_token="ghp_demo_token", is_active=True))
    db.merge(WebhookSecret(webhook_secret_id=1, integration_id=1, project_id=1,
                           provider=IntegrationProvider.GITHUB, secret="demo-webhook-secret",
                           is_active=True))
    db.commit()  # projekt musi istnieć przed zadaniami

    # --- Tasks ---
    for tid, title, status, assignee, reviewer, branch, closed in TASKS:
        db.merge(Task(task_id=tid, project_id=1, title=title,
                      description=f"Opis zadania: {title}", status=status,
                      assignee_id=assignee, reviewer_id=reviewer,
                      git_branch_name=branch, jira_issue_key=f"BON-{tid}",
                      created_at=ago(7), updated_at=ago(1), closed_at=closed))
    db.commit()  # zadania muszą istnieć przed czatem/PR/docs/historią

    # --- Task recipient snapshots (dla resolvera powiadomień) ---
    for tid, title, status, assignee, reviewer, branch, closed in TASKS:
        db.merge(TaskRecipientSnapshot(task_id=tid, project_id=1, owner_id="user-1",
                                       assignee_id=assignee, reviewer_id=reviewer,
                                       title=title, updated_at=NOW))

    # --- Subscriptions ---
    subs = [(101, "user-1"), (101, "user-3"), (102, "user-1"), (102, "user-2"), (103, "user-3")]
    for tid, uid in subs:
        db.merge(TaskSubscription(task_id=tid, user_id=uid, created_at=ago(3)))

    # --- Chat messages ---
    chats = [
        (1, 101, "user-3", "Boilerplate gotowy, proszę o review.", ago(5, 2)),
        (2, 101, "user-1", "Sprawdziłem, wygląda dobrze. Zamykamy.", ago(5, 1)),
        (3, 102, "user-2", "Auth podpięty, czekam na review.", ago(1, 5)),
        (4, 102, "user-1", "Rzucę okiem dzisiaj.", ago(1, 3)),
    ]
    for mid, tid, author, txtmsg, created in chats:
        db.merge(ChatMessage(message_id=mid, task_id=tid, author_id=author, text=txtmsg, created_at=created))

    # --- Notifications ---
    notifs = [
        (1, "user-1", NotificationType.PR_CREATED, "Nowy pull request", "Utworzono PR dla BON-102", "/projects/1/tasks/102", False),
        (2, "user-2", NotificationType.PR_REVIEWED, "Review zaakceptowane", "PR dla BON-101 zaakceptowany", "/projects/1/tasks/101", True),
        (3, "user-2", NotificationType.CHAT_MESSAGE, "Nowa wiadomość", "user-1 napisał w BON-102", "/projects/1/tasks/102", False),
        (4, "user-3", NotificationType.TASK_ASSIGNED, "Przypisano zadanie", "Przypisano Ci BON-103", "/projects/1/tasks/103", False),
        (5, "user-3", NotificationType.TASK_UPDATED, "Zaktualizowano zadanie", "BON-101 zmieniło status na DONE", "/projects/1/tasks/101", True),
        (6, "user-1", NotificationType.STATUS_CHANGED, "Zmiana statusu", "BON-105 zostało zamknięte", "/projects/1/tasks/105", False),
        (7, "user-4", NotificationType.TASK_ASSIGNED, "Przypisano zadanie", "Przypisano Ci BON-105", "/projects/1/tasks/105", True),
        (8, "user-1", NotificationType.MENTION, "Wzmianka", "Wspomniano o Tobie w BON-103", "/projects/1/tasks/103", False),
    ]
    for nid, uid, ntype, title, msg, link, read in notifs:
        db.merge(Notification(notification_id=nid, user_id=uid, type=ntype, title=title,
                              message=msg, link_url=link, is_read=read, is_delivered=True, created_at=ago(2)))

    # --- Docs ---
    db.merge(Docs(docs_id=1, task_id=101, title="Setup projektu — README",
                  url="https://confluence.local/pages/101", external_id="CONF-101"))
    db.merge(Docs(docs_id=2, task_id=102, title="Kontrakt API Auth",
                  url="https://confluence.local/pages/102", external_id="CONF-102"))

    # --- Pull requests ---
    db.merge(PullRequest(pull_request_id=1, task_id=101, external_id="42", title="Boilerplate setup",
                         url="https://github.com/bonnibel/core/pull/42", reviewer_id="user-1",
                         status=PullRequestStatus.MERGED, created_at=ago(5, 3), updated_at=ago(5), merged_at=ago(5)))
    db.merge(PullRequest(pull_request_id=2, task_id=102, external_id="57", title="Auth integration",
                         url="https://github.com/bonnibel/core/pull/57", reviewer_id="user-1",
                         status=PullRequestStatus.OPEN, created_at=ago(1, 4), updated_at=ago(1, 2), merged_at=None))

    # --- Task history ---
    history = [
        (1, 101, TaskEventType.CREATED, "user-1", "Utworzono zadanie", "Konfiguracja boilerplate"),
        (2, 101, TaskEventType.STATUS_CHANGED, "user-3", "Zmieniono status", "Nowy status: DONE"),
        (3, 102, TaskEventType.CREATED, "user-1", "Utworzono zadanie", "Integracja Auth"),
        (4, 102, TaskEventType.UPDATED, "user-2", "Utworzono pull request", "Auth integration"),
    ]
    for eid, tid, etype, actor, title, desc in history:
        db.merge(TaskHistory(event_id=eid, task_id=tid, type=etype, actor_id=actor,
                             title=title, description=desc, url=None))

    db.commit()


def reset_sequences(db) -> None:
    """Po wstawieniu jawnych ID ustaw sekwencje na max+1, by API nie kolidowało."""
    pairs = [
        ("projects_project_id_seq", "projects", "project_id"),
        ("tasks_task_id_seq", "tasks", "task_id"),
        ("chat_messages_message_id_seq", "chat_messages", "message_id"),
        ("notifications_notification_id_seq", "notifications", "notification_id"),
        ("pull_requests_pull_request_id_seq", "pull_requests", "pull_request_id"),
        ("docs_docs_id_seq", "docs", "docs_id"),
        ("task_history_event_id_seq", "task_history", "event_id"),
        ("project_integrations_integration_id_seq", "project_integrations", "integration_id"),
        ("webhook_secrets_webhook_secret_id_seq", "webhook_secrets", "webhook_secret_id"),
    ]
    for seq, table, pk in pairs:
        db.execute(text(
            f"SELECT setval('{seq}', (SELECT COALESCE(MAX({pk}), 1) FROM {table}))"
        ))
    db.commit()


def main() -> None:
    with SessionLocal() as db:
        seed(db)
        reset_sequences(db)
    print("Seed OK. Dane demo załadowane.")
    print(f"Logowanie (hasło dla wszystkich: {PASSWORD}):")
    for uid, email, name, surname, _ in USERS:
        print(f"  - {email}  ({uid}, {name} {surname})")
    print("Projekt: 'Bonnibel Core' (id=1) | zadania 101-106 | PR/Docs/History/Notifications wypełnione.")


if __name__ == "__main__":
    main()
