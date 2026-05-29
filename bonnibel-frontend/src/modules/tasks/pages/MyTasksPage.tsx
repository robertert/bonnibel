import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { taskService } from '@/services/taskService'
import { useAuthStore } from '@/modules/auth/store/authStore'
import type { Task } from '@/types/domain'

export default function MyTasksPage() {
  const userId = useAuthStore((s) => s.userId)
  const [tasks, setTasks] = useState<Task[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!userId) {
      setTasks([])
      setLoading(false)
      return
    }
    setLoading(true)
    // Filtrujemy zadania po realnym id zalogowanego użytkownika (a nie po stałym 'user-1').
    taskService.getUserTasks(1, userId)
      .then(setTasks)
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [userId])

  if (loading) {
    return <div style={{ padding: '24px', textAlign: 'center' }}>Ładowanie Twoich zadań...</div>
  }

  return (
    <div style={{ padding: '24px', maxWidth: '800px', margin: '0 auto', fontFamily: 'sans-serif' }}>
      <h2 style={{ marginBottom: '20px', color: '#1a202c' }}>Moje zadania</h2>

      {tasks.length === 0 ? (
        <p style={{ color: '#666' }}>Nie masz aktualnie przypisanych żadnych zadań.</p>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {tasks.map(task => (
            <div key={task.taskId} style={{ border: '1px solid #e2e8f0', borderRadius: '8px', padding: '16px', background: 'white', display: 'flex', justifyContent: 'space-between', alignItems: 'center', boxShadow: '0 1px 3px rgba(0,0,0,0.02)' }}>
              <div>
                <span style={{ fontSize: '11px', color: '#a0aec0', fontWeight: 'bold', display: 'block', marginBottom: '2px' }}>{task.jiraIssueKey}</span>
                <h4 style={{ margin: 0, fontSize: '16px', color: '#2d3748' }}>{task.title}</h4>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                <span style={{
                  fontSize: '11px',
                  padding: '4px 8px',
                  borderRadius: '12px',
                  background: '#edf2f7',
                  color: '#4a5568',
                  fontWeight: 'bold'
                }}>{task.status}</span>
                <Link to={`/projects/${task.projectId}/tasks/${task.taskId}`} style={{ textDecoration: 'none', color: '#0070f3', fontSize: '14px', fontWeight: 'bold' }}>
                  Otwórz →
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}