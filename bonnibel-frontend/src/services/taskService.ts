import { apiFetch } from '@/lib/api'
import type { Task, TaskStatus } from '@/types/domain'

export const taskService = {
  getProjectTasks: (
    projectId: number,
    filters?: {
      status?: TaskStatus;
      assigneeId?: string;
      reviewerId?: string;
      onlySubscribed?: boolean;
    }
  ): Promise<Task[]> => {
    const params = new URLSearchParams()
    if (filters?.status) params.append('status', filters.status)
    if (filters?.assigneeId) params.append('assigneeId', filters.assigneeId)
    if (filters?.reviewerId) params.append('reviewerId', filters.reviewerId)
    if (filters?.onlySubscribed !== undefined) params.append('onlySubscribed', String(filters.onlySubscribed))

    const queryString = params.toString()
    const path = `/projects/${projectId}/tasks` + (queryString ? `?${queryString}` : '')
    return apiFetch<Task[]>(path)
  },

  getTask: (projectId: number, taskId: number): Promise<Task> => {
    return apiFetch<Task>(`/projects/${projectId}/tasks/${taskId}`)
  },

  getMyTasks: (projectId: number): Promise<Task[]> => {
    return taskService.getProjectTasks(projectId, { assigneeId: 'user-1' })
  },

  getUserTasks: (projectId: number, userId: string): Promise<Task[]> => {
    return apiFetch<Task[]>(`/projects/${projectId}/tasks?assigneeId=${userId}`)
  },

  updateStatus: (projectId: number, taskId: number, status: TaskStatus): Promise<Task> => {
    return apiFetch<Task>(`/projects/${projectId}/tasks/${taskId}/status`, {
      method: 'PATCH',
      body: JSON.stringify({ status, updatedAt: new Date().toISOString() }),
    })
  },

  createTask: (
    projectId: number,
    taskData: { title: string; description: string; assigneeId?: string; reviewerId?: string }
  ): Promise<Task> => {
    // Backend (CreateTaskRequest) oczekuje tylko tych pól; status/jira/daty ustawia sam.
    return apiFetch<Task>(`/projects/${projectId}/tasks`, {
      method: 'POST',
      body: JSON.stringify({
        title: taskData.title,
        description: taskData.description,
        assigneeId: taskData.assigneeId ?? null,
        reviewerId: taskData.reviewerId ?? null,
      }),
    })
  },

  assignTask: (projectId: number, taskId: number, assigneeId: string | null): Promise<Task> => {
    return apiFetch<Task>(`/projects/${projectId}/tasks/${taskId}/assign`, {
      method: 'PATCH',
      body: JSON.stringify({ assigneeId, updatedAt: new Date().toISOString() }),
    })
  },

  assignReviewer: (projectId: number, taskId: number, reviewerId: string | null): Promise<Task> => {
    return apiFetch<Task>(`/projects/${projectId}/tasks/${taskId}/reviewer`, {
      method: 'PATCH',
      body: JSON.stringify({ reviewerId, updatedAt: new Date().toISOString() }),
    })
  },

  requestClose: (projectId: number, taskId: number): Promise<void> => {
    return apiFetch<void>(`/projects/${projectId}/tasks/${taskId}/request-close`, {
      method: 'POST',
    })
  }
}