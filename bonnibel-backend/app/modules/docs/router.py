from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.dependencies.auth import CurrentUserId
from app.dependencies.db import get_db
from app.modules.docs.schemas import DocCreate, DocRead
from app.modules.docs.service import create_doc, list_docs

router = APIRouter(tags=["Docs"])


@router.get("/projects/{project_id}/tasks/{task_id}/docs", response_model=list[DocRead])
def read_docs(
    project_id: int,
    task_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> list[DocRead]:
    return list_docs(db, project_id, task_id)


@router.post(
    "/projects/{project_id}/tasks/{task_id}/docs",
    response_model=DocRead,
    status_code=status.HTTP_201_CREATED,
)
def add_doc(
    project_id: int,
    task_id: int,
    payload: DocCreate,
    current_user_id: CurrentUserId,
    db: Annotated[Session, Depends(get_db)],
) -> DocRead:
    return create_doc(db, project_id, task_id, payload, current_user_id)
