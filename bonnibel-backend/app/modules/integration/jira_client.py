from .models import JiraTicketRef, JiraTicketStatus, IntegrationProvider
from .http_client import IntegrationHttpClient
from .repository import ProjectIntegrationRepository
from .exceptions import JiraIntegrationException


class JiraIntegrationClient:
    def __init__(self, repo: ProjectIntegrationRepository, http: IntegrationHttpClient):
        self.repo = repo
        self.http = http

    def create_ticket(self, project_id: int, task_id: int, title: str, description: str) -> JiraTicketRef:
        integration = self.repo.get_active_integration(project_id, IntegrationProvider.JIRA)
        url = f"{integration.external_id}/rest/api/2/issue"

        body = {
            "fields": {
                "summary": title,
                "description": description,
                "issuetype": {"name": "Task"}
            }
        }

        response = self.http.post(url, integration.access_token, body)

        if not response.is_success():
            raise JiraIntegrationException(f"Failed to create Jira ticket: {response.text}")

        data = response.json()
        ticket_key = data["key"]

        return JiraTicketRef(
            task_id=task_id,
            ticket_external_id=data["id"],
            ticket_key=ticket_key,
            url=f"{integration.external_id}/browse/{ticket_key}",
            status=JiraTicketStatus.TODO
        )

    def move_ticket_to_in_progress(self, project_id: int, ticket_key: str):
        self._transition_ticket(project_id, ticket_key, "21")  # Adjust ID as needed

    def move_ticket_to_done(self, project_id: int, ticket_key: str):
        self._transition_ticket(project_id, ticket_key, "31")

    def _transition_ticket(self, project_id: int, ticket_key: str, transition_id: str):
        integration = self.repo.get_active_integration(project_id, IntegrationProvider.JIRA)
        url = f"{integration.external_id}/rest/api/2/issue/{ticket_key}/transitions"

        body = {"transition": {"id": transition_id}}
        self.http.post(url, integration.access_token, body)