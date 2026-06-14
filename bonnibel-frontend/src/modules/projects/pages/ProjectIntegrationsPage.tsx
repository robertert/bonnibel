import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { integrationService, type ProjectIntegration } from '@/services/integrationService'
import type { IntegrationProvider } from '@/types/domain'

const PROVIDERS: { value: IntegrationProvider; label: string; hint: string; tokenHint: string }[] = [
  { value: 'GITHUB', label: 'GitHub', hint: 'np. owner/repo', tokenHint: 'Personal Access Token (Bearer)' },
  { value: 'JIRA', label: 'Jira', hint: 'np. https://twojadomena.atlassian.net', tokenHint: 'email:api_token (Basic)' },
  { value: 'CONFLUENCE', label: 'Confluence', hint: 'np. https://twojadomena.atlassian.net/wiki', tokenHint: 'email:api_token (Basic)' },
]

export default function ProjectIntegrationsPage() {
  const { projectId } = useParams<{ projectId: string }>()
  const pid = Number(projectId)

  const [integrations, setIntegrations] = useState<ProjectIntegration[]>([])
  const [loading, setLoading] = useState(true)
  const [provider, setProvider] = useState<IntegrationProvider>('GITHUB')
  const [externalId, setExternalId] = useState('')
  const [accessToken, setAccessToken] = useState('')
  const [busy, setBusy] = useState(false)

  const load = () => {
    setLoading(true)
    integrationService.list(pid)
      .then(setIntegrations)
      .catch(console.error)
      .finally(() => setLoading(false))
  }

  useEffect(load, [pid])

  const handleConnect = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!externalId.trim() || !accessToken.trim()) return
    setBusy(true)
    try {
      await integrationService.connect(pid, {
        provider,
        external_id: externalId.trim(),
        access_token: accessToken.trim(),
      })
      setExternalId('')
      setAccessToken('')
      load()
    } catch (err) {
      console.error('Nie udało się podłączyć integracji', err)
      window.alert('Nie udało się podłączyć integracji.')
    } finally {
      setBusy(false)
    }
  }

  const handleDisconnect = async (p: IntegrationProvider) => {
    if (!window.confirm(`Odłączyć integrację ${p}?`)) return
    try {
      await integrationService.disconnect(pid, p)
      load()
    } catch (err) {
      console.error('Nie udało się odłączyć integracji', err)
      window.alert('Nie udało się odłączyć integracji.')
    }
  }

  const currentProvider = PROVIDERS.find((p) => p.value === provider)
  const currentHint = currentProvider?.hint

  return (
    <div className="p-8 max-w-2xl">
      <Link to={`/projects/${projectId}`} className="text-sm text-gray-500 hover:text-gray-700">← Powrót do projektu</Link>
      <h1 className="mt-3 text-2xl font-semibold text-gray-900">Integracje projektu</h1>
      <p className="text-sm text-gray-500 mt-1 mb-6">Token dotyczy tego projektu i jest ustawiany przez właściciela.</p>

      {/* Podłączone */}
      <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm mb-6">
        <h2 className="text-lg font-semibold mb-3">Podłączone</h2>
        {loading ? (
          <p className="text-gray-500 text-sm">Wczytywanie…</p>
        ) : integrations.length === 0 ? (
          <p className="text-gray-500 text-sm">Brak podłączonych integracji.</p>
        ) : (
          <ul className="space-y-2">
            {integrations.map((i) => (
              <li key={i.integration_id} className="flex items-center justify-between gap-3 border-b border-gray-100 pb-2 last:border-0">
                <div>
                  <span className="font-medium text-gray-900">{i.provider}</span>
                  <span className="ml-2 text-sm text-gray-500">{i.external_id}</span>
                  <span className={`ml-2 text-[11px] font-semibold px-2 py-0.5 rounded-full ${i.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'}`}>
                    {i.is_active ? 'aktywna' : 'nieaktywna'}
                  </span>
                </div>
                <button onClick={() => handleDisconnect(i.provider)} className="text-sm text-red-600 hover:text-red-800">Odłącz</button>
              </li>
            ))}
          </ul>
        )}
      </div>

      {/* Formularz podłączenia */}
      <form onSubmit={handleConnect} className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm space-y-3">
        <h2 className="text-lg font-semibold">Podłącz integrację</h2>
        <div>
          <label className="block text-sm text-gray-600 mb-1">Dostawca</label>
          <select value={provider} onChange={(e) => setProvider(e.target.value as IntegrationProvider)}
                  className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm">
            {PROVIDERS.map((p) => <option key={p.value} value={p.value}>{p.label}</option>)}
          </select>
        </div>
        <div>
          <label className="block text-sm text-gray-600 mb-1">Identyfikator zewnętrzny</label>
          <input value={externalId} onChange={(e) => setExternalId(e.target.value)} placeholder={currentHint}
                 className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm" />
        </div>
        <div>
          <label className="block text-sm text-gray-600 mb-1">Token dostępu</label>
          <input type="password" value={accessToken} onChange={(e) => setAccessToken(e.target.value)} placeholder="••••••••"
                 className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm" />
          <p className="mt-1 text-xs text-gray-400">Format: {currentProvider?.tokenHint}</p>
        </div>
        <button type="submit" disabled={busy}
                className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-60">
          {busy ? 'Łączenie…' : 'Podłącz'}
        </button>
      </form>
    </div>
  )
}
