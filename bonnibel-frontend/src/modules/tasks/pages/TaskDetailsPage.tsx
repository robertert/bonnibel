import React, { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { taskService } from '@/services/taskService'
import type { Task, TaskStatus } from '@/types/domain'

export default function TaskDetailsPage() {
  const { projectId, taskId } = useParams<{ projectId: string; taskId: string }>()
  const [task, setTask] = useState<Task | null>(null)
  const [loading, setLoading] = useState(true)
  const [updating, setUpdating] = useState(false)

  useEffect(() => {
    if (projectId && taskId) {
      setLoading(true)
      taskService.getTask(Number(projectId), Number(taskId))
        .then(setTask)
        .catch(console.error)
        .finally(() => setLoading(false))
    }
  }, [projectId, taskId])

  const handleStatusChange = async (newStatus: TaskStatus) => {
    if (!projectId || !taskId || !task) return
    setUpdating(true)
    try {
      const updatedTask = await taskService.updateStatus(Number(projectId), Number(taskId), newStatus)
      setTask(updatedTask)
    } catch (err) {
      console.error("Nie udało się zaktualizować statusu", err)
    } finally {
      setUpdating(false)
    }
  }

  if (loading) {
    return <div style={{ padding: '24px', textAlign: 'center' }}>Wczytywanie szczegółów zadania #{taskId}...</div>
  }

  if (!task) {
    return <div style={{ padding: '24px', textAlign: 'center', color: 'red' }}>Nie odnaleziono zadania o podanym identyfikatorze.</div>
  }

  return (
    <div style={{ padding: '24px', maxWidth: '800px', margin: '0 auto', fontFamily: 'sans-serif' }}>
      <Link to={`/projects/${projectId}/tasks`} style={{ textDecoration: 'none', color: '#4a5568', fontSize: '14px', display: 'inline-block', marginBottom: '16px' }}>
        ← Powrót do listy zadań
      </Link>

      <div style={{ background: 'white', border: '1px solid #e2e8f0', borderRadius: '12px', padding: '24px', boxShadow: '0 4px 6px rgba(0,0,0,0.02)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <span style={{ fontSize: '14px', color: '#0070f3', fontWeight: 'bold', background: '#e1effe', padding: '4px 8px', borderRadius: '4px' }}>
            {task.jiraIssueKey || 'BON-Task'}
          </span>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
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
              <option value="TODO" style={{ color: '#1a202c', backgroundColor: '#ffffff' }}>TODO</option>
              <option value="IN_PROGRESS" style={{ color: '#1a202c', backgroundColor: '#ffffff' }}>IN_PROGRESS</option>
              <option value="IN_REVIEW" style={{ color: '#1a202c', backgroundColor: '#ffffff' }}>IN_REVIEW</option>
              <option value="DONE" style={{ color: '#1a202c', backgroundColor: '#ffffff' }}>DONE</option>
              <option value="CLOSED" style={{ color: '#1a202c', backgroundColor: '#ffffff' }}>CLOSED</option>
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
            <span style={{ display: 'block', fontSize: '12px', color: '#718096', fontWeight: 'bold', textTransform: 'uppercase', marginBottom: '4px' }}>Powiązana gałąź Git:</span>
            <code style={{ color: '#1a202c',background: '#f7fafc', padding: '4px 8px', borderRadius: '4px', border: '1px solid #e2e8f0', fontSize: '13px', display: 'inline-block' }}>
              {task.gitBranchName || 'brak powiązania'}
            </code>
          </div>
          <div>
            <span style={{ display: 'block', fontSize: '12px', color: '#718096', fontWeight: 'bold', textTransform: 'uppercase', marginBottom: '4px' }}>Przypisana osoba:</span>
            <span style={{ fontSize: '14px', color: '#2d3748' }}>
              {task.assigneeId ? `Użytkownik: ${task.assigneeId}` : 'Nieprzypisane'}
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}