import { apiFetch } from '@/lib/api'
import type { TaskHistory, TaskSubscription } from '@/types/domain'

// Historia zadania i subskrypcje.
export const taskActivityService = {
  getHistory: (projectId: number, taskId: number): Promise<TaskHistory[]> =>
    apiFetch<TaskHistory[]>(`/projects/${projectId}/tasks/${taskId}/history`),

  getSubscriptions: (): Promise<TaskSubscription[]> =>
    apiFetch<TaskSubscription[]>(`/tasks/subscriptions`),

  subscribe: (taskId: number): Promise<TaskSubscription> =>
    apiFetch<TaskSubscription>(`/tasks/${taskId}/subscribe`, { method: 'POST' }),

  unsubscribe: (taskId: number): Promise<void> =>
    apiFetch<void>(`/tasks/${taskId}/subscribe`, { method: 'DELETE' }),
}
