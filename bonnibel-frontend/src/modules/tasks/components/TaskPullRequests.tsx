import { useEffect, useState } from 'react'
import { taskActivityService } from '@/services/taskActivityService'
import type { PullRequest, ProjectRole } from '@/types/domain'

const card: React.CSSProperties = { background: 'white', border: '1px solid #e2e8f0', borderRadius: '12px', padding: '20px', boxShadow: '0 4px 6px rgba(0,0,0,0.02)' }
const heading: React.CSSProperties = { margin: '0 0 16px 0', fontSize: '18px', color: '#1a202c' }
const input: React.CSSProperties = { padding: '8px 10px', borderRadius: '6px', border: '1px solid #cbd5e0', fontSize: '14px' }
const btn: React.CSSProperties = { padding: '8px 14px', borderRadius: '6px', border: 'none', color: '#fff', fontSize: '14px', cursor: 'pointer' }

const STATUS_COLORS: Record<PullRequest['status'], string> = { OPEN: '#0070f3', MERGED: '#22863a', CLOSED: '#cb2431' }

export default function TaskPullRequests({ projectId, taskId, onChanged, userRole }: { projectId: number; taskId: number; onChanged?: () => void; userRole?: ProjectRole | null }) {
  const [prs, setPrs] = useState<PullRequest[]>([])
  const [loading, setLoading] = useState(true)
  const [title, setTitle] = useState('')
  const [busy, setBusy] = useState(false)

  const load = () => {
    setLoading(true)
    taskActivityService.getPullRequests(projectId, taskId).then(setPrs).finally(() => setLoading(false))
  }
  useEffect(load, [projectId, taskId])

  const handleCreate = async (e: React.FormEvent) => { /* bez zmian */
    e.preventDefault()
    if (!title.trim()) return
    setBusy(true)
    try {
      await taskActivityService.createPullRequest(projectId, taskId, { title: title.trim() })
      setTitle(''); load(); onChanged?.()
    } catch (err) { window.alert('Błąd dodawania PR') } finally { setBusy(false) }
  }

  const handleDecision = async (prId: number, action: 'approve' | 'decline') => { /* bez zmian */
    setBusy(true)
    try {
      if (action === 'approve') await taskActivityService.approvePullRequest(prId)
      else await taskActivityService.declinePullRequest(prId)
      load(); onChanged?.()
    } catch (err) { window.alert('Błąd decyzji PR') } finally { setBusy(false) }
  }

  // --- LOGIKA UPRAWNIEŃ ---
  const canCreatePR = userRole === 'OWNER' || userRole === 'DEVELOPER'
  const canReviewPR = userRole === 'OWNER' || userRole === 'REVIEWER'
  // ------------------------

  return (
    <div style={card}>
      <h2 style={heading}>Pull Requesty</h2>
      {loading ? <p style={{ fontSize: '14px' }}>Wczytywanie…</p> : prs.length === 0 ? <p style={{ fontSize: '14px' }}>Brak pull requestów.</p> : (
        <ul style={{ listStyle: 'none', margin: '0 0 16px 0', padding: 0, display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {prs.map((pr) => (
            <li key={pr.pullRequestId} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap' }}>
              <span style={{ fontSize: '14px' }}>
                <a href={pr.url} target="_blank" rel="noreferrer" style={{ color: '#0070f3', textDecoration: 'none' }}>🔀 {pr.title}</a>
                <span style={{ marginLeft: '8px', fontSize: '12px', fontWeight: 700, color: STATUS_COLORS[pr.status] }}>{pr.status}</span>
              </span>
              {/* Przyciski widać tylko, jak masz uprawnienia do akceptacji */}
              {pr.status === 'OPEN' && canReviewPR && (
                <span style={{ display: 'flex', gap: '6px' }}>
                  <button onClick={() => handleDecision(pr.pullRequestId, 'approve')} disabled={busy} style={{ ...btn, background: '#22863a' }}>Akceptuj</button>
                  <button onClick={() => handleDecision(pr.pullRequestId, 'decline')} disabled={busy} style={{ ...btn, background: '#cb2431' }}>Odrzuć</button>
                </span>
              )}
            </li>
          ))}
        </ul>
      )}

      {/* Formularz widać tylko dla Deva i Ownera */}
      {canCreatePR && (
        <form onSubmit={handleCreate} style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
          <input style={{ ...input, flex: '3 1 200px' }} placeholder="Tytuł pull requesta" value={title} onChange={(e) => setTitle(e.target.value)} />
          <button type="submit" style={{ ...btn, background: '#0070f3', opacity: busy ? 0.6 : 1 }} disabled={busy}>Utwórz PR</button>
        </form>
      )}
    </div>
  )
}