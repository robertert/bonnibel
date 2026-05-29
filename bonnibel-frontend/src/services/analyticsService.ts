import { apiFetch } from '@/lib/api'
import type { AnalyticsOverview } from '@/types/domain'

// Backend (bonnibel-backend/app/modules/analytics) udostępnia jeden endpoint:
//   GET /api/projects/{projectId}/analytics/overview
// Base URL w apiFetch zawiera już /api, więc ścieżka jest bez wiodącego /api.
export const analyticsService = {
  getOverview: (projectId: number): Promise<AnalyticsOverview> =>
    apiFetch<AnalyticsOverview>(`/projects/${projectId}/analytics/overview`),
}
