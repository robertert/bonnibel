import { apiFetch } from '@/lib/api'
import type { PullRequest, TaskDoc, TaskHistory } from '@/types/domain'

// Docs, Pull Requesty i historia zadania (backend: moduły docs / pull_requests / task_history).
export const taskActivityService = {
  // --- Docs ---
  getDocs: (projectId: number, taskId: number): Promise<TaskDoc[]> =>
    apiFetch<TaskDoc[]>(`/projects/${projectId}/tasks/${taskId}/docs`),

  addDoc: (
    projectId: number,
    taskId: number,
    data: { title: string; url?: string; content?: string }
  ): Promise<TaskDoc> =>
    apiFetch<TaskDoc>(`/projects/${projectId}/tasks/${taskId}/docs`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // --- Pull Requests ---
  getPullRequests: (projectId: number, taskId: number): Promise<PullRequest[]> =>
    apiFetch<PullRequest[]>(`/projects/${projectId}/tasks/${taskId}/pull-requests`),

  createPullRequest: (
    projectId: number,
    taskId: number,
    data: { title: string; description?: string }
  ): Promise<PullRequest> =>
    apiFetch<PullRequest>(`/projects/${projectId}/tasks/${taskId}/pull-requests`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  approvePullRequest: (prId: number): Promise<PullRequest> =>
    apiFetch<PullRequest>(`/pull-requests/${prId}/approve`, { method: 'POST' }),

  declinePullRequest: (prId: number): Promise<PullRequest> =>
    apiFetch<PullRequest>(`/pull-requests/${prId}/decline`, { method: 'POST' }),

  // --- History ---
  getHistory: (projectId: number, taskId: number): Promise<TaskHistory[]> =>
    apiFetch<TaskHistory[]>(`/projects/${projectId}/tasks/${taskId}/history`),
}
