import { apiFetch } from '@/lib/api'
import { isUsingFastApiBackend } from '@/lib/env'
import type { ProjectMember, PullRequest, PullRequestStatus, Task } from '@/types/domain'

interface MockProject {
  projectId: number
  ownerId?: string
}

function apiPath(path: string): string {
  return path
}

export const pullRequestService = {
  listForReviewsScope: async (
    userId: string,
    filters: { status?: PullRequestStatus } = {}
  ): Promise<PullRequest[]> => {
    if (isUsingFastApiBackend()) {
      const params = new URLSearchParams({ mode: 'reviews' })
      if (filters.status) params.append('status', filters.status)
      return apiFetch<PullRequest[]>(apiPath(`/users/${userId}/pull-requests?${params.toString()}`))
    }

    const [pullRequests, tasks, projects, members] = await Promise.all([
      apiFetch<PullRequest[]>('/pullRequests'),
      apiFetch<Task[]>('/tasks'),
      apiFetch<MockProject[]>('/projects'),
      apiFetch<ProjectMember[]>('/projectMembers').catch(() => []),
    ])
    const tasksById = new Map(tasks.map((task) => [task.taskId, task]))
    const projectRoles = new Map(
      members
        .filter((member) => member.userId === userId)
        .map((member) => [member.projectId, member.role])
    )

    return pullRequests
      .map((pullRequest) => {
        const task = tasksById.get(pullRequest.taskId)
        return {
          ...pullRequest,
          projectId: pullRequest.projectId ?? task?.projectId ?? null,
          assigneeId: task?.assigneeId ?? null,
        }
      })
      .filter((pullRequest) => {
        if (filters.status && pullRequest.status !== filters.status) return false

        const projectId = pullRequest.projectId
        if (!projectId) {
          return pullRequest.reviewerId === userId || pullRequest.assigneeId === userId
        }

        const role = projectRoles.get(projectId)
        const project = projects.find((item) => item.projectId === projectId)
        if (role === 'OWNER' || project?.ownerId === userId) return true
        if (role === 'REVIEWER') return pullRequest.reviewerId === userId
        if (role === 'DEVELOPER') return pullRequest.assigneeId === userId
        return pullRequest.reviewerId === userId || pullRequest.assigneeId === userId
      })
      .sort((a, b) => Date.parse(b.createdAt) - Date.parse(a.createdAt))
  },

  listForReview: (
    projectId: number,
    filters: { reviewerId?: string; status?: PullRequestStatus } = {}
  ): Promise<PullRequest[]> => {
    const params = new URLSearchParams()
    if (filters.reviewerId) params.append('reviewerId', filters.reviewerId)
    if (filters.status) params.append('status', filters.status)

    if (!isUsingFastApiBackend()) {
      const mockParams = new URLSearchParams(params)
      mockParams.append('projectId', String(projectId))
      return apiFetch<PullRequest[]>(`/pullRequests?${mockParams.toString()}`)
    }

    const queryString = params.toString()
    const path = `/projects/${projectId}/pull-requests${queryString ? `?${queryString}` : ''}`
    return apiFetch<PullRequest[]>(apiPath(path))
  },

  getTaskPullRequest: async (projectId: number, taskId: number): Promise<PullRequest | null> => {
    const pullRequests = await pullRequestService.listForReview(projectId)
    return pullRequests.find((pullRequest) => pullRequest.taskId === taskId) ?? null
  },

  getPullRequest: (projectId: number, pullRequestId: number): Promise<PullRequest> => {
    if (!isUsingFastApiBackend()) {
      return apiFetch<PullRequest>(`/pullRequests/${pullRequestId}`)
    }

    return apiFetch<PullRequest>(apiPath(`/projects/${projectId}/pull-requests/${pullRequestId}`))
  },

  createPullRequest: (
    projectId: number,
    taskId: number,
    draft?: Pick<PullRequest, 'title' | 'url' | 'reviewerId'> & { externalId?: string }
  ): Promise<PullRequest> => {
    const isFastApi = isUsingFastApiBackend()
    const mockId = Date.now()
    return apiFetch<PullRequest>(isFastApi ? apiPath(`/projects/${projectId}/tasks/${taskId}/pull-requests`) : '/pullRequests', {
      method: 'POST',
      body: JSON.stringify(
        isFastApi
          ? {}
          : {
              id: mockId,
              pullRequestId: mockId,
              projectId,
              taskId,
              externalId: draft?.externalId ?? `mock-pr-${taskId}`,
              title: draft?.title ?? `PR for task #${taskId}`,
              url: draft?.url ?? `https://github.com/example/bonnibel/pull/${taskId}`,
              reviewerId: draft?.reviewerId ?? 'user-1',
              status: 'OPEN',
              createdAt: new Date().toISOString(),
              updatedAt: new Date().toISOString(),
              mergedAt: null,
            }
      ),
    })
  },

  acceptReview: (projectId: number, pullRequestId: number): Promise<PullRequest> => {
    if (!isUsingFastApiBackend()) {
      return apiFetch<PullRequest>(`/pullRequests/${pullRequestId}`, {
        method: 'PATCH',
        body: JSON.stringify({
          status: 'MERGED',
          updatedAt: new Date().toISOString(),
          mergedAt: new Date().toISOString(),
        }),
      })
    }

    return apiFetch<PullRequest>(apiPath(`/projects/${projectId}/pull-requests/${pullRequestId}/accept`), {
      method: 'POST',
    })
  },

  rejectReview: (projectId: number, pullRequestId: number, reason: string): Promise<PullRequest> => {
    if (!isUsingFastApiBackend()) {
      return apiFetch<PullRequest>(`/pullRequests/${pullRequestId}`, {
        method: 'PATCH',
        body: JSON.stringify({
          status: 'CLOSED',
          rejectionReason: reason,
          updatedAt: new Date().toISOString(),
        }),
      })
    }

    return apiFetch<PullRequest>(apiPath(`/projects/${projectId}/pull-requests/${pullRequestId}/reject`), {
      method: 'POST',
      body: JSON.stringify({ reason }),
    })
  },
}
