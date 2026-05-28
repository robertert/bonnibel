"""Wspolne fixtury testowe: izolowana baza SQLite in-memory na core/models."""
from __future__ import annotations

import asyncio

import pytest
from sqlalchemy import BigInteger, create_engine
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.models import Base, Project, Task, User, UserStatus


# W SQLite autoinkrementacja dziala tylko dla "INTEGER PRIMARY KEY" (alias ROWID),
# a nasze PK to BigInteger -> BIGINT. Na potrzeby testow kompilujemy BigInteger
# jako INTEGER (tylko dialekt sqlite; produkcyjny Postgres bez zmian).
@compiles(BigInteger, "sqlite")
def _compile_bigint_sqlite(element, compiler, **kw):  # noqa: ANN001
    return "INTEGER"


@pytest.fixture
def db():
    # StaticPool + jedno polaczenie => baza :memory: zyje przez caly test.
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)
        engine.dispose()


@pytest.fixture
def db_session(db):
    return db


@pytest.fixture
def run():
    """Uruchamia korutyne serwisu w tescie synchronicznym."""
    def _run(coro):
        return asyncio.run(coro)
    return _run


@pytest.fixture
def make_user(db):
    def _make(user_id: str, email: str) -> User:
        user = User(
            user_id=user_id,
            email=email,
            name=user_id,
            surname="Test",
            status=UserStatus.ACTIVE,
            is_online=False,
        )
        db.add(user)
        db.commit()
        return user
    return _make


@pytest.fixture
def seeded_task(db_session):
    owner = User(
        user_id="owner-1",
        email="owner@example.com",
        name="Owner",
        surname="User",
        status=UserStatus.ACTIVE,
        is_online=False,
    )
    reviewer = User(
        user_id="reviewer-1",
        email="reviewer@example.com",
        name="Review",
        surname="User",
        status=UserStatus.ACTIVE,
        is_online=False,
    )
    project = Project(
        project_id=1,
        owner_id=owner.user_id,
        name="Demo",
        description="Demo project",
    )
    task = Task(
        task_id=1,
        project_id=project.project_id,
        title="Implement docs",
        description="Task description",
        assignee_id=owner.user_id,
        reviewer_id=reviewer.user_id,
        git_branch_name="feature/docs",
        jira_issue_key="BON-1",
    )
    db_session.add_all([owner, reviewer, project, task])
    db_session.commit()
    return task
