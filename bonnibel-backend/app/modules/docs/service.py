from dataclasses import dataclass

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.models import Docs
from app.modules.docs.repository import DocsRepository, TaskLookupRepository

MOCK_ACTOR_ID = "mock-user"


def api_error(status_code: int, error_code: str, message: str) -> HTTPException:
    return HTTPException(
        status_code=status_code,
        detail={"errorCode": error_code, "message": message},
    )


@dataclass(frozen=True)
class DocsPageRef:
    task_id: int
    page_external_id: str
    title: str
    url: str


class MockDocsIntegrationClient:
    def create_task_page(
        self,
        project_id: int,
        task_id: int,
        task_title: str,
        content: str,
        author_id: str,
    ) -> DocsPageRef:
        external_id = f"mock-docs-{project_id}-{task_id}"
        return DocsPageRef(
            task_id=task_id,
            page_external_id=external_id,
            title=task_title,
            url=f"https://mock.docs.local/projects/{project_id}/tasks/{task_id}",
        )

    def get_page(self, project_id: int, page_external_id: str) -> DocsPageRef:
        return DocsPageRef(
            task_id=0,
            page_external_id=page_external_id,
            title=page_external_id,
            url=f"https://mock.docs.local/projects/{project_id}/pages/{page_external_id}",
        )


class MockRoleService:
    def require_permission(self, *_args, **_kwargs) -> None:
        return None


class MockTaskHistoryService:
    def add_history(self, *_args, **_kwargs) -> None:
        return None


class MockNotificationService:
    def notify(self, *_args, **_kwargs) -> None:
        return None


class DocsService:
    def __init__(self, db: Session):
        self.docs_repository = DocsRepository(db)
        self.task_repository = TaskLookupRepository(db)
        self.role_service = MockRoleService()
        self.task_history_service = MockTaskHistoryService()
        self.notification_service = MockNotificationService()
        self.docs_client = MockDocsIntegrationClient()

    def add_task_docs(
        self,
        actor_id: str,
        project_id: int,
        task_id: int,
        title: str,
        url: str,
    ) -> Docs:
        self.role_service.require_permission(actor_id, project_id, "ADD_TASK_DOCS")
        task = self.task_repository.find_by_project_and_id(project_id, task_id)
        if task is None:
            raise api_error(status.HTTP_404_NOT_FOUND, "TASK_NOT_FOUND", "Task was not found")
        if self.docs_repository.exists_by_task_id(task_id):
            raise api_error(
                status.HTTP_409_CONFLICT,
                "DOCS_ALREADY_EXISTS",
                "Docs already exist for this task",
            )

        page_ref = self.docs_client.create_task_page(
            project_id=project_id,
            task_id=task_id,
            task_title=title,
            content=url,
            author_id=actor_id,
        )
        docs = Docs(
            task_id=task_id,
            title=title,
            url=url or page_ref.url,
            external_id=page_ref.page_external_id,
        )
        saved = self.docs_repository.save(docs)
        self.task_history_service.add_history(task_id, actor_id, "DOCS_ADDED", title, saved.url)
        self.notification_service.notify("DOCS_ADDED", task_id)
        return saved

    def get_task_docs(self, actor_id: str, project_id: int, task_id: int) -> Docs:
        self.role_service.require_permission(actor_id, project_id, "VIEW_PROJECT_TASKS")
        task = self.task_repository.find_by_project_and_id(project_id, task_id)
        if task is None:
            raise api_error(status.HTTP_404_NOT_FOUND, "TASK_NOT_FOUND", "Task was not found")
        docs = self.docs_repository.find_by_task_id(task_id)
        if docs is None:
            raise api_error(status.HTTP_404_NOT_FOUND, "DOCS_NOT_FOUND", "Docs were not found")
        return docs

    def get_project_docs(self, actor_id: str, project_id: int) -> list[Docs]:
        self.role_service.require_permission(actor_id, project_id, "VIEW_PROJECT_TASKS")
        if not self.task_repository.project_exists(project_id):
            raise api_error(
                status.HTTP_404_NOT_FOUND,
                "PROJECT_NOT_FOUND",
                "Project was not found",
            )
        return self.docs_repository.find_by_project_id(project_id)

    def update_task_docs(
        self,
        actor_id: str,
        project_id: int,
        task_id: int,
        title: str,
        url: str,
    ) -> Docs:
        self.role_service.require_permission(actor_id, project_id, "ADD_TASK_DOCS")
        task = self.task_repository.find_by_project_and_id(project_id, task_id)
        if task is None:
            raise api_error(status.HTTP_404_NOT_FOUND, "TASK_NOT_FOUND", "Task was not found")
        docs = self.docs_repository.find_by_task_id(task_id)
        if docs is None:
            raise api_error(status.HTTP_404_NOT_FOUND, "DOCS_NOT_FOUND", "Docs were not found")

        docs.title = title
        docs.url = url
        saved = self.docs_repository.save(docs)
        self.task_history_service.add_history(task_id, actor_id, "DOCS_UPDATED", title, saved.url)
        self.notification_service.notify("DOCS_UPDATED", task_id)
        return saved

    def require_task_has_docs(self, task_id: int) -> None:
        if not self.docs_repository.exists_by_task_id(task_id):
            raise api_error(
                status.HTTP_409_CONFLICT,
                "TASK_DOCS_REQUIRED",
                "Task docs are required before creating a pull request",
            )
