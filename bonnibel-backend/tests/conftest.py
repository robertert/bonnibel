import sys
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.models import Base, Project, Task, User


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def seeded_task(db_session):
    owner = User(
        user_id="owner-1",
        email="owner@example.com",
        name="Owner",
        surname="User",
    )
    reviewer = User(
        user_id="reviewer-1",
        email="reviewer@example.com",
        name="Review",
        surname="User",
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
