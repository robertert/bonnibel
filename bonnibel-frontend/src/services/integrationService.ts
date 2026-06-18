import { apiFetch } from '@/lib/api'
import type { IntegrationProvider } from '@/types/domain'

// Uwaga: moduł logic (backend) używa snake_case w kontrakcie integracji.
export interface ProjectIntegration {
  integration_id: number
  project_id: number
  provider: IntegrationProvider
  external_id: string
  is_active: boolean
}

export const integrationService = {
  list: (projectId: number): Promise<ProjectIntegration[]> =>
    apiFetch<ProjectIntegration[]>(`/project/${projectId}/integrations`),

  connect: (
    projectId: number,
    data: { provider: IntegrationProvider; external_id: string; access_token: string }
  ): Promise<ProjectIntegration> =>
    apiFetch<ProjectIntegration>(`/project/${projectId}/integrations`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  disconnect: (projectId: number, provider: IntegrationProvider): Promise<void> =>
    apiFetch<void>(`/project/${projectId}/integrations/${provider}`, { method: 'DELETE' }),
}