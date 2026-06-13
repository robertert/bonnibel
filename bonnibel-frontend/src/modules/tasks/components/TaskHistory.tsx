import { useEffect, useState } from 'react'
import { taskActivityService } from '@/services/taskActivityService'
import type { TaskHistory as TaskHistoryEvent } from '@/types/domain'

const card: React.CSSProperties = {
  background: 'white', border: '1px solid #e2e8f0', borderRadius: '12px',
  padding: '20px', boxShadow: '0 4px 6px rgba(0,0,0,0.02)',
}
const heading: React.CSSProperties = { margin: '0 0 16px 0', fontSize: '18px', color: '#1a202c' }

export default function TaskHistory({ projectId, taskId }: { projectId: number; taskId: number }) {
  const [events, setEvents] = useState<TaskHistoryEvent[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(true)
    taskActivityService.getHistory(projectId, taskId)
      .then(setEvents)
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [projectId, taskId])

  return (
    <div style={card}>
      <h2 style={heading}>Historia zadania</h2>
      {loading ? (
        <p style={{ color: '#718096', fontSize: '14px' }}>Wczytywanie…</p>
      ) : events.length === 0 ? (
        <p style={{ color: '#718096', fontSize: '14px' }}>Brak zdarzeń.</p>
      ) : (
        <ul style={{ listStyle: 'none', margin: 0, padding: 0, display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {events.map((e) => (
            <li key={e.eventId} style={{ display: 'flex', gap: '10px', alignItems: 'flex-start' }}>
              <span style={{ marginTop: '4px', width: '8px', height: '8px', borderRadius: '50%', background: '#0070f3', flexShrink: 0 }} />
              <div>
                <div style={{ fontSize: '14px', color: '#1a202c', fontWeight: 600 }}>{e.title}</div>
                {e.description && <div style={{ fontSize: '13px', color: '#4a5568' }}>{e.description}</div>}
                <div style={{ fontSize: '12px', color: '#a0aec0' }}>{e.type} · {e.actorId}</div>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
