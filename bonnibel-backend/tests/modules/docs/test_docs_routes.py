import pytest
from fastapi import HTTPException

from app.modules.docs.service import MOCK_ACTOR_ID, DocsService


def test_create_docs_for_existing_task(db_session, seeded_task):
    docs = DocsService(db_session).add_task_docs(
        MOCK_ACTOR_ID,
        1,
        1,
        "Task docs",
        "https://docs.example/task-1",
    )

    assert docs.docs_id == 1
    assert docs.task_id == seeded_task.task_id
    assert docs.title == "Task docs"
    assert docs.url == "https://docs.example/task-1"
    assert docs.external_id == "mock-docs-1-1"


def test_duplicate_docs_returns_conflict(db_session, seeded_task):
    service = DocsService(db_session)
    service.add_task_docs(MOCK_ACTOR_ID, 1, 1, "Task docs", "https://docs.example/task-1")

    with pytest.raises(HTTPException) as exc:
        service.add_task_docs(MOCK_ACTOR_ID, 1, 1, "Task docs", "https://docs.example/task-1")

    assert exc.value.status_code == 409
    assert exc.value.detail["errorCode"] == "DOCS_ALREADY_EXISTS"


def test_get_task_docs(db_session, seeded_task):
    service = DocsService(db_session)
    service.add_task_docs(MOCK_ACTOR_ID, 1, 1, "Task docs", "https://docs.example/task-1")

    docs = service.get_task_docs(MOCK_ACTOR_ID, 1, 1)

    assert docs.task_id == seeded_task.task_id


def test_get_project_docs(db_session, seeded_task):
    service = DocsService(db_session)
    service.add_task_docs(MOCK_ACTOR_ID, 1, 1, "Task docs", "https://docs.example/task-1")

    docs = service.get_project_docs(MOCK_ACTOR_ID, 1)

    assert len(docs) == 1
    assert docs[0].external_id == "mock-docs-1-1"


def test_missing_task_returns_not_found(db_session):
    service = DocsService(db_session)

    with pytest.raises(HTTPException) as exc:
        service.add_task_docs(MOCK_ACTOR_ID, 1, 404, "Task docs", "https://docs.example/task-404")

    assert exc.value.status_code == 404
    assert exc.value.detail["errorCode"] == "TASK_NOT_FOUND"


def test_missing_docs_returns_not_found(db_session, seeded_task):
    service = DocsService(db_session)

    with pytest.raises(HTTPException) as exc:
        service.get_task_docs(MOCK_ACTOR_ID, 1, 1)

    assert exc.value.status_code == 404
    assert exc.value.detail["errorCode"] == "DOCS_NOT_FOUND"
