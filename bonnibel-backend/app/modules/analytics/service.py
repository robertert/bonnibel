from app.modules.analytics.repository import AnalyticsRepository
from app.modules.analytics.schemas import AnalyticsOverviewResponse

class AnalyticsService:
    def __init__(self):
        self.repo = AnalyticsRepository()

    async def get_overview(self, db, project_id: int):
        task_count = await self.repo.task_count(db, project_id)
        done_tasks = await self.repo.done_tasks(db, project_id)

        status_rows = await self.repo.tasks_by_status(db, project_id)
        user_rows = await self.repo.tasks_by_user(db, project_id)

        tasks_by_status = {status: count for status, count in status_rows}
        tasks_by_user = {user_id: count for user_id, count in user_rows}

        return AnalyticsOverviewResponse(
            taskCount=task_count,
            doneTasks=done_tasks,
            openTasks=(task_count or 0) - (done_tasks or 0),
            tasksByStatus=tasks_by_status,
            tasksByUser=tasks_by_user,
        )

        