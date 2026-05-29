from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.models import Docs
from app.modules.docs.schemas import DocsCreate, DocsResponse, DocsUpdate
from app.modules.docs.service import MOCK_ACTOR_ID, DocsService

router = APIRouter()


def to_response(docs: Docs) -> DocsResponse:
    return DocsResponse(
        docsId=docs.docs_id,
        taskId=docs.task_id,
        title=docs.title,
        url=docs.url,
        externalId=docs.external_id,
    )


@router.post(
    "/projects/{projectId}/tasks/{taskId}/docs",
    response_model=DocsResponse,
    status_code=201,
)
async def add_task_docs(
    projectId: int,
    taskId: int,
    docs_in: DocsCreate,
    db: Session = Depends(get_db),
):
    docs = DocsService(db).add_task_docs(
        actor_id=MOCK_ACTOR_ID,
        project_id=projectId,
        task_id=taskId,
        title=docs_in.title,
        url=docs_in.url,
    )
    return to_response(docs)


@router.get("/projects/{projectId}/tasks/{taskId}/docs", response_model=DocsResponse)
async def get_task_docs(projectId: int, taskId: int, db: Session = Depends(get_db)):
    docs = DocsService(db).get_task_docs(MOCK_ACTOR_ID, projectId, taskId)
    return to_response(docs)


@router.put("/projects/{projectId}/tasks/{taskId}/docs", response_model=DocsResponse)
async def update_task_docs(
    projectId: int,
    taskId: int,
    docs_in: DocsUpdate,
    db: Session = Depends(get_db),
):
    docs = DocsService(db).update_task_docs(
        actor_id=MOCK_ACTOR_ID,
        project_id=projectId,
        task_id=taskId,
        title=docs_in.title,
        url=docs_in.url,
    )
    return to_response(docs)


@router.get("/projects/{projectId}/docs", response_model=list[DocsResponse])
async def get_project_docs(projectId: int, db: Session = Depends(get_db)):
    docs = DocsService(db).get_project_docs(MOCK_ACTOR_ID, projectId)
    return [to_response(item) for item in docs]
