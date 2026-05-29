from fastapi import HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.models import ProjectRole, IntegrationProvider
from .repository import ProjectRepository, ProjectMemberRepository, ProjectIntegrationRepository


class ProjectService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ProjectRepository(db)
        self.member_repo = ProjectMemberRepository(db)
        self.integration_repo = ProjectIntegrationRepository(db)

    def create_project(self, owner_id: str, name: str, description: Optional[str] = None):
        project = self.repo.create(owner_id, name, description)
        self.member_repo.create(project.project_id, owner_id, ProjectRole.OWNER)
        return project

    def get_user_projects(self, user_id: str):
        return self.repo.get_by_user_id(user_id)

    def get_project(self, user_id: str, project_id: int):
        # TODO: dodać sprawdzanie uprawnień później
        return self.repo.get_by_id(project_id)

    def update_project(self, user_id: str, project_id: int, name: Optional[str], description: Optional[str]):
        # TODO: dodać sprawdzanie uprawnień
        project = self.repo.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="PROJECT_NOT_FOUND")

        if name is not None:
            project.name = name
        if description is not None:
            project.description = description

        return self.repo.update(project)

    def delete_project(self, user_id: str, project_id: int):
        # TODO: dodać sprawdzanie uprawnień
        self.repo.delete(project_id)

    # Integracje
    def connect_integration(self, actor_id: str, project_id: int, provider: IntegrationProvider, 
                          external_id: str, access_token: str):
        # TODO: dodać sprawdzanie uprawnień
        return self.integration_repo.create(project_id, provider, external_id, access_token)

    def disconnect_integration(self, actor_id: str, project_id: int, provider: IntegrationProvider):
        # TODO: dodać sprawdzanie uprawnień
        self.integration_repo.delete(project_id, provider)


class MembershipService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ProjectMemberRepository(db)

    def add_member(self, actor_id: str, project_id: int, user_id: str, role: ProjectRole):
        # TODO: dodać sprawdzanie uprawnień
        if self.repo.exists(project_id, user_id):
            raise HTTPException(status_code=409, detail="USER_ALREADY_IN_PROJECT")
        return self.repo.create(project_id, user_id, role)

    def remove_member(self, actor_id: str, project_id: int, user_id: str):
        # TODO: dodać sprawdzanie uprawnień
        member = self.repo.get_by_user_and_project(project_id, user_id)
        if not member:
            raise HTTPException(status_code=404, detail="MEMBER_NOT_FOUND")
        if member.role == ProjectRole.OWNER:
            raise HTTPException(status_code=409, detail="CANNOT_REMOVE_PROJECT_OWNER")
        self.repo.delete(project_id, user_id)

    def change_member_role(self, actor_id: str, project_id: int, user_id: str, role: ProjectRole):
        # TODO: dodać sprawdzanie uprawnień
        member = self.repo.change_role(project_id, user_id, role)
        if not member:
            raise HTTPException(status_code=404, detail="MEMBER_NOT_FOUND")
        return member

    def get_project_members(self, actor_id: str, project_id: int):
        # TODO: dodać sprawdzanie uprawnień
        return self.repo.get_by_project(project_id)