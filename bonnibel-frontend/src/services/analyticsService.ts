import { apiFetch } from '@/lib/api'
import { isUsingFastApiBackend } from '@/lib/env'
import type {
  AnalyticsByAssignee,
  AnalyticsByStatus,
  AnalyticsCommits,
  AnalyticsTaskCount,
  Task,
  TaskHistory,
} from '@/types/domain'

const EMPTY_BY_STATUS: AnalyticsByStatus = {
  TODO: 0,
  IN_PROGRESS: 0,
  IN_REVIEW: 0,
  DONE: 0,
}

async function fetchAllProjectTasks(projectId: number): Promise<Task[]> {
  return apiFetch<Task[]>(`/tasks?projectId=${projectId}`)
}

async function fetchAllProjectHistory(projectId: number): Promise<TaskHistory[]> {
  // json-server: taskHistory nie ma projectId, więc pobieramy całość i filtrujemy po taskach projektu.
  const [tasks, allHistory] = await Promise.all([
    fetchAllProjectTasks(projectId),
    apiFetch<TaskHistory[]>(`/taskHistory`),
  ])
  const taskIds = new Set(tasks.map((t) => t.taskId))
  return allHistory.filter((h) => taskIds.has(h.taskId))
}

export const analyticsService = {
  getTaskCount: async (projectId: number): Promise<AnalyticsTaskCount> => {
    if (isUsingFastApiBackend()) {
      return apiFetch<AnalyticsTaskCount>(
        `/api/projects/${projectId}/analytics/tasks/count`
      )
    }
    const tasks = await fetchAllProjectTasks(projectId)
    return { projectId, taskCount: tasks.length }
  },

  getTaskCountByStatus: async (projectId: number): Promise<AnalyticsByStatus> => {
    if (isUsingFastApiBackend()) {
      return apiFetch<AnalyticsByStatus>(
        `/api/projects/${projectId}/analytics/tasks/by-status`
      )
    }
    const tasks = await fetchAllProjectTasks(projectId)
    const out: AnalyticsByStatus = { ...EMPTY_BY_STATUS }
    for (const t of tasks) {
      // Backend (core/models.py:TaskStatus) nie zna CLOSED — pomijamy.
      if (t.status === 'CLOSED') continue
      out[t.status] = (out[t.status] ?? 0) + 1
    }
    return out
  },

  getTaskCountByAssignee: async (projectId: number): Promise<AnalyticsByAssignee> => {
    if (isUsingFastApiBackend()) {
      return apiFetch<AnalyticsByAssignee>(
        `/api/projects/${projectId}/analytics/tasks/by-assignee`
      )
    }
    const tasks = await fetchAllProjectTasks(projectId)
    const out: AnalyticsByAssignee = {}
    for (const t of tasks) {
      const k = t.assigneeId ?? '(brak)'
      out[k] = (out[k] ?? 0) + 1
    }
    return out
  },

  getClosedTaskHistory: async (projectId: number): Promise<TaskHistory[]> => {
    if (isUsingFastApiBackend()) {
      return apiFetch<TaskHistory[]>(
        `/api/projects/${projectId}/analytics/closed-history`
      )
    }
    // Backend TaskEventType nie ma już dedykowanego TASK_CLOSED/PR_MERGED —
    // używamy STATUS_CHANGED (status zmieniony na DONE) jako proxy.
    const history = await fetchAllProjectHistory(projectId)
    return history.filter((h) => h.type === 'STATUS_CHANGED')
  },

  getCommits: async (projectId: number): Promise<AnalyticsCommits> => {
    if (isUsingFastApiBackend()) {
      return apiFetch<AnalyticsCommits>(
        `/api/projects/${projectId}/analytics/commits`
      )
    }
    // TODO: backend TaskEventType nie modeluje COMMIT — bez dedykowanego
    // typu zdarzenia zwracamy zera. Do uzupełnienia gdy backend doda commit
    // tracking.
    return { commitCount: 0, byActor: {} }
  },
}
