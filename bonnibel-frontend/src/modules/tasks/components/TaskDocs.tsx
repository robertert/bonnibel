import { useEffect, useState } from 'react'
import { docsService } from '@/services/docsService'
import type { TaskDoc, ProjectRole } from '@/types/domain'

// Style pominięte dla zwięzłości - wklej swoje stare style (card, heading, input, btn) z poprzedniego pliku!
const card: React.CSSProperties = { background: 'white', border: '1px solid #e2e8f0', borderRadius: '12px', padding: '20px', boxShadow: '0 4px 6px rgba(0,0,0,0.02)' }
const heading: React.CSSProperties = { margin: '0 0 16px 0', fontSize: '18px', color: '#1a202c' }
const input: React.CSSProperties = { padding: '8px 10px', borderRadius: '6px', border: '1px solid #cbd5e0', fontSize: '14px' }
const btn: React.CSSProperties = { padding: '8px 14px', borderRadius: '6px', border: 'none', background: '#0070f3', color: '#fff', fontSize: '14px', cursor: 'pointer' }

export default function TaskDocs({ projectId, taskId, userRole }: { projectId: number; taskId: number; userRole?: ProjectRole | null }) {
  const [docs, setDocs] = useState<TaskDoc[]>([])
  const [loading, setLoading] = useState(true)
  const [title, setTitle] = useState('')
  const [url, setUrl] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const load = () => {
    setLoading(true)
    docsService.getTaskDocs(projectId, taskId)
      .then((doc) => setDocs([doc]))
      .catch(() => setDocs([]))
      .finally(() => setLoading(false))
  }
  useEffect(load, [projectId, taskId])

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!title.trim() || !url.trim()) return
    setSubmitting(true)
    try {
      await docsService.addTaskDocs(projectId, taskId, { title: title.trim(), url: url.trim() })
      setTitle(''); setUrl(''); load()
    } catch (err) { window.alert('Błąd dodawania.') } finally { setSubmitting(false) }
  }

  const canAdd = userRole === 'OWNER' || userRole === 'DEVELOPER'

  return (
    <div style={card}>
      <h2 style={heading}>Dokumentacja</h2>
      {loading ? <p style={{ fontSize: '14px' }}>Wczytywanie…</p> : docs.length === 0 ? <p style={{ fontSize: '14px' }}>Brak dokumentów.</p> : (
        <ul style={{ listStyle: 'none', margin: '0 0 16px 0', padding: 0, display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {docs.map((d) => (
            <li key={d.docsId} style={{ fontSize: '14px' }}>
              <a href={d.url} target="_blank" rel="noreferrer" style={{ color: '#0070f3', textDecoration: 'none' }}>📄 {d.title}</a>
            </li>
          ))}
        </ul>
      )}

      {canAdd && (
        <form onSubmit={handleAdd} style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
          <input style={{ ...input, flex: '2 1 160px' }} placeholder="Tytuł dokumentu" value={title} onChange={(e) => setTitle(e.target.value)} />
          <input style={{ ...input, flex: '3 1 200px' }} placeholder="URL" value={url} onChange={(e) => setUrl(e.target.value)} />
          <button type="submit" style={{ ...btn, opacity: submitting ? 0.6 : 1 }} disabled={submitting}>Dodaj</button>
        </form>
      )}
    </div>
  )
}