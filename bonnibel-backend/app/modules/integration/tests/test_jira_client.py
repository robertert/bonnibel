import pytest
from unittest.mock import Mock

from ..jira_client import JiraIntegrationClient
from ..models import IntegrationProvider, JiraTicketStatus
from ..exceptions import JiraIntegrationException


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
    return Mock()


def test_create_ticket_success(mock_repo, mock_http):
    mock_http.post.return_value = Mock(
        is_success=lambda: True,
        json=lambda: {"id": "10001", "key": "TASK-123"}
    )

    client = JiraIntegrationClient(mock_repo, mock_http)
    ticket = client.create_ticket(1, 100, "Implement login", "Description")

    assert ticket.ticket_key == "TASK-123"
    assert ticket.status == JiraTicketStatus.TODO


def test_create_ticket_failure(mock_repo, mock_http):
    mock_http.post.return_value = Mock(is_success=lambda: False, text="Error")

    client = JiraIntegrationClient(mock_repo, mock_http)

    with pytest.raises(JiraIntegrationException):
        client.create_ticket(1, 100, "Title", "Desc")