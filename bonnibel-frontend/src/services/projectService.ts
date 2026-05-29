import { apiFetch } from '@/lib/api'

export interface ProjectSummary {
  projectId: number
  name: string
  description?: string
  ownerId?: string
}

export const projectService = {
  // Base URL w apiFetch zawiera już /api, więc ścieżka jest bez wiodącego /api.
  list: async (): Promise<ProjectSummary[]> => {
    return apiFetch<ProjectSummary[]>('/projects')
  },
}
