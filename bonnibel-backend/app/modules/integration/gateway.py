"""Spina klientów integracji (Git/Jira/Confluence) z bazą danych.

Klienci z tego modułu operują na własnych dataklasach `ProjectIntegration`
i abstrakcyjnym `ProjectIntegrationRepository`. Tutaj dostarczamy konkretną
implementację repozytorium opartą o tabelę `project_integrations` z core/models
oraz fabrykę budującą gotowe klienty. Wszystkie wywołania zewnętrzne są
"best-effort" — wołający powinien je owijać w try/except (patrz `safe_call`).
"""
from __future__ import annotations

from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.models import ProjectIntegration as OrmProjectIntegration

from .models import IntegrationProvider, ProjectIntegration
from .repository import ProjectIntegrationRepository
from .http_client import IntegrationHttpClient
from .git_client import GitIntegrationClient
from .jira_client import JiraIntegrationClient
from .confluence_client import ConfluenceIntegrationClient
from .exceptions import IntegrationException


class SqlAlchemyProjectIntegrationRepository(ProjectIntegrationRepository):
    """Repozytorium integracji oparte o tabelę project_integrations (core/models)."""

    def __init__(self, db: Session):
        self.db = db

    def _to_dataclass(self, row: OrmProjectIntegration) -> ProjectIntegration:
        return ProjectIntegration(
            integration_id=row.integration_id,
            project_id=row.project_id,
            external_id=row.external_id,
            provider=IntegrationProvider(row.provider.value),
            access_token=row.access_token,
            is_active=row.is_active,
        )

    def find_by_project_id_and_provider(
        self, project_id: int, provider: IntegrationProvider
    ) -> Optional[ProjectIntegration]:
        row = self.db.scalars(
            select(OrmProjectIntegration).where(
                OrmProjectIntegration.project_id == project_id,
                OrmProjectIntegration.provider == provider.value,
                OrmProjectIntegration.is_active.is_(True),
            )
        ).first()
        return self._to_dataclass(row) if row else None

    def get_active_integration(
        self, project_id: int, provider: IntegrationProvider
    ) -> ProjectIntegration:
        integration = self.find_by_project_id_and_provider(project_id, provider)
        if integration is None:
            raise IntegrationException(
                f"No active {provider.value} integration for project {project_id}"
            )
        return integration

    def has_active_integration(self, project_id: int, provider: IntegrationProvider) -> bool:
        return self.find_by_project_id_and_provider(project_id, provider) is not None

    def save(self, integration: ProjectIntegration) -> ProjectIntegration:  # pragma: no cover
        raise NotImplementedError("Integrations are created via the project module")


class IntegrationGateway:
    """Buduje klienty integracji dla danej sesji DB i sprawdza dostępność."""

    def __init__(self, db: Session):
        self.repo = SqlAlchemyProjectIntegrationRepository(db)
        http = IntegrationHttpClient()
        self.git = GitIntegrationClient(self.repo, http)
        self.jira = JiraIntegrationClient(self.repo, http)
        self.confluence = ConfluenceIntegrationClient(self.repo, http)

    def has(self, project_id: int, provider: IntegrationProvider) -> bool:
        return self.repo.has_active_integration(project_id, provider)
