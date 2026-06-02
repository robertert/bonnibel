import { useState } from 'react'
import type { FormEvent } from 'react'
import { Link, useParams } from 'react-router-dom'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import {
  projectRoleOptions,
  projectService,
  type ProjectRole,
} from '@/services/projectService'

export default function MembersPage() {
  const { projectId } = useParams<{ projectId: string }>()
  const queryClient = useQueryClient()
  const numericProjectId = Number(projectId)
  const isValidProjectId = Number.isFinite(numericProjectId)
  const [userId, setUserId] = useState('')
  const [role, setRole] = useState<ProjectRole>('DEVELOPER')

  const projectQuery = useQuery({
    queryKey: ['projects', 'detail', numericProjectId],
    queryFn: () => projectService.get(numericProjectId),
    enabled: isValidProjectId,
  })

  const membersQuery = useQuery({
    queryKey: ['projects', 'members', numericProjectId],
    queryFn: () => projectService.listMembers(numericProjectId),
    enabled: isValidProjectId,
  })

  const invalidateMembers = () => {
    queryClient.invalidateQueries({ queryKey: ['projects', 'members', numericProjectId] })
  }

  const addMember = useMutation({
    mutationFn: () =>
      projectService.addMember(numericProjectId, {
        userId: userId.trim(),
        role,
      }),
    onSuccess: () => {
      invalidateMembers()
      setUserId('')
      setRole('DEVELOPER')
    },
  })

  const changeRole = useMutation({
    mutationFn: (data: { userId: string; role: ProjectRole }) =>
      projectService.changeMemberRole(numericProjectId, data.userId, data.role),
    onSuccess: invalidateMembers,
  })

  const removeMember = useMutation({
    mutationFn: (memberUserId: string) =>
      projectService.removeMember(numericProjectId, memberUserId),
    onSuccess: invalidateMembers,
  })

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()

    if (!userId.trim()) {
      return
    }

    addMember.mutate()
  }

  if (!isValidProjectId) {
    return (
      <div className="p-8">
        <p className="text-sm text-red-600">Nieprawidłowy identyfikator projektu.</p>
      </div>
    )
  }

  return (
    <div className="p-8 space-y-6">
      <Link
        to={`/projects/${numericProjectId}`}
        className="text-sm font-medium text-blue-600 hover:underline"
      >
        Wróć do projektu
      </Link>

      <header>
        <div className="text-xs font-medium uppercase tracking-wide text-gray-500">
          Projekt #{numericProjectId}
        </div>
        <h1 className="mt-1 text-2xl font-semibold text-gray-900">
          Członkowie projektu
        </h1>
        <p className="mt-2 text-sm text-gray-600">
          {projectQuery.data
            ? projectQuery.data.name
            : projectQuery.isLoading
              ? 'Wczytywanie nazwy projektu...'
              : 'Zarządzanie składem i rolami zespołu.'}
        </p>
      </header>

      <section className="border border-gray-200 rounded-lg bg-white p-5 shadow-sm">
        <h2 className="text-base font-semibold text-gray-900">Dodaj członka</h2>
        <form onSubmit={handleSubmit} className="mt-4 grid gap-4 md:grid-cols-[minmax(220px,1fr)_180px_auto] md:items-end">
          <label className="grid gap-1 text-sm">
            <span className="font-medium text-gray-700">User ID</span>
            <input
              value={userId}
              onChange={(event) => setUserId(event.target.value)}
              required
              className="rounded-md border border-gray-300 px-3 py-2 text-sm text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-200"
              placeholder="np. user-2"
            />
          </label>
          <label className="grid gap-1 text-sm">
            <span className="font-medium text-gray-700">Rola</span>
            <select
              value={role}
              onChange={(event) => setRole(event.target.value as ProjectRole)}
              className="rounded-md border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-200"
            >
              {projectRoleOptions.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          </label>
          <button
            type="submit"
            disabled={addMember.isPending || !userId.trim()}
            className="rounded-md bg-blue-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-blue-300"
          >
            {addMember.isPending ? 'Dodawanie...' : 'Dodaj'}
          </button>
        </form>
        {addMember.isError && (
          <p className="mt-3 text-sm text-red-600">
            Nie udało się dodać członka. Sprawdź user_id albo czy użytkownik już nie jest w projekcie.
          </p>
        )}
      </section>

      <section className="space-y-3">
        <div className="flex items-center justify-between gap-3">
          <h2 className="text-base font-semibold text-gray-900">Lista członków</h2>
          {membersQuery.isFetching && (
            <span className="text-xs font-medium text-gray-500">Odświeżanie...</span>
          )}
        </div>

        {membersQuery.isLoading ? (
          <p className="text-sm text-gray-500">Wczytywanie członków projektu...</p>
        ) : membersQuery.isError ? (
          <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
            Nie udało się pobrać członków projektu z endpointu
            {' '}
            <code>/api/project/{numericProjectId}/members</code>.
          </div>
        ) : !membersQuery.data || membersQuery.data.length === 0 ? (
          <div className="rounded-lg border border-dashed border-gray-300 bg-white p-6 text-sm text-gray-500">
            Ten projekt nie ma jeszcze członków.
          </div>
        ) : (
          <div className="overflow-hidden rounded-lg border border-gray-200 bg-white shadow-sm">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 text-left text-xs font-semibold uppercase text-gray-500">
                <tr>
                  <th className="px-4 py-3">User ID</th>
                  <th className="px-4 py-3">Rola</th>
                  <th className="px-4 py-3 text-right">Akcje</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {membersQuery.data.map((member) => (
                  <tr key={member.userId}>
                    <td className="px-4 py-3 font-mono text-gray-800">{member.userId}</td>
                    <td className="px-4 py-3">
                      <select
                        value={member.role}
                        disabled={changeRole.isPending}
                        onChange={(event) =>
                          changeRole.mutate({
                            userId: member.userId,
                            role: event.target.value as ProjectRole,
                          })
                        }
                        className="rounded-md border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-200"
                      >
                        {projectRoleOptions.map((option) => (
                          <option key={option} value={option}>
                            {option}
                          </option>
                        ))}
                      </select>
                    </td>
                    <td className="px-4 py-3 text-right">
                      <button
                        type="button"
                        disabled={removeMember.isPending || member.role === 'OWNER'}
                        onClick={() => removeMember.mutate(member.userId)}
                        className="rounded-md border border-red-200 px-3 py-2 text-sm font-semibold text-red-700 hover:bg-red-50 disabled:cursor-not-allowed disabled:border-gray-200 disabled:text-gray-400"
                        title={member.role === 'OWNER' ? 'Właściciela projektu nie można usunąć' : undefined}
                      >
                        Usuń
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {changeRole.isError && (
          <p className="text-sm text-red-600">Nie udało się zmienić roli członka.</p>
        )}
        {removeMember.isError && (
          <p className="text-sm text-red-600">Nie udało się usunąć członka projektu.</p>
        )}
      </section>
    </div>
  )
}
