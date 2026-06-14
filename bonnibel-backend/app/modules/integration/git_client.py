import base64
import logging
from datetime import datetime
from typing import Optional

from .models import (
    GitBranchRef, GitPullRequestRef, PullRequestStatus,
    IntegrationProvider, ProjectIntegration
)
from .http_client import IntegrationHttpClient
from .repository import ProjectIntegrationRepository
from .exceptions import GitIntegrationException

logger = logging.getLogger(__name__)


class GitIntegrationClient:
    def __init__(self, repo: ProjectIntegrationRepository, http: IntegrationHttpClient):
        self.repo = repo
        self.http = http

    def create_branch(self, project_id: int, task_id: int, jira_ticket_key: str,
                      assignee_name: str, base_branch: str = "main") -> GitBranchRef:

        integration = self.repo.get_active_integration(project_id, IntegrationProvider.GITHUB)
        branch_name = self._generate_branch_name(jira_ticket_key, assignee_name)

        url = f"https://api.github.com/repos/{integration.external_id}/git/refs"

        body = {
            "ref": f"refs/heads/{branch_name}",
            "sha": self._get_latest_sha(integration.external_id, base_branch, integration.access_token)
        }

        response = self.http.post(url, integration.access_token, body)

        if not response.is_success():
            raise GitIntegrationException(f"Failed to create branch: {response.text}")

        # Dokładamy mały commit na świeżej gałęzi, żeby miała diff względem main
        # (inaczej GitHub odrzuci PR: "no commits between"). Best-effort.
        try:
            self._bootstrap_branch_commit(
                integration.external_id, branch_name, integration.access_token, jira_ticket_key
            )
        except Exception as exc:
            logger.warning("Commit startowy na gałęzi %s nie powiódł się: %r", branch_name, exc)

        return GitBranchRef(
            task_id=task_id,
            branch_name=branch_name,
            external_id=branch_name,
            url=f"https://github.com/{integration.external_id}/tree/{branch_name}"
        )

    def _bootstrap_branch_commit(self, owner_repo: str, branch: str, token: str, jira_ticket_key: str) -> None:
        """Tworzy mały plik na gałęzi przez GitHub Contents API (commit ponad main)."""
        path = f".bonnibel/{branch}.md"
        url = f"https://api.github.com/repos/{owner_repo}/contents/{path}"
        content = base64.b64encode(
            f"# {jira_ticket_key}\n\nGałąź robocza utworzona automatycznie przez Bonnibel.\n".encode("utf-8")
        ).decode("ascii")
        body = {
            "message": f"chore: bootstrap branch for {jira_ticket_key}",
            "content": content,
            "branch": branch,
        }
        resp = self.http.put(url, token, body)
        if not resp.is_success():
            raise GitIntegrationException(
                f"Nie udało się dodać commita startowego na gałęzi '{branch}': "
                f"HTTP {resp.status_code} {resp.text}"
            )

    def create_pull_request(self, project_id: int, task_id: int, title: str, description: str,
                            source_branch: str, target_branch: str = "main",
                            reviewer_id: Optional[str] = None) -> GitPullRequestRef:

        integration = self.repo.get_active_integration(project_id, IntegrationProvider.GITHUB)

        url = f"https://api.github.com/repos/{integration.external_id}/pulls"

        body = {
            "title": title,
            "body": description,
            "head": source_branch,
            "base": target_branch
        }

        response = self.http.post(url, integration.access_token, body)
        data = response.json()

        return GitPullRequestRef(
            pull_request_external_id=str(data.get("id")),
            task_id=task_id,
            reviewer_id=reviewer_id,
            status=PullRequestStatus.OPEN,
            title=title,
            url=data.get("html_url"),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

    def merge_pull_request(self, project_id: int, pr_external_id: str):
        integration = self.repo.get_active_integration(project_id, IntegrationProvider.GITHUB)
        url = f"https://api.github.com/repos/{integration.external_id}/pulls/{pr_external_id}/merge"
        self.http.put(url, integration.access_token)

    def delete_branch(self, project_id: int, branch_name: str):
        integration = self.repo.get_active_integration(project_id, IntegrationProvider.GITHUB)
        url = f"https://api.github.com/repos/{integration.external_id}/git/refs/heads/{branch_name}"
        self.http.delete(url, integration.access_token)

    # Private methods
    def _generate_branch_name(self, jira_key: str, assignee: str) -> str:
        clean_assignee = "".join(c for c in assignee.lower() if c.isalnum())
        return f"{jira_key.lower()}-{clean_assignee}"

    def _get_latest_sha(self, owner_repo: str, branch: str, token: str) -> str:
        url = f"https://api.github.com/repos/{owner_repo}/git/refs/heads/{branch}"
        resp = self.http.get(url, token)
        if not resp.is_success():
            raise GitIntegrationException(
                f"Nie udało się odczytać gałęzi bazowej '{branch}' ({owner_repo}): "
                f"HTTP {resp.status_code} {resp.text}"
            )
        try:
            return resp.json()["object"]["sha"]
        except (KeyError, TypeError) as exc:
            raise GitIntegrationException(
                f"Nieoczekiwana odpowiedź GitHub przy odczycie gałęzi '{branch}': "
                f"{str(resp.text)[:200]}"
            ) from exc