import pytest
from unittest.mock import Mock

from ..confluence_client import ConfluenceIntegrationClient
from ..models import IntegrationProvider
from ..exceptions import ConfluenceIntegrationException


@pytest.fixture
def mock_repo():
    repo = Mock()
    integration = Mock()
    integration.external_id = "https://bonnibel.atlassian.net/wiki"
    integration.access_token = "confluence_token"
    integration.provider = IntegrationProvider.CONFLUENCE
    repo.get_active_integration.return_value = integration
    return repo


@pytest.fixture
def mock_http():
    return Mock()


def test_create_task_page_success(mock_repo, mock_http):
    mock_http.post.return_value = Mock(
        is_success=lambda: True,
        json=lambda: {"id": "987654", "title": "Task Page"}
    )

    client = ConfluenceIntegrationClient(mock_repo, mock_http)

    page = client.create_task_page(
        project_id=1,
        task_id=100,
        task_title="Task-123 Docs",
        content="<p>Hello</p>",
        author_id="user1"
    )

    assert page.page_external_id == "987654"
    assert "pages/" in page.url


def test_create_page_failure(mock_repo, mock_http):
    mock_http.post.return_value = Mock(is_success=lambda: False, text="Error")

    client = ConfluenceIntegrationClient(mock_repo, mock_http)

    with pytest.raises(ConfluenceIntegrationException):
        client.create_task_page(1, 100, "Title", "Content", "author")