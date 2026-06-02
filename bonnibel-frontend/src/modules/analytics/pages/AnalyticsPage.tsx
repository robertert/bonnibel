import { useMemo, useState } from 'react'
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

  return {
    projectId: routeId ? Number(routeId) : selected ?? projects[0]?.projectId ?? null,
    projects: projects.map((p) => ({ projectId: p.projectId, name: p.name })),
    setProjectId: setSelected,
    loading: isLoading,
  }
}

export default function AnalyticsPage() {
  const { projectId, projects, setProjectId, loading } = useResolvedProjectId()
  const { projectId: routeId } = useParams<{ projectId?: string }>()

  const count = useQuery({
    queryKey: ['analytics', 'count', projectId],
    queryFn: () => analyticsService.getTaskCount(projectId!),
    enabled: projectId != null,
  })

  const byStatus = useQuery({
    queryKey: ['analytics', 'byStatus', projectId],
    queryFn: () => analyticsService.getTaskCountByStatus(projectId!),
    enabled: projectId != null,
  })

  const byAssignee = useQuery({
    queryKey: ['analytics', 'byAssignee', projectId],
    queryFn: () => analyticsService.getTaskCountByAssignee(projectId!),
    enabled: projectId != null,
  })

  const closed = useQuery({
    queryKey: ['analytics', 'closed', projectId],
    queryFn: () => analyticsService.getClosedTaskHistory(projectId!),
    enabled: projectId != null,
  })

  const commits = useQuery({
    queryKey: ['analytics', 'commits', projectId],
    queryFn: () => analyticsService.getCommits(projectId!),
    enabled: projectId != null,
  })

  const assigneeEntries = useMemo(() => {
    return Object.entries(byAssignee.data ?? {})
      .map(([label, value]) => ({ label, value }))
      .sort((a, b) => b.value - a.value)
  }, [byAssignee.data])

  const commitEntries = useMemo(() => {
    return Object.entries(commits.data?.byActor ?? {})
      .map(([label, value]) => ({ label, value }))
      .sort((a, b) => b.value - a.value)
  }, [commits.data])

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

      <section className="grid grid-cols-2 md:grid-cols-5 gap-3">
        <StatCard label="Wszystkich zadań" value={count.data?.taskCount ?? '—'} tone="info" />
        <StatCard label="Do zrobienia" value={byStatus.data?.TODO ?? '—'} />
        <StatCard label="W trakcie" value={byStatus.data?.IN_PROGRESS ?? '—'} tone="warning" />
        <StatCard label="Review" value={byStatus.data?.IN_REVIEW ?? '—'} />
        <StatCard label="Zakończone" value={byStatus.data?.DONE ?? '—'} tone="success" />
      </section>

      <section className="grid md:grid-cols-2 gap-6">
        <div className="border border-gray-200 rounded-2xl bg-white p-5 shadow-sm">
          <h2 className="font-semibold text-gray-800 mb-3">Zadania per użytkownik</h2>
          {byAssignee.isLoading ? (
            <p className="text-sm text-gray-500">Wczytywanie…</p>
          ) : (
            <BarList entries={assigneeEntries} emptyText="Brak przypisanych zadań." />
          )}
        </div>

        <div className="border border-gray-200 rounded-2xl bg-white p-5 shadow-sm">
          <h2 className="font-semibold text-gray-800 mb-3">
            Commity ({commits.data?.commitCount ?? 0})
          </h2>
          {commits.isLoading ? (
            <p className="text-sm text-gray-500">Wczytywanie…</p>
          ) : (
            <BarList entries={commitEntries} emptyText="Brak commitów w historii projektu." />
          )}
        </div>
      </section>

      <section className="border border-gray-200 rounded-2xl bg-white p-5 shadow-sm">
        <h2 className="font-semibold text-gray-800 mb-3">Historia zamkniętych zadań</h2>
        {closed.isLoading ? (
          <p className="text-sm text-gray-500">Wczytywanie…</p>
        ) : !closed.data || closed.data.length === 0 ? (
          <p className="text-sm text-gray-500">Brak zamkniętych zadań w tym projekcie.</p>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-gray-500 border-b">
                <th className="py-2 pr-3">Task</th>
                <th className="py-2 pr-3">Typ</th>
                <th className="py-2 pr-3">Actor</th>
                <th className="py-2 pr-3">Tytuł</th>
                <th className="py-2">Link</th>
              </tr>
            </thead>
            <tbody>
              {closed.data.map((h) => (
                <tr key={h.eventId} className="border-b last:border-b-0">
                  <td className="py-2 pr-3 font-mono">#{h.taskId}</td>
                  <td className="py-2 pr-3">{h.type}</td>
                  <td className="py-2 pr-3">{h.actorId}</td>
                  <td className="py-2 pr-3">{h.title}</td>
                  <td className="py-2">
                    {h.url ? (
                      <a
                        href={h.url}
                        target="_blank"
                        rel="noreferrer"
                        className="text-blue-600 hover:underline"
                      >
                        otwórz
                      </a>
                    ) : (
                      <span className="text-gray-400">—</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>
    </div>
  )
}
