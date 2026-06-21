import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { taskService } from '@/services/taskService'
import { taskActivityService } from '@/services/taskActivityService'
import { userService } from '@/services/userService'
import { projectService } from '@/services/projectService'
import TaskChat from '@/modules/chat/components/TaskChat'
import TaskDocs from '@/modules/tasks/components/TaskDocs'
import TaskPullRequests from '@/modules/tasks/components/TaskPullRequests'
import TaskHistory from '@/modules/tasks/components/TaskHistory'
import type { Task, TaskStatus, User, ProjectRole } from '@/types/domain'

export default function TaskDetailsPage() {
  const { projectId, taskId } = useParams<{ projectId: string; taskId: string }>()
  const [task, setTask] = useState<Task | null>(null)
  const [userRole, setUserRole] = useState<ProjectRole | null>(null)
  
  const [loading, setLoading] = useState(true)
  const [updating, setUpdating] = useState(false)
  const [users, setUsers] = useState<User[]>([])
  
  const [subscribed, setSubscribed] = useState(false)
  const [subBusy, setSubBusy] = useState(false)

  // Ładowanie wszystkich potrzebnych danych
  useEffect(() => {
    if (!projectId || !taskId) return
    setLoading(true)
    
    const pid = Number(projectId)
    const currentUserId = localStorage.getItem('userId')

    Promise.all([
      taskService.getTask(pid, Number(taskId)),
      userService.listUsers(),
      projectService.listMembers(pid),
      taskActivityService.getSubscriptions()
    ])
    .then(([fetchedTask, fetchedUsers, members, subs]) => {
      setTask(fetchedTask)
      setUsers(fetchedUsers)
      
      const me = members.find(m => m.userId === currentUserId)
      if (me) setUserRole(me.role)
      
      setSubscribed(subs.some((s) => s.taskId === Number(taskId)))
    })
    .catch(console.error)
    .finally(() => setLoading(false))
  }, [projectId, taskId])

  // Akcje
  const handleToggleSubscribe = async () => { /* bez zmian */
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
    } catch (err) { console.error(err) } finally { setSubBusy(false) }
  }

  const handleAssign = async (assigneeId: string | null) => {
    if (!projectId || !taskId) return
    setUpdating(true)
    try {
      const updated = await taskService.assignTask(Number(projectId), Number(taskId), assigneeId)
      setTask(updated)
    } catch (err) { console.error(err) } finally { setUpdating(false) }
  }

  const handleReviewer = async (reviewerId: string | null) => {
    if (!projectId || !taskId) return
    setUpdating(true)
    try {
      const updated = await taskService.assignReviewer(Number(projectId), Number(taskId), reviewerId)
      setTask(updated)
    } catch (err) { console.error(err) } finally { setUpdating(false) }
  }

  const handleStatusChange = async (newStatus: TaskStatus) => {
    if (!projectId || !taskId || !task) return
    setUpdating(true)
    try {
      const updatedTask = await taskService.updateStatus(Number(projectId), Number(taskId), newStatus)
      setTask(updatedTask)
    } catch (err) { console.error(err) } finally { setUpdating(false) }
  }

  const reloadTask = () => {
    if (projectId && taskId) {
      taskService.getTask(Number(projectId), Number(taskId)).then(setTask).catch(console.error)
    }
  }

  // --- LOGIKA UPRAWNIEŃ ---
  const getAvailableStatuses = (): TaskStatus[] => {
    if (userRole === 'OWNER') return ['TODO', 'IN_PROGRESS', 'IN_REVIEW', 'DONE', 'CLOSED']
    if (userRole === 'DEVELOPER') return ['TODO', 'IN_PROGRESS', 'IN_REVIEW']
    if (userRole === 'REVIEWER') return ['IN_REVIEW', 'DONE', 'CLOSED']
    return [task?.status as TaskStatus] // Fallback
  }
  
  const canChangeAssignee = userRole === 'OWNER' || userRole === 'DEVELOPER'
  const canChangeReviewer = userRole === 'OWNER' || userRole === 'REVIEWER'
  // ------------------------

  if (loading) return <div style={{ padding: '24px', textAlign: 'center' }}>Wczytywanie szczegółów zadania...</div>
  if (!task) return <div style={{ padding: '24px', textAlign: 'center', color: 'red' }}>Nie odnaleziono zadania.</div>

  return (
    <div style={{ padding: '24px', maxWidth: '800px', margin: '0 auto', fontFamily: 'sans-serif' }}>
      <Link to={`/projects/${projectId}/tasks`} style={{ textDecoration: 'none', color: '#4a5568', fontSize: '14px', display: 'inline-block', marginBottom: '16px' }}>← Powrót do listy zadań</Link>

      <div style={{ background: 'white', border: '1px solid #e2e8f0', borderRadius: '12px', padding: '24px', boxShadow: '0 4px 6px rgba(0,0,0,0.02)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <span style={{ fontSize: '14px', color: '#0070f3', fontWeight: 'bold', background: '#e1effe', padding: '4px 8px', borderRadius: '4px' }}>{task.jiraIssueKey || 'BON-Task'}</span>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <button onClick={handleToggleSubscribe} disabled={subBusy} style={{ padding: '6px 12px', borderRadius: '6px', fontSize: '14px', cursor: 'pointer', border: '1px solid ' + (subscribed ? '#0070f3' : '#cbd5e0'), background: subscribed ? '#e1effe' : '#ffffff', color: subscribed ? '#0070f3' : '#4a5568' }}>
              {subscribed ? '🔔 Obserwujesz' : '🔕 Obserwuj'}
            </button>
            <span style={{ fontSize: '14px', color: '#4a5568' }}>Status:</span>
            <select value={task.status} disabled={updating} onChange={(e) => handleStatusChange(e.target.value as TaskStatus)} style={{ padding: '6px 12px', borderRadius: '6px', border: '1px solid #cbd5e0', fontSize: '14px', cursor: 'pointer', backgroundColor: '#ffffff' }}>
              {getAvailableStatuses().map(status => (
                <option key={status} value={status}>{status}</option>
              ))}
              {/* Zawsze pokazuj obecny status, nawet jeśli rola by go normalnie ukryła */}
              {!getAvailableStatuses().includes(task.status) && <option value={task.status} disabled>{task.status}</option>}
            </select>
          </div>
        </div>

        <h1 style={{ margin: '0 0 16px 0', fontSize: '24px', color: '#1a202c' }}>{task.title}</h1>
        <p style={{ fontSize: '16px', lineHeight: '1.6', color: '#4a5568', whiteSpace: 'pre-line', margin: '0 0 24px 0' }}>{task.description}</p>
        <hr style={{ border: 'none', borderTop: '1px solid #e2e8f0', margin: '24px 0' }} />

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
          <div>
            <span style={{ display: 'block', fontSize: '12px', color: '#718096', fontWeight: 'bold', textTransform: 'uppercase', marginBottom: '4px' }}>Powiązana gałąź Git:</span>
            <code style={{ color: '#1a202c',background: '#f7fafc', padding: '4px 8px', borderRadius: '4px', border: '1px solid #e2e8f0', fontSize: '13px', display: 'inline-block' }}>{task.gitBranchName || 'brak powiązania'}</code>
          </div>
          <div>
            <span style={{ display: 'block', fontSize: '12px', color: '#718096', fontWeight: 'bold', textTransform: 'uppercase', marginBottom: '4px' }}>Przypisana osoba:</span>
            <select value={task.assigneeId ?? ''} disabled={updating || !canChangeAssignee} onChange={(e) => handleAssign(e.target.value || null)} style={{ width: '100%', padding: '6px 10px', borderRadius: '6px', border: '1px solid #cbd5e0', fontSize: '14px', backgroundColor: canChangeAssignee ? '#ffffff' : '#f7fafc', cursor: canChangeAssignee ? 'pointer' : 'not-allowed' }}>
              <option value="">— nieprzypisane —</option>
              {users.map((u) => <option key={u.userId} value={u.userId}>{u.email}</option>)}
            </select>
          </div>
          <div>
            <span style={{ display: 'block', fontSize: '12px', color: '#718096', fontWeight: 'bold', textTransform: 'uppercase', marginBottom: '4px' }}>Recenzent:</span>
            <select value={task.reviewerId ?? ''} disabled={updating || !canChangeReviewer} onChange={(e) => handleReviewer(e.target.value || null)} style={{ width: '100%', padding: '6px 10px', borderRadius: '6px', border: '1px solid #cbd5e0', fontSize: '14px', backgroundColor: canChangeReviewer ? '#ffffff' : '#f7fafc', cursor: canChangeReviewer ? 'pointer' : 'not-allowed' }}>
              <option value="">— brak —</option>
              {users.map((u) => <option key={u.userId} value={u.userId}>{u.email}</option>)}
            </select>
          </div>
        </div>
      </div>

      <div style={{ marginTop: '24px', display: 'flex', flexDirection: 'column', gap: '24px' }}>
        {/* Przekazujemy rolę w dół! */}
        <TaskPullRequests projectId={Number(projectId)} taskId={task.taskId} onChanged={reloadTask} userRole={userRole} />
        <TaskDocs projectId={Number(projectId)} taskId={task.taskId} userRole={userRole} />
        <TaskHistory projectId={Number(projectId)} taskId={task.taskId} />
        <TaskChat projectId={Number(projectId)} taskId={task.taskId} />
      </div>
    </div>
  )
}