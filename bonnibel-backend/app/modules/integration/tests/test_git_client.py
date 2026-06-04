# tests/test_git_client.py
import pytest
from unittest.mock import Mock
from datetime import datetime

from bonnibel.integration.git_client import GitIntegrationClient
from bonnibel.integration.models import IntegrationProvider, PullRequestStatus


@pytest.fixture
def mock_repo():
    repo = Mock()
    integration = Mock()
    integration.external_id = "bonnibel/test-repo"
    integration.access_token = "ghp_testtoken123"
    repo.get_active_integration.return_value = integration
    return repo


@pytest.fixture
def mock_http():
    http = Mock()
    http.post.return_value = Mock(
        is_success=Mock(return_value=True),
        json=Mock(return_value={"id": 12345, "html_url": "https://github.com/pull/123"})
    )
    return http


def test_create_branch(mock_repo, mock_http):
    client = GitIntegrationClient(mock_repo, mock_http)

    result = client.create_branch(
        project_id=1,
        task_id=100,
        jira_ticket_key="TASK-123",
        assignee_name="John Doe",
        base_branch="main"
    )

    assert "task-123" in result.branch_name
    assert "github.com" in result.url
    mock_repo.get_active_integration.assert_called_once()


def test_create_pull_request(mock_repo, mock_http):
    client = GitIntegrationClient(mock_repo, mock_http)

    pr = client.create_pull_request(
        project_id=1,
        task_id=100,
        title="Fix login bug",
        description="...",
        source_branch="feature/task-123",
        target_branch="main"
    )

    assert pr.status == PullRequestStatus.OPEN
    assert pr.pull_request_external_id == "12345"