import pytest
from unittest.mock import Mock

from bonnibel.integration.confluence_client import ConfluenceIntegrationClient
from bonnibel.integration.models import IntegrationProvider
from bonnibel.integration.exceptions import ConfluenceIntegrationException


@pytest.fixture
def mock_repo():
    repo = Mock()
    integration = Mock()
    integration.external_id = "https://bonnibel.atlassian.net/wiki"
    integration.access_token = "confluence_token_xyz"
    integration.provider = IntegrationProvider.CONFLUENCE
    repo.get_active_integration.return_value = integration
    return repo


@pytest.fixture
def mock_http():
    http = Mock()
    return http


def test_create_task_page_success(mock_repo, mock_http):
    mock_http.post.return_value = Mock(
        is_success=Mock(return_value=True),
        json=Mock(return_value={
            "id": "987654321",
            "title": "Task-123 Documentation"
        })
    )

    client = ConfluenceIntegrationClient(mock_repo, mock_http)

    page = client.create_task_page(
        project_id=1,
        task_id=100,
        task_title="Task-123 Implementation",
        content="<h1>Implementation Details</h1>",
        author_id="user123"
    )

    assert page.page_external_id == "987654321"
    assert page.title == "Task-123 Implementation"
    assert "pages/987654321" in page.url


def test_create_page_failure(mock_repo, mock_http):
    mock_http.post.return_value = Mock(
        is_success=Mock(return_value=False),
        text="Permission denied"
    )

    client = ConfluenceIntegrationClient(mock_repo, mock_http)

    with pytest.raises(ConfluenceIntegrationException):
        client.create_task_page(1, 100, "Title", "Content", "author")