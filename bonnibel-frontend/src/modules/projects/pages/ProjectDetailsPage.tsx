import { useState } from 'react'
import type { FormEvent } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { projectService } from '@/services/projectService'

export default function ProjectDetailsPage() {
  const { projectId } = useParams<{ projectId: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const numericProjectId = Number(projectId)
  const isValidProjectId = Number.isFinite(numericProjectId)
  const [draft, setDraft] = useState<{ name: string; description: string } | null>(null)

  const projectQuery = useQuery({
    queryKey: ['projects', 'detail', numericProjectId],
    queryFn: () => projectService.get(numericProjectId),
    enabled: isValidProjectId,
  })

  const formName = draft?.name ?? projectQuery.data?.name ?? ''
  const formDescription = draft?.description ?? projectQuery.data?.description ?? ''

  const updateProject = useMutation({
    mutationFn: () =>
      projectService.update(numericProjectId, {
        name: formName.trim(),
        description: formDescription.trim() || null,
      }),
    onSuccess: (project) => {
      queryClient.setQueryData(['projects', 'detail', numericProjectId], project)
      queryClient.invalidateQueries({ queryKey: ['projects', 'list'] })
      setDraft(null)
    },
  })

  const deleteProject = useMutation({
    mutationFn: () => projectService.remove(numericProjectId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects', 'list'] })
      navigate('/projects')
    },
  })

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()

    if (formName.trim().length < 3) {
      return
    }

    updateProject.mutate()
  }

  const handleDelete = () => {
    const confirmed = window.confirm('Usunąć ten projekt? Tej operacji nie da się cofnąć.')
    if (confirmed) {
      deleteProject.mutate()
    }
  }

  if (!isValidProjectId) {
    return (
      <div className="p-8">
        <p className="text-sm text-red-600">Nieprawidłowy identyfikator projektu.</p>
      </div>
    )
  }

  if (projectQuery.isLoading) {
    return (
      <div className="p-8">
        <p className="text-sm text-gray-500">Wczytywanie szczegółów projektu #{projectId}...</p>
      </div>
    )
  }

  if (projectQuery.isError || !projectQuery.data) {
    return (
      <div className="p-8 space-y-4">
        <Link to="/projects" className="text-sm font-medium text-blue-600 hover:underline">
          Wróć do projektów
        </Link>
        <p className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          Nie udało się pobrać projektu #{projectId}.
        </p>
      </div>
    )
  }

  return (
    <div className="p-8 space-y-6">
      <Link to="/projects" className="text-sm font-medium text-blue-600 hover:underline">
        Wróć do projektów
      </Link>

      <header className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <div className="text-xs font-medium uppercase tracking-wide text-gray-500">
            Projekt #{projectQuery.data.projectId}
          </div>
          <h1 className="mt-1 text-2xl font-semibold text-gray-900">{projectQuery.data.name}</h1>
          <p className="mt-2 max-w-3xl text-sm leading-6 text-gray-600">
            {projectQuery.data.description || 'Brak opisu projektu.'}
          </p>
          <p className="mt-2 text-xs text-gray-500">
            Właściciel: <span className="font-mono">{projectQuery.data.ownerId || 'brak danych'}</span>
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Link
            to={`/projects/${numericProjectId}/members`}
            className="rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-semibold text-gray-700 shadow-sm hover:bg-gray-50"
          >
            Członkowie
          </Link>
          <Link
            to={`/projects/${numericProjectId}/tasks`}
            className="rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-semibold text-gray-700 shadow-sm hover:bg-gray-50"
          >
            Zadania
          </Link>
        </div>
      </header>

      <section className="border border-gray-200 rounded-lg bg-white p-5 shadow-sm">
        <h2 className="text-base font-semibold text-gray-900">Edycja projektu</h2>
        <form onSubmit={handleSubmit} className="mt-4 space-y-4">
          <label className="grid gap-1 text-sm">
            <span className="font-medium text-gray-700">Nazwa</span>
            <input
              value={formName}
              onChange={(event) =>
                setDraft({ name: event.target.value, description: formDescription })
              }
              minLength={3}
              maxLength={100}
              required
              className="rounded-md border border-gray-300 px-3 py-2 text-sm text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-200"
            />
          </label>
          <label className="grid gap-1 text-sm">
            <span className="font-medium text-gray-700">Opis</span>
            <textarea
              value={formDescription}
              onChange={(event) =>
                setDraft({ name: formName, description: event.target.value })
              }
              maxLength={500}
              rows={5}
              className="resize-y rounded-md border border-gray-300 px-3 py-2 text-sm text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-200"
            />
          </label>
          <div className="flex flex-wrap items-center gap-3">
            <button
              type="submit"
              disabled={updateProject.isPending || formName.trim().length < 3}
              className="rounded-md bg-blue-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-blue-300"
            >
              {updateProject.isPending ? 'Zapisywanie...' : 'Zapisz zmiany'}
            </button>
            {updateProject.isSuccess && (
              <span className="text-sm text-green-700">Zapisano zmiany.</span>
            )}
            {updateProject.isError && (
              <span className="text-sm text-red-600">Nie udało się zapisać zmian.</span>
            )}
          </div>
        </form>
      </section>

      <section className="border border-red-200 rounded-lg bg-red-50 p-5">
        <h2 className="text-base font-semibold text-red-900">Usuwanie projektu</h2>
        <p className="mt-1 text-sm text-red-700">
          Usunięcie projektu skasuje go po stronie API razem z powiązanym kontekstem.
        </p>
        <button
          type="button"
          onClick={handleDelete}
          disabled={deleteProject.isPending}
          className="mt-4 rounded-md bg-red-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-red-700 disabled:cursor-not-allowed disabled:bg-red-300"
        >
          {deleteProject.isPending ? 'Usuwanie...' : 'Usuń projekt'}
        </button>
        {deleteProject.isError && (
          <p className="mt-3 text-sm text-red-700">Nie udało się usunąć projektu.</p>
        )}
      </section>
    </div>
  )
}
