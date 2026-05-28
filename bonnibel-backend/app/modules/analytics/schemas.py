from pydantic import BaseModel
from typing import Dict


class AnalyticsOverviewResponse(BaseModel):
    taskCount: int
    doneTasks: int
    openTasks: int

    tasksByStatus: Dict[str, int]
    tasksByUser: Dict[str, int]