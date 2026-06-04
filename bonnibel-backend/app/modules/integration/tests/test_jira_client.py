import pytest
from unittest.mock import Mock

from bonnibel.integration.jira_client import JiraIntegrationClient
from bonnibel.integration.models import IntegrationProvider, JiraTicketStatus
from bonnibel.integration.exceptions import JiraIntegrationException


@pytest.fixture
def mock_repo():
    repo = Mock()
    integration = Mock()
    integration.external_id = "https://bonnibel.atlassian.net"
    integration.access_token = "jira_token_123"
    integration.provider = IntegrationProvider.JIRA
    repo.get_active_integration.return_value = integration
    return repo


@pytest.fixture
def mock_http():
    http = Mock()
    return http


def test_create_ticket_success(mock_repo, mock_http):
    mock_http.post.return_value = Mock(
        is_success=Mock(return_value=True),
        json=Mock(return_value={
            "id": "10001",
            "key": "TASK-123"
        })
    )

    client = JiraIntegrationClient(mock_repo, mock_http)

    ticket = client.create_ticket(
        project_id=1,
        task_id=100,
        title="Implement login feature",
        description="Users should be able to login with email"
    )

    assert ticket.ticket_key == "TASK-123"
    assert ticket.status == JiraTicketStatus.TODO
    assert "browse/TASK-123" in ticket.url


def test_move_ticket_to_in_progress(mock_repo, mock_http):
    mock_http.post.return_value = Mock(is_success=Mock(return_value=True))

    client = JiraIntegrationClient(mock_repo, mock_http)
    client.move_ticket_to_in_progress(1, "TASK-123")

    mock_http.post.assert_called_once()


def test_create_ticket_failure(mock_repo, mock_http):
    mock_http.post.return_value = Mock(
        is_success=Mock(return_value=False),
        text="Invalid project key"
    )

    client = JiraIntegrationClient(mock_repo, mock_http)

    with pytest.raises(JiraIntegrationException):
        client.create_ticket(1, 100, "Test", "Desc")