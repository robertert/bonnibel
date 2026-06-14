import { apiFetch } from '@/lib/api'

export type ProjectRole = 'OWNER' | 'DEVELOPER' | 'REVIEWER'
export const projectRoleOptions: ProjectRole[] = ['OWNER', 'DEVELOPER', 'REVIEWER']

export interface ProjectSummary {
  projectId: number
  name: string
  description?: string
  ownerId?: string
}

export interface ProjectMember {
  projectId: number
  userId: string
  role: ProjectRole
}

// Moduł logic zwraca pola w snake_case — mapujemy na camelCase.
type ProjectMemberApi = {
  project_id?: number
  projectId?: number
  user_id?: string
  userId?: string
  role: ProjectRole
}

function mapMember(m: ProjectMemberApi): ProjectMember {
  return {
    projectId: m.project_id ?? m.projectId ?? 0,
    userId: m.user_id ?? m.userId ?? '',
    role: m.role,
  }
}

export const projectService = {
  // Base URL w apiFetch zawiera już /api, więc ścieżka jest bez wiodącego /api.
  list: async (): Promise<ProjectSummary[]> => {
    return apiFetch<ProjectSummary[]>('/projects')
  },

  get: async (projectId: number): Promise<ProjectSummary> => {
    const projects = await apiFetch<ProjectSummary[]>('/projects')
    const found = projects.find((p) => p.projectId === projectId)
    if (!found) throw new Error('Project not found')
    return found
  },

  listMembers: async (projectId: number): Promise<ProjectMember[]> => {
    const members = await apiFetch<ProjectMemberApi[]>(`/project/${projectId}/members`)
    return members.map(mapMember)
  },

  addMember: async (
    projectId: number,
    data: { userId: string; role: ProjectRole }
  ): Promise<ProjectMember> => {
    const member = await apiFetch<ProjectMemberApi>(`/project/${projectId}/members`, {
      method: 'POST',
      body: JSON.stringify({ user_id: data.userId, role: data.role }),
    })
    return mapMember(member)
  },

  changeMemberRole: async (
    projectId: number,
    userId: string,
    role: ProjectRole
  ): Promise<ProjectMember> => {
    const member = await apiFetch<ProjectMemberApi>(`/project/${projectId}/members/${userId}/role`, {
      method: 'PATCH',
      body: JSON.stringify({ role }),
    })
    return mapMember(member)
  },

  removeMember: async (projectId: number, userId: string): Promise<void> => {
    await apiFetch<void>(`/project/${projectId}/members/${userId}`, { method: 'DELETE' })
  },
}
