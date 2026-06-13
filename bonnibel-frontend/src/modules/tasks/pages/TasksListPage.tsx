import { useEffect, useState, type FormEvent } from 'react'
import { useParams, Link } from 'react-router-dom'
import { taskService } from '@/services/taskService'
import type { Task } from '@/types/domain'

export default function TasksListPage() {
  const { projectId } = useParams<{ projectId: string }>()
  const [tasks, setTasks] = useState<Task[]>([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [creating, setCreating] = useState(false)

  const handleCreate = async (e: FormEvent) => {
    e.preventDefault()
    if (!projectId || !title.trim() || creating) return
    setCreating(true)
    try {
      const created = await taskService.createTask(Number(projectId), {
        title: title.trim(),
        description: description.trim(),
      })
      setTasks((prev) => [created, ...prev])
      setTitle('')
      setDescription('')
      setShowForm(false)
    } catch (err) {
      console.error('Nie udało się utworzyć zadania', err)
      window.alert('Nie udało się utworzyć zadania.')
    } finally {
      setCreating(false)
    }
  }

  useEffect(() => {
    if (projectId) {
      setLoading(true)
      taskService.getProjectTasks(Number(projectId))
        .then(setTasks)
        .catch(console.error)
        .finally(() => setLoading(false))
    }
  }, [projectId])

  if (loading) {
    return <div style={{ padding: '24px', textAlign: 'center' }}>Ładowanie listy zadań projektu #{projectId}...</div>
  }

  return (
    <div style={{ padding: '24px', maxWidth: '1200px', margin: '0 auto', fontFamily: 'sans-serif' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <h2 style={{ margin: 0 }}>Zadania projektu #{projectId}</h2>
        <button
          onClick={() => setShowForm((s) => !s)}
          style={{ padding: '8px 16px', background: '#0070f3', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold' }}
        >
          {showForm ? 'Anuluj' : '+ Utwórz zadanie'}
        </button>
      </div>

      {showForm && (
        <form
          onSubmit={handleCreate}
          style={{ border: '1px solid #e2e8f0', borderRadius: '8px', padding: '16px', background: 'white', marginBottom: '24px', display: 'flex', flexDirection: 'column', gap: '12px' }}
        >
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Tytuł zadania"
            autoFocus
            style={{ padding: '8px 12px', border: '1px solid #cbd5e0', borderRadius: '6px', fontSize: '14px', color: '#1a202c', backgroundColor: 'white' }}
          />
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Opis (opcjonalnie)"
            rows={3}
            style={{ padding: '8px 12px', border: '1px solid #cbd5e0', borderRadius: '6px', fontSize: '14px', color: '#1a202c', backgroundColor: 'white', resize: 'vertical' }}
          />
          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '8px' }}>
            <button
              type="submit"
              disabled={creating || !title.trim()}
              style={{ padding: '8px 16px', background: creating || !title.trim() ? '#a0c4f3' : '#0070f3', color: 'white', border: 'none', borderRadius: '6px', cursor: (creating || !title.trim()) ? 'default' : 'pointer', fontWeight: 'bold' }}
            >
              {creating ? 'Tworzę…' : 'Dodaj zadanie'}
            </button>
          </div>
        </form>
      )}

      {tasks.length === 0 ? (
        <p style={{ color: '#666' }}>W tym projekcie nie ma jeszcze żadnych zadań.</p>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '16px' }}>
          {tasks.map(task => (
            <div key={task.taskId} style={{ border: '1px solid #e2e8f0', borderRadius: '8px', padding: '16px', background: 'white', boxShadow: '0 2px 4px rgba(0,0,0,0.02)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                <span style={{ fontSize: '12px', color: '#0070f3', fontWeight: 'bold' }}>{task.jiraIssueKey || 'Zadanie'}</span>
                <span style={{
                  fontSize: '11px',
                  padding: '4px 8px',
                  borderRadius: '12px',
                  background: task.status === 'DONE' ? '#e6fffa' : '#fffaf0',
                  color: task.status === 'DONE' ? '#319795' : '#dd6b20',
                  fontWeight: 'bold'
                }}>{task.status}</span>
              </div>
              <h4 style={{ margin: '0 0 8px 0', fontSize: '16px', color: '#1a202c' }}>{task.title}</h4>
              <p style={{ fontSize: '14px', color: '#4a5568', margin: '0 0 16px 0', display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                {task.description}
              </p>
              <Link to={`/projects/${projectId}/tasks/${task.taskId}`} style={{ textDecoration: 'none', color: '#0070f3', fontWeight: 'bold', fontSize: '14px' }}>
                Szczegóły →
              </Link>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}