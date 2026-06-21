import { apiFetch } from '@/lib/api'
import { isUsingFastApiBackend } from '@/lib/env'
import type { TaskDoc } from '@/types/domain'

function apiPath(path: string): string {
  return path
}

export const docsService = {
  getTaskDocs: async (projectId: number, taskId: number): Promise<TaskDoc> => {
    if (isUsingFastApiBackend()) {
      return apiFetch<TaskDoc>(apiPath(`/projects/${projectId}/tasks/${taskId}/docs`))
    }

    const docs = await apiFetch<TaskDoc[]>(`/docs?projectId=${projectId}&taskId=${taskId}`)
    if (!docs[0]) {
      throw new Error('DOCS_NOT_FOUND')
    }
    return docs[0]
  },

  getProjectDocs: (projectId: number): Promise<TaskDoc[]> => {
    if (!isUsingFastApiBackend()) {
      return apiFetch<TaskDoc[]>(`/docs?projectId=${projectId}`)
    }

    return apiFetch<TaskDoc[]>(apiPath(`/projects/${projectId}/docs`))
  },

  addTaskDocs: (
    projectId: number,
    taskId: number,
    data: { title: string; url: string }
  ): Promise<TaskDoc> => {
    return apiFetch<TaskDoc>(isUsingFastApiBackend() ? apiPath(`/projects/${projectId}/tasks/${taskId}/docs`) : '/docs', {
      method: 'POST',
      body: JSON.stringify({
        ...data,
        projectId,
        taskId,
        externalId: null,
      }),
    })
  },

  updateTaskDocs: (
    projectId: number,
    taskId: number,
    docsId: number,
    data: { title: string; url: string }
  ): Promise<TaskDoc> => {
    if (!isUsingFastApiBackend()) {
      return apiFetch<TaskDoc>(`/docs/${docsId}`, {
        method: 'PATCH',
        body: JSON.stringify(data),
      })
    }

    return apiFetch<TaskDoc>(apiPath(`/projects/${projectId}/tasks/${taskId}/docs`), {
      method: 'PUT',
      body: JSON.stringify(data),
    })
  },
}
