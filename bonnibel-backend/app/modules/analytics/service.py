from datetime import datetime, timedelta

from app.core.models import User
from app.modules.analytics.repository import AnalyticsRepository
from app.modules.analytics.schemas import AnalyticsOverviewResponse

STALE_AFTER_DAYS = 7


class AnalyticsService:
    def __init__(self):
        self.repo = AnalyticsRepository()

    def _emails_for(self, db, user_ids) -> dict[str, str]:
        ids = {uid for uid in user_ids if uid}
        if not ids:
            return {}
        rows = db.query(User.user_id, User.email).filter(User.user_id.in_(ids)).all()
        return {user_id: email for user_id, email in rows}

    def _label_map(self, rows, emails: dict[str, str]) -> dict[str, int]:
        # rows: [(user_id|None, count)] -> {email|id|"(brak)": count}
        out: dict[str, int] = {}
        for user_id, count in rows:
            label = emails.get(user_id) or (user_id if user_id else "(brak)")
            out[label] = out.get(label, 0) + count
        return out

    async def get_overview(self, db, project_id: int):
        task_count = await self.repo.task_count(db, project_id)
        done_tasks = await self.repo.done_tasks(db, project_id)
        unassigned = await self.repo.unassigned_tasks(db, project_id)

        threshold = datetime.utcnow() - timedelta(days=STALE_AFTER_DAYS)
        stale = await self.repo.stale_tasks(db, project_id, threshold)

        status_rows = await self.repo.tasks_by_status(db, project_id)
        user_rows = await self.repo.tasks_by_user(db, project_id)
        reviewer_rows = await self.repo.tasks_by_reviewer(db, project_id)
        wip_rows = await self.repo.wip_by_user(db, project_id)
        completed_rows = await self.repo.completed_tasks(db, project_id)

        tasks_by_status = {status: count for status, count in status_rows}

        # Maile dla assignee + reviewer w jednym zapytaniu.
        all_ids = (
            [uid for uid, _ in user_rows]
            + [rid for rid, _ in reviewer_rows]
            + [uid for uid, _ in wip_rows]
        )
        emails = self._emails_for(db, all_ids)

        tasks_by_user = self._label_map(user_rows, emails)
        tasks_by_reviewer = self._label_map(reviewer_rows, emails)
        wip_by_user = self._label_map(wip_rows, emails)

        # Wskaźnik ukończenia (%).
        completion_rate = round((done_tasks / task_count) * 100, 1) if task_count else 0.0

        # Cykl realizacji (h) + throughput per dzień z dat zakończenia.
        durations = []
        throughput_by_day: dict[str, int] = {}
        for created_at, completed_at in completed_rows:
            if created_at and completed_at:
                durations.append((completed_at - created_at).total_seconds() / 3600)
                day = completed_at.date().isoformat()
                throughput_by_day[day] = throughput_by_day.get(day, 0) + 1

        avg_cycle = round(sum(durations) / len(durations), 1) if durations else None

        return AnalyticsOverviewResponse(
            taskCount=task_count,
            doneTasks=done_tasks,
            openTasks=(task_count or 0) - (done_tasks or 0),
            completionRate=completion_rate,
            unassignedTasks=unassigned,
            staleTasks=stale,
            avgCycleTimeHours=avg_cycle,
            tasksByStatus=tasks_by_status,
            tasksByUser=tasks_by_user,
            tasksByReviewer=tasks_by_reviewer,
            wipByUser=wip_by_user,
            throughputByDay=throughput_by_day,
        )
