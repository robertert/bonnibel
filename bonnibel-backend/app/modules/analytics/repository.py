from datetime import datetime

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.core.models import Task, TaskStatus


class AnalyticsRepository:
    async def task_count(self, db: Session, project_id: int):
        q = select(func.count(Task.task_id)).where(Task.project_id == project_id)
        return db.execute(q).scalar() or 0

    async def tasks_by_status(self, db: Session, project_id: int):
        q = (select(Task.status, func.count(Task.task_id))
             .where(Task.project_id == project_id)
             .group_by(Task.status))

        return db.execute(q).all()

    async def tasks_by_user(self, db: Session, project_id: int):
        q = (select(Task.assignee_id, func.count(Task.task_id))
             .where(Task.project_id == project_id)
             .group_by(Task.assignee_id))

        return db.execute(q).all()

    async def tasks_by_reviewer(self, db: Session, project_id: int):
        q = (select(Task.reviewer_id, func.count(Task.task_id))
             .where(Task.project_id == project_id)
             .group_by(Task.reviewer_id))

        return db.execute(q).all()

    async def wip_by_user(self, db: Session, project_id: int):
        q = (select(Task.assignee_id, func.count(Task.task_id))
             .where(Task.project_id == project_id)
             .where(Task.status.in_([TaskStatus.IN_PROGRESS, TaskStatus.IN_REVIEW]))
             .group_by(Task.assignee_id))

        return db.execute(q).all()

    async def done_tasks(self, db: Session, project_id: int):
        q = (select(func.count(Task.task_id))
             .where(Task.project_id == project_id)
             .where(Task.status == TaskStatus.DONE))
        return db.execute(q).scalar() or 0

    async def unassigned_tasks(self, db: Session, project_id: int):
        q = (select(func.count(Task.task_id))
             .where(Task.project_id == project_id)
             .where(Task.assignee_id.is_(None)))
        return db.execute(q).scalar() or 0

    async def stale_tasks(self, db: Session, project_id: int, threshold: datetime):
        # Zadania nie-DONE, których nie ruszano od dłuższego czasu.
        q = (select(func.count(Task.task_id))
             .where(Task.project_id == project_id)
             .where(Task.status != TaskStatus.DONE)
             .where(Task.updated_at < threshold))
        return db.execute(q).scalar() or 0

    async def completed_tasks(self, db: Session, project_id: int):
        # (created_at, completed_at) dla zadań DONE; gdy brak closed_at, używamy updated_at.
        completed_at = func.coalesce(Task.closed_at, Task.updated_at)
        q = (select(Task.created_at, completed_at)
             .where(Task.project_id == project_id)
             .where(Task.status == TaskStatus.DONE))
        return db.execute(q).all()
