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

    async def done_tasks(self, db: Session, project_id: int):
        q = (select(func.count(Task.task_id))
             .where(Task.project_id == project_id)
             .where(Task.status == TaskStatus.DONE))
        return db.execute(q).scalar() or 0