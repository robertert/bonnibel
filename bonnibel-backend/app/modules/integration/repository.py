from abc import ABC, abstractmethod
from typing import Optional
from .models import ProjectIntegration, IntegrationProvider


class ProjectIntegrationRepository(ABC):

    @abstractmethod
    def get_active_integration(self, project_id: int, provider: IntegrationProvider) -> ProjectIntegration:
        pass

    @abstractmethod
    def save(self, integration: ProjectIntegration) -> ProjectIntegration:
        pass

    @abstractmethod
    def find_by_project_id_and_provider(self, project_id: int, provider: IntegrationProvider) -> Optional[ProjectIntegration]:
        pass

    @abstractmethod
    def has_active_integration(self, project_id: int, provider: IntegrationProvider) -> bool:
        pass