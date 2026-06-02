import { useState } from 'react'
import type { FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { projectService } from '@/services/projectService'

export default function ProjectsListPage() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')

  const projectsQuery = useQuery({
    queryKey: ['projects', 'list'],
    queryFn: projectService.list,
  })

  const createProject = useMutation({
    mutationFn: projectService.create,
    onSuccess: (project) => {
      queryClient.invalidateQueries({ queryKey: ['projects', 'list'] })
      setName('')
      setDescription('')
      navigate(`/projects/${project.projectId}`)
    },
  })

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const trimmedName = name.trim()

    if (trimmedName.length < 3) {
      return
    }

    createProject.mutate({
      name: trimmedName,
      description: description.trim() || null,
    })
  }

  return (
    <div className="p-8 space-y-6">
      <header className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">Moje projekty</h1>
          <p className="mt-1 text-sm text-gray-500">
            Projekty, w których jesteś właścicielem albo członkiem zespołu.
          </p>
        </div>
      </header>

      <section className="border border-gray-200 rounded-lg bg-white p-5 shadow-sm">
        <h2 className="text-base font-semibold text-gray-900">Utwórz projekt</h2>
        <form onSubmit={handleSubmit} className="mt-4 grid gap-4 md:grid-cols-[minmax(180px,1fr)_minmax(240px,2fr)_auto] md:items-end">
          <label className="grid gap-1 text-sm">
            <span className="font-medium text-gray-700">Nazwa</span>
            <input
              value={name}
              onChange={(event) => setName(event.target.value)}
              minLength={3}
              maxLength={100}
              required
              className="rounded-md border border-gray-300 px-3 py-2 text-sm text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-200"
              placeholder="np. Bonnibel"
            />
          </label>
          <label className="grid gap-1 text-sm">
            <span className="font-medium text-gray-700">Opis</span>
            <input
              value={description}
              onChange={(event) => setDescription(event.target.value)}
              maxLength={500}
              className="rounded-md border border-gray-300 px-3 py-2 text-sm text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-200"
              placeholder="Krótki opis projektu"
            />
          </label>
          <button
            type="submit"
            disabled={createProject.isPending || name.trim().length < 3}
            className="rounded-md bg-blue-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-blue-300"
          >
            {createProject.isPending ? 'Tworzenie...' : 'Utwórz projekt'}
          </button>
        </form>
        {createProject.isError && (
          <p className="mt-3 text-sm text-red-600">
            Nie udało się utworzyć projektu. Sprawdź połączenie z API.
          </p>
        )}
      </section>

      <section className="space-y-3">
        <div className="flex items-center justify-between gap-3">
          <h2 className="text-base font-semibold text-gray-900">Lista projektów</h2>
          {projectsQuery.isFetching && (
            <span className="text-xs font-medium text-gray-500">Odświeżanie...</span>
          )}
        </div>

        {projectsQuery.isLoading ? (
          <p className="text-sm text-gray-500">Wczytywanie projektów...</p>
        ) : projectsQuery.isError ? (
          <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
            Nie udało się pobrać projektów. Upewnij się, że backend działa i używa endpointu
            {' '}
            <code>/api/project/my</code>.
          </div>
        ) : !projectsQuery.data || projectsQuery.data.length === 0 ? (
          <div className="rounded-lg border border-dashed border-gray-300 bg-white p-6 text-sm text-gray-500">
            Nie masz jeszcze żadnych projektów.
          </div>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {projectsQuery.data.map((project) => (
              <Link
                key={project.projectId}
                to={`/projects/${project.projectId}`}
                className="block rounded-lg border border-gray-200 bg-white p-5 shadow-sm transition hover:border-blue-300 hover:shadow-md"
              >
                <div className="flex items-start justify-between gap-3">
                  <h3 className="text-lg font-semibold text-gray-900">{project.name}</h3>
                  <span className="rounded-full bg-gray-100 px-2 py-1 text-xs font-medium text-gray-600">
                    #{project.projectId}
                  </span>
                </div>
                <p className="mt-2 min-h-10 text-sm leading-5 text-gray-600">
                  {project.description || 'Brak opisu projektu.'}
                </p>
                <div className="mt-4 text-xs text-gray-500">
                  Właściciel: <span className="font-mono">{project.ownerId || 'brak danych'}</span>
                </div>
              </Link>
            ))}
          </div>
        )}
      </section>
    </div>
  )
}
