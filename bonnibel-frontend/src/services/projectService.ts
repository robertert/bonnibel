import { apiFetch } from '@/lib/api'
import { isUsingFastApiBackend } from '@/lib/env'

export type ProjectRole = 'OWNER' | 'DEVELOPER' | 'REVIEWER'

export interface ProjectSummary {
  projectId: number
  ownerId: string
  name: string
  description?: string | null
}

export interface ProjectMember {
  projectId: number
  userId: string
  role: ProjectRole
}

type ProjectApi = {
  id?: number
  project_id?: number
  projectId?: number
  owner_id?: string
  ownerId?: string
  name: string
  description?: string | null
}

type ProjectMemberApi = {
  id?: number | string
  project_id?: number
  projectId?: number
  user_id?: string
  userId?: string
  role: ProjectRole
}

const roleOptions: ProjectRole[] = ['OWNER', 'DEVELOPER', 'REVIEWER']

function projectBasePath() {
  return isUsingFastApiBackend() ? '/api/project' : '/projects'
}

function memberBasePath(projectId: number) {
  return isUsingFastApiBackend()
    ? `${projectBasePath()}/${projectId}/members`
    : `/projectMembers`
}

function mapProject(project: ProjectApi): ProjectSummary {
  return {
    projectId: project.project_id ?? project.projectId ?? project.id ?? 0,
    ownerId: project.owner_id ?? project.ownerId ?? '',
    name: project.name,
    description: project.description ?? null,
  }
}

function mapMember(member: ProjectMemberApi): ProjectMember {
  return {
    projectId: member.project_id ?? member.projectId ?? 0,
    userId: member.user_id ?? member.userId ?? '',
    role: member.role,
  }
}

export const projectService = {
  list: async (): Promise<ProjectSummary[]> => {
    const path = isUsingFastApiBackend() ? `${projectBasePath()}/my` : projectBasePath()
    const projects = await apiFetch<ProjectApi[]>(path)
    return projects.map(mapProject)
  },

  get: async (projectId: number): Promise<ProjectSummary> => {
    const project = await apiFetch<ProjectApi>(`${projectBasePath()}/${projectId}`)
    return mapProject(project)
  },

  create: async (data: {
    name: string
    description?: string | null
  }): Promise<ProjectSummary> => {
    const project = await apiFetch<ProjectApi>(`${projectBasePath()}/`, {
      method: 'POST',
      body: JSON.stringify({
        name: data.name,
        description: data.description || null,
      }),
    })

    return mapProject(project)
  },

  update: async (
    projectId: number,
    data: {
      name?: string
      description?: string | null
    },
  ): Promise<ProjectSummary> => {
    const project = await apiFetch<ProjectApi>(`${projectBasePath()}/${projectId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    })

    return mapProject(project)
  },

  remove: async (projectId: number): Promise<void> => {
    await apiFetch<void>(`${projectBasePath()}/${projectId}`, {
      method: 'DELETE',
    })
  },

  listMembers: async (projectId: number): Promise<ProjectMember[]> => {
    const path = isUsingFastApiBackend()
      ? memberBasePath(projectId)
      : `${memberBasePath(projectId)}?projectId=${projectId}`
    const members = await apiFetch<ProjectMemberApi[]>(path)
    return members.map(mapMember)
  },

  addMember: async (
    projectId: number,
    data: {
      userId: string
      role: ProjectRole
    },
  ): Promise<ProjectMember> => {
    const body = isUsingFastApiBackend()
      ? { user_id: data.userId, role: data.role }
      : { id: `${projectId}-${data.userId}`, projectId, userId: data.userId, role: data.role }

    const member = await apiFetch<ProjectMemberApi>(memberBasePath(projectId), {
      method: 'POST',
      body: JSON.stringify(body),
    })

    return mapMember(member)
  },

  changeMemberRole: async (
    projectId: number,
    userId: string,
    role: ProjectRole,
  ): Promise<ProjectMember> => {
    const path = isUsingFastApiBackend()
      ? `${memberBasePath(projectId)}/${userId}/role`
      : `${memberBasePath(projectId)}/${projectId}-${userId}`
    const member = await apiFetch<ProjectMemberApi>(path, {
      method: 'PATCH',
      body: JSON.stringify({ role }),
    })

    return mapMember(member)
  },

  removeMember: async (projectId: number, userId: string): Promise<void> => {
    const path = isUsingFastApiBackend()
      ? `${memberBasePath(projectId)}/${userId}`
      : `${memberBasePath(projectId)}/${projectId}-${userId}`
    await apiFetch<void>(path, {
      method: 'DELETE',
    })
  },
}

export { roleOptions as projectRoleOptions }
