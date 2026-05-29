import { useEffect, useState, type FormEvent } from 'react'
import { useParams, Link } from 'react-router-dom'
import { taskService } from '@/services/taskService'
import { taskActivityService } from '@/services/taskActivityService'
import { userService } from '@/services/userService'
import { docsService } from '@/services/docsService'
import { pullRequestService } from '@/services/pullRequestService'
import TaskChat from '@/modules/chat/components/TaskChat'
import TaskHistory from '@/modules/tasks/components/TaskHistory'
import type { PullRequest, Task, TaskDoc, TaskStatus, User } from '@/types/domain'

export default function TaskDetailsPage() {
  const { projectId, taskId } = useParams<{ projectId: string; taskId: string }>()
  const [task, setTask] = useState<Task | null>(null)
  const [docs, setDocs] = useState<TaskDoc | null>(null)
  const [pullRequest, setPullRequest] = useState<PullRequest | null>(null)
  const [loading, setLoading] = useState(true)
  const [updating, setUpdating] = useState(false)
  const [users, setUsers] = useState<User[]>([])
  const [subscribed, setSubscribed] = useState(false)
  const [subBusy, setSubBusy] = useState(false)
  const [docsTitle, setDocsTitle] = useState('')
  const [docsUrl, setDocsUrl] = useState('')
  const [docsSaving, setDocsSaving] = useState(false)
  const [docsEditing, setDocsEditing] = useState(false)
  const [prCreating, setPrCreating] = useState(false)
  const [message, setMessage] = useState<string | null>(null)

  useEffect(() => {
    userService.listUsers().then(setUsers).catch(console.error)
  }, [])

  useEffect(() => {
    if (!taskId) return
    taskActivityService.getSubscriptions()
      .then((subs) => setSubscribed(subs.some((s) => s.taskId === Number(taskId))))
      .catch(() => setSubscribed(false))
  }, [taskId])

  useEffect(() => {
    if (projectId && taskId) {
      const numericProjectId = Number(projectId)
      const numericTaskId = Number(taskId)

      setLoading(true)
      Promise.all([
        taskService.getTask(numericProjectId, numericTaskId),
        docsService.getTaskDocs(numericProjectId, numericTaskId).catch(() => null),
        pullRequestService.getTaskPullRequest(numericProjectId, numericTaskId).catch(() => null),
      ])
        .then(([loadedTask, loadedDocs, loadedPullRequest]) => {
          setTask(loadedTask)
          setDocs(loadedDocs)
          setPullRequest(loadedPullRequest)
        })
        .catch(console.error)
        .finally(() => setLoading(false))
    }
  }, [projectId, taskId])

  const handleToggleSubscribe = async () => {
    if (!taskId) return
    setSubBusy(true)
    try {
      if (subscribed) {
        await taskActivityService.unsubscribe(Number(taskId))
        setSubscribed(false)
      } else {
        await taskActivityService.subscribe(Number(taskId))
        setSubscribed(true)
      }
    } catch (err) {
      console.error('Nie udalo sie zmienic subskrypcji', err)
      window.alert('Nie udalo sie zmienic subskrypcji.')
    } finally {
      setSubBusy(false)
    }
  }

  const handleAssign = async (assigneeId: string | null) => {
    if (!projectId || !taskId) return
    setUpdating(true)
    try {
      const updated = await taskService.assignTask(Number(projectId), Number(taskId), assigneeId)
      setTask(updated)
    } catch (err) {
      console.error('Nie udalo sie przypisac osoby', err)
      window.alert('Nie udalo sie przypisac osoby.')
    } finally {
      setUpdating(false)
    }
  }

  const handleReviewer = async (reviewerId: string | null) => {
    if (!projectId || !taskId) return
    setUpdating(true)
    try {
      const updated = await taskService.assignReviewer(Number(projectId), Number(taskId), reviewerId)
      setTask(updated)
    } catch (err) {
      console.error('Nie udalo sie przypisac recenzenta', err)
      window.alert('Nie udalo sie przypisac recenzenta.')
    } finally {
      setUpdating(false)
    }
  }

  const handleStatusChange = async (newStatus: TaskStatus) => {
    if (!projectId || !taskId || !task) return
    setUpdating(true)
    try {
      const updatedTask = await taskService.updateStatus(Number(projectId), Number(taskId), newStatus)
      setTask(updatedTask)
    } catch (err) {
      console.error('Nie udalo sie zaktualizowac statusu', err)
    } finally {
      setUpdating(false)
    }
  }

  const handleAddDocs = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (!projectId || !taskId || !docsTitle.trim() || !docsUrl.trim()) return

    setDocsSaving(true)
    setMessage(null)
    try {
      const createdDocs = await docsService.addTaskDocs(Number(projectId), Number(taskId), {
        title: docsTitle.trim(),
        url: docsUrl.trim(),
      })
      setDocs(createdDocs)
      setDocsTitle('')
      setDocsUrl('')
      setMessage('Dokumentacja zostala dodana do zadania.')
    } catch (err) {
      console.error('Nie udalo sie dodac dokumentacji', err)
      setMessage('Nie udalo sie dodac dokumentacji.')
    } finally {
      setDocsSaving(false)
    }
  }

  const startEditingDocs = () => {
    if (!docs) return
    setDocsTitle(docs.title)
    setDocsUrl(docs.url)
    setDocsEditing(true)
    setMessage(null)
  }

  const cancelEditingDocs = () => {
    setDocsEditing(false)
    setDocsTitle('')
    setDocsUrl('')
  }

  const handleUpdateDocs = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (!projectId || !taskId || !docs || !docsTitle.trim() || !docsUrl.trim()) return

    setDocsSaving(true)
    setMessage(null)
    try {
      const updatedDocs = await docsService.updateTaskDocs(Number(projectId), Number(taskId), docs.docsId, {
        title: docsTitle.trim(),
        url: docsUrl.trim(),
      })
      setDocs(updatedDocs)
      setDocsEditing(false)
      setDocsTitle('')
      setDocsUrl('')
      setMessage('Dokumentacja zostala zaktualizowana.')
    } catch (err) {
      console.error('Nie udalo sie zaktualizowac dokumentacji', err)
      setMessage('Nie udalo sie zaktualizowac dokumentacji.')
    } finally {
      setDocsSaving(false)
    }
  }

  const handleCreatePullRequest = async () => {
    if (!projectId || !taskId || !task || !docs) {
      setMessage('Najpierw dodaj dokumentacje zadania.')
      return
    }
    if (pullRequest) {
      setMessage('Pull request dla tego zadania juz istnieje.')
      return
    }

    setPrCreating(true)
    setMessage(null)
    try {
      const createdPullRequest = await pullRequestService.createPullRequest(Number(projectId), Number(taskId), {
        title: `${task.jiraIssueKey ?? `Task #${task.taskId}`} - ${task.title}`,
        url: `https://github.com/example/bonnibel/pull/${task.taskId}`,
        reviewerId: task.reviewerId ?? 'user-1',
      })
      setPullRequest(createdPullRequest)
      setMessage('Pull request zostal utworzony i przekazany do review.')
    } catch (err) {
      console.error('Nie udalo sie utworzyc pull requesta', err)
      setMessage('Nie udalo sie utworzyc pull requesta.')
    } finally {
      setPrCreating(false)
    }
  }

  if (loading) {
    return <div style={{ padding: '24px', textAlign: 'center' }}>Wczytywanie szczegolow zadania #{taskId}...</div>
  }

  if (!task) {
    return <div style={{ padding: '24px', textAlign: 'center', color: 'red' }}>Nie odnaleziono zadania o podanym identyfikatorze.</div>
  }

  return (
    <div style={{ padding: '24px', maxWidth: '800px', margin: '0 auto', fontFamily: 'sans-serif' }}>
      <Link to={`/projects/${projectId}/tasks`} style={{ textDecoration: 'none', color: '#4a5568', fontSize: '14px', display: 'inline-block', marginBottom: '16px' }}>
        Powrot do listy zadan
      </Link>

      <div style={{ background: 'white', border: '1px solid #e2e8f0', borderRadius: '12px', padding: '24px', boxShadow: '0 4px 6px rgba(0,0,0,0.02)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <span style={{ fontSize: '14px', color: '#0070f3', fontWeight: 'bold', background: '#e1effe', padding: '4px 8px', borderRadius: '4px' }}>
            {task.jiraIssueKey || 'BON-Task'}
          </span>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <button
              onClick={handleToggleSubscribe}
              disabled={subBusy}
              style={{
                padding: '6px 12px', borderRadius: '6px', fontSize: '14px', cursor: 'pointer',
                border: '1px solid ' + (subscribed ? '#0070f3' : '#cbd5e0'),
                background: subscribed ? '#e1effe' : '#ffffff',
                color: subscribed ? '#0070f3' : '#4a5568',
              }}
            >
              {subscribed ? 'Obserwujesz' : 'Obserwuj'}
            </button>
            <span style={{ fontSize: '14px', color: '#4a5568' }}>Status zadania:</span>
            <select
              value={task.status}
              disabled={updating}
              onChange={(e) => handleStatusChange(e.target.value as TaskStatus)}
              style={{
                padding: '6px 12px',
                borderRadius: '6px',
                border: '1px solid #cbd5e0',
                fontSize: '14px',
                cursor: 'pointer',
                color: '#1a202c',
                backgroundColor: '#ffffff',
              }}
            >
              <option value="TODO">TODO</option>
              <option value="IN_PROGRESS">IN_PROGRESS</option>
              <option value="IN_REVIEW">IN_REVIEW</option>
              <option value="DONE">DONE</option>
              <option value="CLOSED">CLOSED</option>
            </select>
          </div>
        </div>

        <h1 style={{ margin: '0 0 16px 0', fontSize: '24px', color: '#1a202c' }}>{task.title}</h1>
        <p style={{ fontSize: '16px', lineHeight: '1.6', color: '#4a5568', whiteSpace: 'pre-line', margin: '0 0 24px 0' }}>
          {task.description}
        </p>

        <hr style={{ border: 'none', borderTop: '1px solid #e2e8f0', margin: '24px 0' }} />

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
          <div>
            <span style={{ display: 'block', fontSize: '12px', color: '#718096', fontWeight: 'bold', textTransform: 'uppercase', marginBottom: '4px' }}>Powiazana galaz Git:</span>
            <code style={{ color: '#1a202c', background: '#f7fafc', padding: '4px 8px', borderRadius: '4px', border: '1px solid #e2e8f0', fontSize: '13px', display: 'inline-block' }}>
              {task.gitBranchName || 'brak powiazania'}
            </code>
          </div>
          <div>
            <span style={{ display: 'block', fontSize: '12px', color: '#718096', fontWeight: 'bold', textTransform: 'uppercase', marginBottom: '4px' }}>Przypisana osoba:</span>
            <select
              value={task.assigneeId ?? ''}
              disabled={updating}
              onChange={(e) => handleAssign(e.target.value || null)}
              style={{ width: '100%', padding: '6px 10px', borderRadius: '6px', border: '1px solid #cbd5e0', fontSize: '14px', color: '#1a202c', backgroundColor: '#ffffff', cursor: 'pointer' }}
            >
              <option value="">nieprzypisane</option>
              {users.map((u) => (
                <option key={u.userId} value={u.userId}>{u.email}</option>
              ))}
            </select>
          </div>
          <div>
            <span style={{ display: 'block', fontSize: '12px', color: '#718096', fontWeight: 'bold', textTransform: 'uppercase', marginBottom: '4px' }}>Recenzent:</span>
            <select
              value={task.reviewerId ?? ''}
              disabled={updating}
              onChange={(e) => handleReviewer(e.target.value || null)}
              style={{ width: '100%', padding: '6px 10px', borderRadius: '6px', border: '1px solid #cbd5e0', fontSize: '14px', color: '#1a202c', backgroundColor: '#ffffff', cursor: 'pointer' }}
            >
              <option value="">brak</option>
              {users.map((u) => (
                <option key={u.userId} value={u.userId}>{u.email}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      <div style={{ marginTop: '24px', background: 'white', border: '1px solid #e2e8f0', borderRadius: '12px', padding: '24px', boxShadow: '0 4px 6px rgba(0,0,0,0.02)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '16px', marginBottom: '20px' }}>
          <div>
            <h2 style={{ margin: '0 0 6px 0', fontSize: '20px', color: '#1a202c' }}>Dokumentacja i Pull Request</h2>
            <p style={{ margin: 0, fontSize: '14px', color: '#718096' }}>
              Dokumentacja jest wymagana przed utworzeniem pull requesta.
            </p>
          </div>
          <button
            type="button"
            disabled={!docs || !!pullRequest || prCreating}
            onClick={handleCreatePullRequest}
            style={{
              padding: '8px 14px',
              borderRadius: '6px',
              border: 'none',
              background: docs && !pullRequest ? '#0070f3' : '#cbd5e0',
              color: 'white',
              cursor: docs && !pullRequest && !prCreating ? 'pointer' : 'not-allowed',
              fontWeight: 'bold',
              fontSize: '14px',
              whiteSpace: 'nowrap',
            }}
          >
            {prCreating ? 'Tworzenie...' : pullRequest ? 'Pull Request istnieje' : 'Utworz Pull Request'}
          </button>
        </div>

        {message && (
          <div style={{ marginBottom: '16px', padding: '10px 12px', borderRadius: '6px', background: '#f7fafc', color: '#4a5568', fontSize: '14px', border: '1px solid #e2e8f0' }}>
            {message}
          </div>
        )}

        {docs && !docsEditing ? (
          <div style={{ border: '1px solid #e2e8f0', borderRadius: '8px', padding: '16px', background: '#f7fafc', marginBottom: '16px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '12px' }}>
              <div>
                <span style={{ display: 'block', fontSize: '12px', color: '#718096', fontWeight: 'bold', textTransform: 'uppercase', marginBottom: '4px' }}>Dokumentacja zadania</span>
                <a href={docs.url} target="_blank" rel="noreferrer" style={{ color: '#0070f3', fontWeight: 'bold', textDecoration: 'none' }}>
                  {docs.title}
                </a>
              </div>
              <button
                type="button"
                onClick={startEditingDocs}
                style={{
                  padding: '7px 12px',
                  borderRadius: '6px',
                  border: '1px solid #cbd5e0',
                  background: 'white',
                  color: '#2d3748',
                  cursor: 'pointer',
                  fontWeight: 'bold',
                  fontSize: '13px',
                  whiteSpace: 'nowrap',
                }}
              >
                Edytuj
              </button>
            </div>
          </div>
        ) : (
          <form onSubmit={docsEditing ? handleUpdateDocs : handleAddDocs} style={{ display: 'grid', gap: '12px', marginBottom: '16px' }}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
              <label style={{ display: 'grid', gap: '6px', fontSize: '13px', color: '#4a5568', fontWeight: 'bold' }}>
                Tytul dokumentacji
                <input
                  value={docsTitle}
                  onChange={(e) => setDocsTitle(e.target.value)}
                  placeholder="Np. Specyfikacja funkcji"
                  style={{ padding: '9px 10px', borderRadius: '6px', border: '1px solid #cbd5e0', fontSize: '14px', color: '#1a202c' }}
                />
              </label>
              <label style={{ display: 'grid', gap: '6px', fontSize: '13px', color: '#4a5568', fontWeight: 'bold' }}>
                URL
                <input
                  value={docsUrl}
                  onChange={(e) => setDocsUrl(e.target.value)}
                  placeholder="https://..."
                  style={{ padding: '9px 10px', borderRadius: '6px', border: '1px solid #cbd5e0', fontSize: '14px', color: '#1a202c' }}
                />
              </label>
            </div>
            <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
              <button
                type="submit"
                disabled={docsSaving || !docsTitle.trim() || !docsUrl.trim()}
                style={{
                  padding: '8px 14px',
                  borderRadius: '6px',
                  border: 'none',
                  background: '#2f855a',
                  color: 'white',
                  cursor: docsSaving ? 'wait' : 'pointer',
                  fontWeight: 'bold',
                  fontSize: '14px',
                }}
              >
                {docsSaving ? 'Zapisywanie...' : docsEditing ? 'Zapisz zmiany' : 'Dodaj dokumentacje'}
              </button>
              {docsEditing && (
                <button
                  type="button"
                  disabled={docsSaving}
                  onClick={cancelEditingDocs}
                  style={{
                    padding: '8px 14px',
                    borderRadius: '6px',
                    border: '1px solid #cbd5e0',
                    background: 'white',
                    color: '#2d3748',
                    cursor: docsSaving ? 'wait' : 'pointer',
                    fontWeight: 'bold',
                    fontSize: '14px',
                  }}
                >
                  Anuluj
                </button>
              )}
            </div>
          </form>
        )}

        {pullRequest && (
          <div style={{ border: '1px solid #bee3f8', borderRadius: '8px', padding: '16px', background: '#ebf8ff' }}>
            <span style={{ display: 'block', fontSize: '12px', color: '#2b6cb0', fontWeight: 'bold', textTransform: 'uppercase', marginBottom: '4px' }}>Pull Request</span>
            <a href={pullRequest.url} target="_blank" rel="noreferrer" style={{ color: '#0070f3', fontWeight: 'bold', textDecoration: 'none' }}>
              {pullRequest.title}
            </a>
            <span style={{ marginLeft: '10px', fontSize: '12px', color: '#2b6cb0', fontWeight: 'bold' }}>{pullRequest.status}</span>
          </div>
        )}
      </div>

      <div style={{ marginTop: '24px', display: 'flex', flexDirection: 'column', gap: '24px' }}>
        <TaskHistory projectId={Number(projectId)} taskId={task.taskId} />
        <TaskChat projectId={Number(projectId)} taskId={task.taskId} />
      </div>
    </div>
  )
}
