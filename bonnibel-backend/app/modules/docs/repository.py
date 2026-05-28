from typing import List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.models import Docs, Project, Task


class DocsRepository:
    def __init__(self, db: Session):
        self.db = db

    def save(self, docs: Docs) -> Docs:
        if docs.docs_id is None and self.db.bind and self.db.bind.dialect.name == "sqlite":
            max_id = self.db.query(func.max(Docs.docs_id)).scalar() or 0
            docs.docs_id = max_id + 1
        self.db.add(docs)
        self.db.commit()
        self.db.refresh(docs)
        return docs

    def find_by_task_id(self, task_id: int) -> Optional[Docs]:
        return self.db.query(Docs).filter(Docs.task_id == task_id).first()

    def find_by_external_id(self, external_id: str) -> Optional[Docs]:
        return self.db.query(Docs).filter(Docs.external_id == external_id).first()

    def find_by_project_id(self, project_id: int) -> List[Docs]:
        return (
            self.db.query(Docs)
            .join(Task, Docs.task_id == Task.task_id)
            .filter(Task.project_id == project_id)
            .order_by(Docs.docs_id)
            .all()
        )

    def exists_by_task_id(self, task_id: int) -> bool:
        return self.find_by_task_id(task_id) is not None


class TaskLookupRepository:
    def __init__(self, db: Session):
        self.db = db

    def find_by_project_and_id(self, project_id: int, task_id: int) -> Optional[Task]:
        return (
            self.db.query(Task)
            .filter(Task.project_id == project_id, Task.task_id == task_id)
            .first()
        )

    def project_exists(self, project_id: int) -> bool:
        return self.db.query(Project).filter(Project.project_id == project_id).first() is not None
