from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.tasks_and_users.models import Project, Task, User


def _dt(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def seed_database(db: Session) -> None:
    if db.execute(select(User.user_id)).first() is not None:
        return

    db.add_all(
        [
            User(
                user_id="user-1",
                email="jan.kowalski@example.com",
                name="Jan",
                surname="Kowalski",
                status="AVAILABLE",
                is_online=True,
            ),
            User(
                user_id="user-2",
                email="anna.nowak@example.com",
                name="Anna",
                surname="Nowak",
                status="BUSY",
                is_online=False,
            ),
            User(
                user_id="user-3",
                email="piotr.zielinski@example.com",
                name="Piotr",
                surname="Zieliński",
                status="OPEN_TO_TASKS",
                is_online=True,
            ),
            Project(project_id=1, name="Bonnibel", description="System zarządzania postępem prac zespołu"),
            Task(
                task_id=101,
                project_id=1,
                title="Konfiguracja boilerplate projektu",
                description="Przygotowanie struktury katalogów React i konfiguracji tsconfig.",
                status="DONE",
                assignee_id="user-3",
                reviewer_id="user-1",
                git_branch_name="feature/bon-101-boilerplate",
                jira_issue_key="BON-101",
                created_at=_dt("2026-05-20T10:00:00.000Z"),
                updated_at=_dt("2026-05-21T12:00:00.000Z"),
                closed_at=_dt("2026-05-21T12:00:00.000Z"),
            ),
            Task(
                task_id=102,
                project_id=1,
                title="Integracja Auth Module z frontendem",
                description="Zaimplementowanie widoków rejestracji (signup) oraz logowania (login).",
                status="IN_PROGRESS",
                assignee_id="user-2",
                reviewer_id="user-1",
                git_branch_name="feature/bon-102-auth-integration",
                jira_issue_key="BON-102",
                created_at=_dt("2026-05-22T08:30:00.000Z"),
                updated_at=_dt("2026-05-24T11:00:00.000Z"),
                closed_at=None,
            ),
            Task(
                task_id=103,
                project_id=1,
                title="Stworzenie widoku Tablicy Zadań (Kanban) test",
                description="Zaprojektowanie i oprogramowanie komponentów tablicy z podziałem na kolumny Todo/Progress/Review/Done.",
                status="TODO",
                assignee_id="user-1",
                reviewer_id=None,
                git_branch_name=None,
                jira_issue_key="BON-103",
                created_at=_dt("2026-05-23T15:00:00.000Z"),
                updated_at=_dt("2026-05-23T15:00:00.000Z"),
                closed_at=None,
            ),
        ]
    )
    db.commit()
