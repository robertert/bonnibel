from .models import DocsPageRef, IntegrationProvider
from .http_client import IntegrationHttpClient
from .repository import ProjectIntegrationRepository
from .exceptions import ConfluenceIntegrationException


class ConfluenceIntegrationClient:
    def __init__(self, repo: ProjectIntegrationRepository, http: IntegrationHttpClient):
        self.repo = repo
        self.http = http

    def create_task_page(self, project_id: int, task_id: int, task_title: str,
                         content: str, author_id: str) -> DocsPageRef:

        integration = self.repo.get_active_integration(project_id, IntegrationProvider.CONFLUENCE)
        url = f"{integration.external_id}/rest/api/content"

        body = {
            "type": "page",
            "title": task_title,
            "space": {"key": "TEAM"},  # Change as needed
            "body": {
                "storage": {
                    "value": content,
                    "representation": "storage"
                }
            }
        }

        response = self.http.post(url, integration.access_token, body)

        if not response.is_success():
            raise ConfluenceIntegrationException(f"Failed to create page: {response.text}")

        data = response.json()

        return DocsPageRef(
            task_id=task_id,
            page_external_id=data["id"],
            title=task_title,
            url=f"{integration.external_id}/pages/{data['id']}"
        )