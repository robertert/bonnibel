from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

# from app.dependencies.db import get_db
from app.core.database import get_db
# from app.modules.auth.router import get_current_user  # tymczasowo
from fastapi import Depends
def get_current_user_dummy():
    """Tymczasowy dummy do testowania bez autoryzacji"""
    return "2f2c28472d4f43048d322a4256b8472a"




from .schemas import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectSummary,
    ProjectMemberCreate,
    ProjectMemberResponse,
    MemberRoleUpdate,
    ProjectIntegrationCreate,
    ProjectIntegrationResponse
)
from .service import ProjectService, MembershipService

router = APIRouter(prefix="/api/project", tags=["Project"])


# Projects
@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    data: ProjectCreate,
    current_user: str = Depends(get_current_user_dummy),  # TODO: zastąpić prawdziwą autoryzacją później
    db: Session = Depends(get_db)
):
    service = ProjectService(db)
    return service.create_project(current_user, data.name, data.description)


@router.get("/my", response_model=List[ProjectSummary])
def get_my_projects(
    current_user: str = Depends(get_current_user_dummy),  # TODO: zastąpić prawdziwą autoryzacją później
    db: Session = Depends(get_db)
):
    service = ProjectService(db)
    return service.get_user_projects(current_user)


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: int,
    current_user: str = Depends(get_current_user_dummy),  # TODO: zastąpić prawdziwą autoryzacją później
    db: Session = Depends(get_db)
):
    service = ProjectService(db)
    project = service.get_project(current_user, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="PROJECT_NOT_FOUND")
    return project


@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int,
    data: ProjectUpdate,
    current_user: str = Depends(get_current_user_dummy),  # TODO: zastąpić prawdziwą autoryzacją później
    db: Session = Depends(get_db)
):
    service = ProjectService(db)
    return service.update_project(current_user, project_id, data.name, data.description)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    current_user: str = Depends(get_current_user_dummy),  # TODO: zastąpić prawdziwą autoryzacją później
    db: Session = Depends(get_db)
):
    service = ProjectService(db)
    service.delete_project(current_user, project_id)


# Membership
@router.post("/{project_id}/members", response_model=ProjectMemberResponse)
def add_project_member(
    project_id: int,
    data: ProjectMemberCreate,
    current_user: str = Depends(get_current_user_dummy),  # TODO: zastąpić prawdziwą autoryzacją później
    db: Session = Depends(get_db)
):
    service = MembershipService(db)
    return service.add_member(current_user, project_id, data.user_id, data.role)


@router.get("/{project_id}/members", response_model=List[ProjectMemberResponse])
def get_project_members(
    project_id: int,
    current_user: str = Depends(get_current_user_dummy),  # TODO: zastąpić prawdziwą autoryzacją później
    db: Session = Depends(get_db)
):
    service = MembershipService(db)
    return service.get_project_members(current_user, project_id)


@router.patch("/{project_id}/members/{user_id}/role", response_model=ProjectMemberResponse)
def change_member_role(
    project_id: int,
    user_id: str,
    data: MemberRoleUpdate,
    current_user: str = Depends(get_current_user_dummy),  # TODO: zastąpić prawdziwą autoryzacją później
    db: Session = Depends(get_db)
):
    service = MembershipService(db)
    return service.change_member_role(current_user, project_id, user_id, data.role)


@router.delete("/{project_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_project_member(
    project_id: int,
    user_id: str,
    current_user: str = Depends(get_current_user_dummy),  # TODO: zastąpić prawdziwą autoryzacją później
    db: Session = Depends(get_db)
):
    service = MembershipService(db)
    service.remove_member(current_user, project_id, user_id)


# Integrations
@router.post("/{project_id}/integrations", response_model=ProjectIntegrationResponse, status_code=status.HTTP_201_CREATED)
def connect_integration(
    project_id: int,
    data: ProjectIntegrationCreate,
    current_user: str = Depends(get_current_user_dummy),  # TODO: zastąpić prawdziwą autoryzacją później
    db: Session = Depends(get_db)
):
    service = ProjectService(db)
    return service.connect_integration(
        current_user, project_id, data.provider, data.external_id, data.access_token
    )


@router.delete("/{project_id}/integrations/{provider}", status_code=status.HTTP_204_NO_CONTENT)
def disconnect_integration(
    project_id: int,
    provider: str, # w przyszłości można rozważyć bardziej rozbudowany identyfikator integracji,
                    # jeśli będzie potrzeba obsługi wielu integracji tego samego typu
    current_user: str = Depends(get_current_user_dummy),  # TODO: zastąpić prawdziwą autoryzacją później
    db: Session = Depends(get_db)
):
    service = ProjectService(db)
    service.disconnect_integration(current_user, project_id, provider)