from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.task_history.schemas import TaskHistoryRead
from app.modules.task_history.service import list_history

router = APIRouter(tags=["Task History"])


@router.get(
    "/projects/{project_id}/tasks/{task_id}/history",
    response_model=list[TaskHistoryRead],
)
def read_task_history(
    project_id: int,
    task_id: int,
    db: Session = Depends(get_db),
) -> list[TaskHistoryRead]:
    return list_history(db, project_id, task_id)
