from sqlalchemy import select, delete, update
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.models import (
    Project, 
    ProjectMember, 
    ProjectIntegration, 
    ProjectRole, 
    IntegrationProvider, 
    WebhookSecret
)


class ProjectRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, owner_id: str, name: str, description: Optional[str] = None) -> Project:
        project = Project(
            owner_id=owner_id,
            name=name,
            description=description
        )
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        return project

    def get_by_id(self, project_id: int) -> Optional[Project]:
        return self.db.query(Project).filter(Project.project_id == project_id).first()

    def get_by_user_id(self, user_id: str) -> List[Project]:
        """Zwraca wszystkie projekty, w których użytkownik jest członkiem"""
        return (
            self.db.query(Project)
            .join(ProjectMember)
            .filter(ProjectMember.user_id == user_id)
            .all()
        )

    def update(self, project: Project) -> Project:
        self.db.commit()
        self.db.refresh(project)
        return project

    def delete(self, project_id: int) -> None:
        """Usuwa projekt wraz z wszystkimi powiązanymi rekordami"""
        # usuwamy powiązane webhook secrets
        self.db.query(WebhookSecret).filter(
            WebhookSecret.project_id == project_id
        ).delete(synchronize_session=False)

        # usuwamy integracje projektu
        self.db.query(ProjectIntegration).filter(
            ProjectIntegration.project_id == project_id
        ).delete(synchronize_session=False)

        # usuwamy członków projektu
        self.db.query(ProjectMember).filter(
            ProjectMember.project_id == project_id
        ).delete(synchronize_session=False)

        # usuwamy sam projekt
        self.db.query(Project).filter(Project.project_id == project_id).delete()
        self.db.commit()


class ProjectMemberRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, project_id: int, user_id: str, role: ProjectRole) -> ProjectMember:
        member = ProjectMember(
            project_id=project_id,
            user_id=user_id,
            role=role
        )
        self.db.add(member)
        self.db.commit()
        self.db.refresh(member)
        return member

    def get_by_project(self, project_id: int) -> List[ProjectMember]:
        return (
            self.db.query(ProjectMember)
            .filter(ProjectMember.project_id == project_id)
            .all()
        )

    def get_by_user_and_project(self, project_id: int, user_id: str) -> Optional[ProjectMember]:
        return self.db.query(ProjectMember).filter(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id
        ).first()

    def change_role(self, project_id: int, user_id: str, new_role: ProjectRole) -> Optional[ProjectMember]:
        member = self.get_by_user_and_project(project_id, user_id)
        if member:
            member.role = new_role
            self.db.commit()
            self.db.refresh(member)
        return member

    def delete(self, project_id: int, user_id: str) -> None:
        self.db.query(ProjectMember).filter(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id
        ).delete()
        self.db.commit()

    def exists(self, project_id: int, user_id: str) -> bool:
        return self.db.query(ProjectMember).filter(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id
        ).first() is not None


class ProjectIntegrationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self, 
        project_id: int, 
        provider: IntegrationProvider, 
        external_id: str, 
        access_token: str
    ) -> ProjectIntegration:
        integration = ProjectIntegration(
            project_id=project_id,
            provider=provider,
            external_id=external_id,
            access_token=access_token,
            is_active=True
        )
        self.db.add(integration)
        self.db.commit()
        self.db.refresh(integration)
        return integration

    def delete(self, project_id: int, provider: IntegrationProvider) -> None:
        """Usuwa integrację wraz z powiązanymi sekretami webhooków"""
        # najpierw pobieramy ID integracji
        integrations = self.db.query(ProjectIntegration).filter(
            ProjectIntegration.project_id == project_id,
            ProjectIntegration.provider == provider
        ).all()

        if integrations:
            integration_ids = [i.integration_id for i in integrations]
            
            # usuwamy powiązane webhook secrets
            self.db.query(WebhookSecret).filter(
                WebhookSecret.integration_id.in_(integration_ids)
            ).delete(synchronize_session=False)

            # usuwamy integracje
            self.db.query(ProjectIntegration).filter(
                ProjectIntegration.project_id == project_id,
                ProjectIntegration.provider == provider
            ).delete(synchronize_session=False)

        self.db.commit()

    def list_by_project(self, project_id: int) -> List[ProjectIntegration]:
        return (
            self.db.query(ProjectIntegration)
            .filter(ProjectIntegration.project_id == project_id)
            .all()
        )