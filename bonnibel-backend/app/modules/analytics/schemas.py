from pydantic import BaseModel
from typing import Dict


class AnalyticsOverviewResponse(BaseModel):
    taskCount: int
    doneTasks: int
    openTasks: int
    completionRate: float
    unassignedTasks: int
    staleTasks: int
    avgCycleTimeHours: float | None = None

    tasksByStatus: Dict[str, int]
    tasksByUser: Dict[str, int]
    tasksByReviewer: Dict[str, int]
    wipByUser: Dict[str, int]
    throughputByDay: Dict[str, int]
