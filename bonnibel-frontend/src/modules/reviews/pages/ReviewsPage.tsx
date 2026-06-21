import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { docsService } from '@/services/docsService'
import { pullRequestService } from '@/services/pullRequestService'
import { useAuthStore } from '@/modules/auth/store/authStore'
import type { PullRequest, TaskDoc } from '@/types/domain'

export default function ReviewsPage() {
  const userId = useAuthStore((state) => state.userId) ?? 'user-1'
  const [pullRequests, setPullRequests] = useState<PullRequest[]>([])
  const [docs, setDocs] = useState<TaskDoc[]>([])
  const [loading, setLoading] = useState(true)
  const [actionId, setActionId] = useState<number | null>(null)
  const [rejectingId, setRejectingId] = useState<number | null>(null)
  const [rejectReasons, setRejectReasons] = useState<Record<number, string>>({})
  const [selectedProjectId, setSelectedProjectId] = useState<number | 'ALL'>('ALL')
  const [message, setMessage] = useState<string | null>(null)

  useEffect(() => {
    setLoading(true)
    pullRequestService.listForReviewsScope(userId, { status: 'OPEN' })
      .then(async (loadedPullRequests) => {
        setPullRequests(loadedPullRequests)
        const projectIds = Array.from(
          new Set(
            loadedPullRequests
              .map((pullRequest) => pullRequest.projectId)
              .filter((projectId): projectId is number => typeof projectId === 'number')
          )
        )
        const loadedDocs = await Promise.all(
          projectIds.map((projectId) => docsService.getProjectDocs(projectId).catch(() => []))
        )
        setDocs(loadedDocs.flat())
      })
      .catch((err) => {
        console.error(err)
        setMessage('Nie udalo sie wczytac pull requestow do review.')
      })
      .finally(() => setLoading(false))
  }, [userId])

  const docsByTaskId = useMemo(() => {
    return docs.reduce<Record<number, TaskDoc>>((acc, taskDocs) => {
      acc[taskDocs.taskId] = taskDocs
      return acc
    }, {})
  }, [docs])

  const projectOptions = useMemo(() => {
    return Array.from(
      new Set(
        pullRequests
          .map((pullRequest) => pullRequest.projectId)
          .filter((projectId): projectId is number => typeof projectId === 'number')
      )
    ).sort((a, b) => a - b)
  }, [pullRequests])

  const visiblePullRequests = useMemo(() => {
    if (selectedProjectId === 'ALL') return pullRequests
    return pullRequests.filter((pullRequest) => pullRequest.projectId === selectedProjectId)
  }, [pullRequests, selectedProjectId])

  const handleAccept = async (pullRequest: PullRequest) => {
    if (!pullRequest.projectId) {
      setMessage('Brakuje projectId dla tego pull requesta.')
      return
    }

    setActionId(pullRequest.pullRequestId)
    setMessage(null)
    try {
      const updated = await pullRequestService.acceptReview(pullRequest.projectId, pullRequest.pullRequestId)
      setPullRequests((current) =>
        current
          .map((item) =>
            item.pullRequestId === pullRequest.pullRequestId
              ? { ...updated, projectId: pullRequest.projectId, assigneeId: pullRequest.assigneeId }
              : item
          )
          .filter((item) => item.status === 'OPEN')
      )
      setMessage('Review zostalo zaakceptowane.')
    } catch (err) {
      console.error('Nie udalo sie zaakceptowac review', err)
      setMessage('Nie udalo sie zaakceptowac review.')
    } finally {
      setActionId(null)
    }
  }

  const handleReject = async (pullRequest: PullRequest) => {
    if (!pullRequest.projectId) {
      setMessage('Brakuje projectId dla tego pull requesta.')
      return
    }
    const reason = rejectReasons[pullRequest.pullRequestId]?.trim()
    if (!reason) {
      setMessage('Podaj powod odrzucenia review.')
      return
    }

    setActionId(pullRequest.pullRequestId)
    setMessage(null)
    try {
      const updated = await pullRequestService.rejectReview(pullRequest.projectId, pullRequest.pullRequestId, reason)
      setPullRequests((current) =>
        current
          .map((item) =>
            item.pullRequestId === pullRequest.pullRequestId
              ? { ...updated, projectId: pullRequest.projectId, assigneeId: pullRequest.assigneeId }
              : item
          )
          .filter((item) => item.status === 'OPEN')
      )
      setRejectingId(null)
      setRejectReasons((current) => ({ ...current, [pullRequest.pullRequestId]: '' }))
      setMessage('Review zostalo odrzucone.')
    } catch (err) {
      console.error('Nie udalo sie odrzucic review', err)
      setMessage('Nie udalo sie odrzucic review.')
    } finally {
      setActionId(null)
    }
  }

  return (
    <div className="p-8 space-y-6">
      <header className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold">Pull Requesty</h1>
        </div>
        {projectOptions.length > 0 && (
          <label className="text-sm flex items-center gap-2">
            <span className="text-gray-600">Projekt:</span>
            <select
              value={selectedProjectId}
              onChange={(e) => setSelectedProjectId(e.target.value === 'ALL' ? 'ALL' : Number(e.target.value))}
              className="px-3 py-2 border border-gray-200 rounded-full text-sm bg-white text-gray-900 shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-200"
            >
              <option value="ALL">Wszystkie projekty</option>
              {projectOptions.map((projectId) => (
                <option key={projectId} value={projectId}>
                  Projekt #{projectId}
                </option>
              ))}
            </select>
          </label>
        )}
      </header>

      {message && (
        <div className="border border-gray-200 bg-white rounded-lg px-4 py-3 text-sm text-gray-700 shadow-sm">
          {message}
        </div>
      )}

      {loading ? (
        <div className="border border-gray-200 rounded-2xl bg-white p-5 shadow-sm text-sm text-gray-500">
          Wczytywanie pull requestow...
        </div>
      ) : pullRequests.length === 0 ? (
        <div className="border border-gray-200 rounded-2xl bg-white p-5 shadow-sm">
          <h2 className="font-semibold text-gray-800 mb-2">Brak PR do wyswietlenia</h2>
          <p className="text-sm text-gray-500">Nie ma otwartych pull requestow pasujacych do Twojej roli.</p>
        </div>
      ) : visiblePullRequests.length === 0 ? (
        <div className="border border-gray-200 rounded-2xl bg-white p-5 shadow-sm">
          <h2 className="font-semibold text-gray-800 mb-2">Brak PR w tym projekcie</h2>
          <p className="text-sm text-gray-500">W wybranym projekcie nie ma otwartych pull requestow pasujacych do Twojej roli.</p>
        </div>
      ) : (
        <div className="grid gap-4">
          {visiblePullRequests.map((pullRequest) => {
            const taskDocs = docsByTaskId[pullRequest.taskId]
            const isWorking = actionId === pullRequest.pullRequestId
            const isRejecting = rejectingId === pullRequest.pullRequestId
            const projectId = pullRequest.projectId

            return (
              <article key={pullRequest.pullRequestId} className="border border-gray-200 rounded-2xl bg-white p-5 shadow-sm">
                <div className="flex flex-wrap items-start justify-between gap-4">
                  <div>
                    <div className="flex flex-wrap items-center gap-2 mb-2">
                      <span className="px-2 py-1 rounded-full bg-blue-50 text-blue-700 text-xs font-semibold">
                        PR #{pullRequest.pullRequestId}
                      </span>
                      <span className="px-2 py-1 rounded-full bg-orange-50 text-orange-700 text-xs font-semibold">
                        {pullRequest.status}
                      </span>
                      {projectId && <span className="text-xs text-gray-500">Projekt #{projectId}</span>}
                      <span className="text-xs text-gray-500">Task #{pullRequest.taskId}</span>
                    </div>
                    <h2 className="text-lg font-semibold text-gray-900">{pullRequest.title}</h2>
                    <p className="text-sm text-gray-500 mt-1">
                      Reviewer: {pullRequest.reviewerId ?? 'brak'} | Assignee: {pullRequest.assigneeId ?? 'brak'}
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    <button
                      type="button"
                      disabled={isWorking || !projectId}
                      onClick={() => handleAccept(pullRequest)}
                      className="px-3 py-2 rounded-md bg-green-600 text-white text-sm font-semibold disabled:opacity-60"
                    >
                      {isWorking ? 'Zapisywanie...' : 'Approve'}
                    </button>
                    <button
                      type="button"
                      disabled={isWorking || !projectId}
                      onClick={() => setRejectingId(isRejecting ? null : pullRequest.pullRequestId)}
                      className="px-3 py-2 rounded-md bg-red-600 text-white text-sm font-semibold disabled:opacity-60"
                    >
                      Reject
                    </button>
                  </div>
                </div>

                <div className="mt-4 flex flex-wrap gap-4 text-sm">
                  <a href={pullRequest.url} target="_blank" rel="noreferrer" className="text-blue-600 hover:underline font-semibold">
                    Otworz pull request
                  </a>
                  {taskDocs ? (
                    <a href={taskDocs.url} target="_blank" rel="noreferrer" className="text-blue-600 hover:underline font-semibold">
                      Dokumentacja: {taskDocs.title}
                    </a>
                  ) : (
                    <span className="text-gray-400">Brak dokumentacji w projekcie</span>
                  )}
                  {projectId && (
                    <Link to={`/projects/${projectId}/tasks/${pullRequest.taskId}`} className="text-blue-600 hover:underline font-semibold">
                      Szczegoly zadania
                    </Link>
                  )}
                </div>

                {isRejecting && (
                  <div className="mt-4 grid gap-3">
                    <textarea
                      value={rejectReasons[pullRequest.pullRequestId] ?? ''}
                      onChange={(e) => setRejectReasons((current) => ({ ...current, [pullRequest.pullRequestId]: e.target.value }))}
                      placeholder="Powod odrzucenia"
                      className="min-h-24 rounded-lg border border-gray-200 px-3 py-2 text-sm text-gray-900 focus:outline-none focus:ring-2 focus:ring-red-100"
                    />
                    <button
                      type="button"
                      disabled={isWorking}
                      onClick={() => handleReject(pullRequest)}
                      className="justify-self-start px-3 py-2 rounded-md bg-red-600 text-white text-sm font-semibold disabled:opacity-60"
                    >
                      Potwierdz odrzucenie
                    </button>
                  </div>
                )}
              </article>
            )
          })}
        </div>
      )}
    </div>
  )
}
