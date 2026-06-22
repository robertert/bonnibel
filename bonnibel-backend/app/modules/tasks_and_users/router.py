from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session
from app.core.models import ProjectRole
from app.core.security import RoleChecker

require_owner = RoleChecker([ProjectRole.OWNER])
require_developer_or_owner = RoleChecker([ProjectRole.OWNER, ProjectRole.DEVELOPER])
require_any_member = RoleChecker([ProjectRole.OWNER, ProjectRole.DEVELOPER, ProjectRole.REVIEWER])


from app.core.database import get_db
from app.modules.tasks_and_users.schemas import (
    CreateTaskRequest,
    ProjectOut,
    TaskOut,
    UpdateProfileRequest,
    UpdateStatusRequest,
    UpdateTaskAssigneeRequest,
    UpdateTaskReviewerRequest,
    UpdateTaskStatusRequest,
    UserOut,
)
from app.modules.tasks_and_users.service import (
    assign_reviewer,
    assign_task,
    create_task,
    get_task,
    get_user,
    list_projects,
    list_tasks,
    list_users,
    request_close,
    update_profile,
    update_status,
    update_task_status,
)


router = APIRouter(tags=["tasks_and_users"])


@router.get("/projects", response_model=list[ProjectOut])
def read_projects(db: Session = Depends(get_db)) -> list[ProjectOut]:
    return list_projects(db)


@router.get("/users", response_model=list[UserOut])
def read_users(db: Session = Depends(get_db)) -> list[UserOut]:
    return list_users(db)


@router.get("/users/{user_id}", response_model=UserOut)
def read_user(user_id: str, db: Session = Depends(get_db)) -> UserOut:
    return get_user(db, user_id)


@router.put("/users/{user_id}/profile", response_model=UserOut)
def edit_user_profile(user_id: str, payload: UpdateProfileRequest, db: Session = Depends(get_db)) -> UserOut:
    return update_profile(db, user_id, payload)


@router.put("/users/{user_id}/status", response_model=UserOut)
def edit_user_status(user_id: str, payload: UpdateStatusRequest, db: Session = Depends(get_db)) -> UserOut:
    return update_status(db, user_id, payload)


@router.get("/projects/{project_id}/tasks", response_model=list[TaskOut])
def read_project_tasks(
    project_id: int,
    status: str | None = Query(default=None),
    assigneeId: str | None = Query(default=None),
    reviewerId: str | None = Query(default=None),
    onlySubscribed: bool | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[TaskOut]:
    return list_tasks(db, project_id, status, assigneeId, reviewerId, onlySubscribed)


@router.get("/projects/{project_id}/tasks/{task_id}", response_model=TaskOut)
def read_task(project_id: int, task_id: int, db: Session = Depends(get_db), membership = Depends(require_any_member)) -> TaskOut:
    return get_task(db, project_id, task_id)


@router.post("/projects/{project_id}/tasks", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def add_task(project_id: int, payload: CreateTaskRequest, db: Session = Depends(get_db), membership = Depends(require_any_member)) -> TaskOut:
    return create_task(db, project_id, payload)


@router.patch("/projects/{project_id}/tasks/{task_id}/status", response_model=TaskOut)
def patch_task_status(project_id: int, task_id: int, payload: UpdateTaskStatusRequest, db: Session = Depends(get_db)) -> TaskOut:
    return update_task_status(db, project_id, task_id, payload)


@router.patch("/projects/{project_id}/tasks/{task_id}/assign", response_model=TaskOut)
def patch_task_assignee(project_id: int, task_id: int, payload: UpdateTaskAssigneeRequest, db: Session = Depends(get_db)) -> TaskOut:
    return assign_task(db, project_id, task_id, payload)


@router.patch("/projects/{project_id}/tasks/{task_id}/reviewer", response_model=TaskOut)
def patch_task_reviewer(project_id: int, task_id: int, payload: UpdateTaskReviewerRequest, db: Session = Depends(get_db)) -> TaskOut:
    return assign_reviewer(db, project_id, task_id, payload)


@router.post("/projects/{project_id}/tasks/{task_id}/request-close", status_code=status.HTTP_204_NO_CONTENT)
def close_task(project_id: int, task_id: int, db: Session = Depends(get_db)) -> Response:
    request_close(db, project_id, task_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
