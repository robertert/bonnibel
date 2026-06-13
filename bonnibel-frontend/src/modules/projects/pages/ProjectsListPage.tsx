import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { projectService, type ProjectSummary } from '@/services/projectService'

export default function ProjectsListPage() {
  const [projects, setProjects] = useState<ProjectSummary[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    projectService.list()
      .then(setProjects)
      .catch((e) => setError(String(e)))
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="p-8">
      <h1 className="text-2xl font-semibold mb-6">Moje projekty</h1>

      {loading && <p className="text-gray-500">Wczytywanie…</p>}
      {error && <p className="text-red-600">Nie udało się pobrać projektów.</p>}
      {!loading && !error && projects.length === 0 && (
        <p className="text-gray-500">Brak projektów.</p>
      )}

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {projects.map((p) => (
          <Link
            key={p.projectId}
            to={`/projects/${p.projectId}`}
            className="block rounded-xl border border-gray-200 bg-white p-5 shadow-sm hover:shadow-md transition-shadow"
          >
            <h2 className="text-lg font-semibold text-gray-900">{p.name}</h2>
            {p.description && <p className="mt-1 text-sm text-gray-500 line-clamp-2">{p.description}</p>}
            <span className="mt-3 inline-block text-xs text-blue-600">Otwórz projekt →</span>
          </Link>
        ))}
      </div>
    </div>
  )
}
