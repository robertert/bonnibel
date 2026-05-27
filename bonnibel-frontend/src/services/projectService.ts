import { apiFetch } from '@/lib/api'
import { isUsingFastApiBackend } from '@/lib/env'

export interface ProjectSummary {
  projectId: number
  name: string
  description?: string
  ownerId?: string
}

export const projectService = {
  list: async (): Promise<ProjectSummary[]> => {
    if (isUsingFastApiBackend()) {
      return apiFetch<ProjectSummary[]>('/api/projects')
    }
    // json-server: kolekcja `projects`
    return apiFetch<ProjectSummary[]>('/projects')
  },
}
