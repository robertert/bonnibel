import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { projectService, type ProjectSummary, type ProjectRole } from '@/services/projectService'

export default function ProjectDetailsPage() {
  const { projectId } = useParams<{ projectId: string }>()
  const pid = Number(projectId)
  
  const [project, setProject] = useState<ProjectSummary | null>(null)
  const [userRole, setUserRole] = useState<ProjectRole | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const currentUserId = localStorage.getItem('userId')
    
    // Pobieramy równolegle dane projektu i listę członków
    Promise.all([
      projectService.list(),
      projectService.listMembers(pid)
    ])
      .then(([projects, members]) => {
        setProject(projects.find((p) => p.projectId === pid) ?? null)
        
        // Szukamy zalogowanego użytkownika na liście członków projektu
        const me = members.find(m => m.userId === currentUserId)
        if (me) {
          setUserRole(me.role)
        }
      })
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [pid])

  // Dynamiczne budowanie linków - Integracje widzi tylko OWNER
  const links = [
    { to: `/projects/${projectId}/tasks`, label: 'Zadania' },
    { to: `/projects/${projectId}/members`, label: 'Członkowie' },
    { to: `/projects/${projectId}/analytics`, label: 'Analityka' },
  ]
  
  if (userRole === 'OWNER') {
    links.push({ to: `/projects/${projectId}/integrations`, label: 'Integracje' })
  }

  if (loading) return <div className="p-8 text-gray-500">Wczytywanie…</div>

  return (
    <div className="p-8 max-w-3xl">
      <Link to="/projects" className="text-sm text-gray-500 hover:text-gray-700">← Powrót do projektów</Link>

      <h1 className="mt-3 text-2xl font-semibold text-gray-900">
        {project ? project.name : `Projekt #${projectId}`}
      </h1>
      {project?.description && <p className="mt-2 text-gray-600">{project.description}</p>}
      {project?.ownerId && <p className="mt-1 text-xs text-gray-400">Właściciel: {project.ownerId}</p>}

      <div className="mt-6 grid grid-cols-2 sm:grid-cols-4 gap-3">
        {links.map((l) => (
          <Link
            key={l.to}
            to={l.to}
            className="rounded-lg border border-gray-200 bg-white px-4 py-3 text-center text-sm font-medium text-gray-700 shadow-sm hover:shadow-md hover:text-blue-600 transition"
          >
            {l.label}
          </Link>
        ))}
      </div>
    </div>
  )
}