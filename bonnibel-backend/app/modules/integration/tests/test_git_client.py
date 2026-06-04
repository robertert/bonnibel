import pytest
from unittest.mock import Mock
from datetime import datetime

# Относительные импорты — решают проблему Unresolved reference
from ..git_client import GitIntegrationClient
from ..models import IntegrationProvider, PullRequestStatus, ProjectIntegration
from ..exceptions import GitIntegrationException


@pytest.fixture
def mock_repo():
    repo = Mock()
    integration = ProjectIntegration(
        project_id=1,
        external_id="bonnibel/test-repo",
        provider=IntegrationProvider.GITHUB,
        access_token="ghp_testtoken123456"
    )
    repo.get_active_integration.return_value = integration
    return repo


@pytest.fixture
def mock_http():
    return Mock()


def test_create_branch_success(mock_repo, mock_http):
    mock_http.post.return_value = Mock(is_success=lambda: True, text="ok")
    mock_http.get.return_value = Mock(json=lambda: {"object": {"sha": "abc123def456"}})

    client = GitIntegrationClient(mock_repo, mock_http)

    result = client.create_branch(
        project_id=1, task_id=100, jira_ticket_key="TASK-123",
        assignee_name="John Doe", base_branch="main"
    )

    assert result.task_id == 100
    assert "task-123" in result.branch_name.lower()
    assert "github.com" in result.url


def test_create_pull_request_success(mock_repo, mock_http):
    mock_http.post.return_value = Mock(
        is_success=lambda: True,
        json=lambda: {
            "id": 98765,
            "html_url": "https://github.com/pull/98765"
        }
    )

    client = GitIntegrationClient(mock_repo, mock_http)

    pr = client.create_pull_request(
        project_id=1,
        task_id=100,
        title="Fix login",
        description="...",
        source_branch="feature/task-123",
        reviewer_id="user456"
    )

    assert pr.status == PullRequestStatus.OPEN
    assert pr.pull_request_external_id == "98765"


def test_create_branch_failure(mock_repo, mock_http):
    mock_http.post.return_value = Mock(is_success=lambda: False, text="Error")

    client = GitIntegrationClient(mock_repo, mock_http)

    with pytest.raises(GitIntegrationException):
        client.create_branch(1, 100, "TASK-1", "John", "main")