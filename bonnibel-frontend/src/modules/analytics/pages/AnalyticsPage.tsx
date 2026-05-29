import { useMemo, useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { analyticsService } from '@/services/analyticsService'
import { projectService } from '@/services/projectService'
import StatCard from '../components/StatCard'
import BarList from '../components/BarList'

function useResolvedProjectId(): {
  projectId: number | null
  projects: { projectId: number; name: string }[]
  setProjectId: (id: number) => void
  loading: boolean
} {
  const { projectId: routeId } = useParams<{ projectId?: string }>()
  const [selected, setSelected] = useState<number | null>(
    routeId ? Number(routeId) : null
  )

  const { data: projects = [], isLoading } = useQuery({
    queryKey: ['projects', 'list'],
    queryFn: projectService.list,
    enabled: !routeId,
  })

  useEffect(() => {
    if (!selected && !routeId && projects.length > 0) {
      setSelected(projects[0].projectId)
    }
  }, [projects, selected, routeId])

  return {
    projectId: routeId ? Number(routeId) : selected,
    projects: projects.map((p) => ({ projectId: p.projectId, name: p.name })),
    setProjectId: setSelected,
    loading: isLoading,
  }
}

export default function AnalyticsPage() {
  const { projectId, projects, setProjectId, loading } = useResolvedProjectId()
  const { projectId: routeId } = useParams<{ projectId?: string }>()

  const overview = useQuery({
    queryKey: ['analytics', 'overview', projectId],
    queryFn: () => analyticsService.getOverview(projectId!),
    enabled: projectId != null,
  })

  const data = overview.data
  const byStatus = data?.tasksByStatus ?? {}

  const toEntries = (rec: Record<string, number> | undefined) =>
    Object.entries(rec ?? {})
      .map(([label, value]) => ({ label: label || '(brak)', value }))
      .sort((a, b) => b.value - a.value)

  const assigneeEntries = useMemo(() => toEntries(data?.tasksByUser), [data])
  const reviewerEntries = useMemo(() => toEntries(data?.tasksByReviewer), [data])
  const wipEntries = useMemo(() => toEntries(data?.wipByUser), [data])
  const throughputEntries = useMemo(
    () =>
      Object.entries(data?.throughputByDay ?? {})
        .map(([label, value]) => ({ label, value }))
        .sort((a, b) => a.label.localeCompare(b.label)),
    [data]
  )

  if (projectId == null) {
    return (
      <div className="p-8">
        <h1 className="text-2xl font-semibold mb-4">Analityka projektu</h1>
        {loading ? (
          <p className="text-gray-500">Wczytywanie listy projektów…</p>
        ) : (
          <p className="text-gray-500">Brak projektów do analizy.</p>
        )}
      </div>
    )
  }

  return (
    <div className="p-8 space-y-6">
      <header className="flex flex-wrap items-center justify-between gap-4">
        <h1 className="text-2xl font-semibold">Analityka projektu</h1>
        {!routeId && projects.length > 0 && (
          <label className="text-sm flex items-center gap-2">
            <span className="text-gray-600">Projekt:</span>
            <select
              value={projectId}
              onChange={(e) => setProjectId(Number(e.target.value))}
              className="px-3 py-2 border border-gray-200 rounded-full text-sm bg-white text-gray-900 shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-200"
            >
              {projects.map((p) => (
                <option key={p.projectId} value={p.projectId}>
                  {p.name} (#{p.projectId})
                </option>
              ))}
            </select>
          </label>
        )}
      </header>

      {overview.isError && (
        <p className="text-sm text-red-600">Nie udało się pobrać analityki projektu.</p>
      )}

      <section className="grid grid-cols-2 md:grid-cols-3 gap-3">
        <StatCard label="Wszystkich zadań" value={data?.taskCount ?? '—'} tone="info" />
        <StatCard label="Otwarte" value={data?.openTasks ?? '—'} tone="warning" />
        <StatCard label="Zakończone" value={data?.doneTasks ?? '—'} tone="success" />
      </section>

      <section className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <StatCard
          label="Ukończenie"
          value={data ? `${data.completionRate}%` : '—'}
          tone="success"
        />
        <StatCard label="Nieprzypisane" value={data?.unassignedTasks ?? '—'} tone="warning" />
        <StatCard label="Utknięte (>7 dni)" value={data?.staleTasks ?? '—'} tone="warning" />
        <StatCard
          label="Śr. czas realizacji"
          value={data?.avgCycleTimeHours != null ? `${data.avgCycleTimeHours} h` : '—'}
          tone="info"
        />
      </section>

      <section className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <StatCard label="Do zrobienia" value={byStatus.TODO ?? 0} />
        <StatCard label="W trakcie" value={byStatus.IN_PROGRESS ?? 0} tone="warning" />
        <StatCard label="Review" value={byStatus.IN_REVIEW ?? 0} />
        <StatCard label="Zakończone" value={byStatus.DONE ?? 0} tone="success" />
      </section>

      <section className="grid md:grid-cols-2 gap-6">
        <div className="border border-gray-200 rounded-2xl bg-white p-5 shadow-sm">
          <h2 className="font-semibold text-gray-800 mb-3">Zadania per użytkownik</h2>
          {overview.isLoading ? (
            <p className="text-sm text-gray-500">Wczytywanie…</p>
          ) : (
            <BarList entries={assigneeEntries} emptyText="Brak przypisanych zadań." />
          )}
        </div>

        <div className="border border-gray-200 rounded-2xl bg-white p-5 shadow-sm">
          <h2 className="font-semibold text-gray-800 mb-3">Zadania per recenzent</h2>
          {overview.isLoading ? (
            <p className="text-sm text-gray-500">Wczytywanie…</p>
          ) : (
            <BarList entries={reviewerEntries} emptyText="Brak przypisanych recenzentów." />
          )}
        </div>

        <div className="border border-gray-200 rounded-2xl bg-white p-5 shadow-sm">
          <h2 className="font-semibold text-gray-800 mb-3">W toku per użytkownik (WIP)</h2>
          {overview.isLoading ? (
            <p className="text-sm text-gray-500">Wczytywanie…</p>
          ) : (
            <BarList entries={wipEntries} emptyText="Nikt nie ma zadań w toku." />
          )}
        </div>

        <div className="border border-gray-200 rounded-2xl bg-white p-5 shadow-sm">
          <h2 className="font-semibold text-gray-800 mb-3">Zakończone w czasie</h2>
          {overview.isLoading ? (
            <p className="text-sm text-gray-500">Wczytywanie…</p>
          ) : (
            <BarList entries={throughputEntries} emptyText="Brak zakończonych zadań." />
          )}
        </div>
      </section>
    </div>
  )
}
