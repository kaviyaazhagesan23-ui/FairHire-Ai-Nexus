import { useCallback, useEffect, useState } from 'react'
import { RefreshCw } from 'lucide-react'
import { API_BASE_URL, api } from '../api'
import { cx } from '../lib/utils'

export type ApiState = 'checking' | 'online' | 'offline'

export function useApiHealth() {
  const [state, setState] = useState<ApiState>('checking')
  const [model, setModel] = useState<string | null>(null)
  const check = useCallback(async () => {
    setState('checking')
    try {
      const h = await api.health()
      setModel(h.model)
      setState(h.status === 'healthy' ? 'online' : 'offline')
    } catch {
      setModel(null)
      setState('offline')
    }
  }, [])
  useEffect(() => { void check() }, [check])
  return { state, model, check }
}

export function ApiStatusPill({ state, onRefresh }: { state: ApiState; onRefresh?: () => void }) {
  const text = state === 'online' ? 'API online' : state === 'checking' ? 'Checking API…' : 'API offline'
  return (
    <button
      className={cx('badge', state === 'online' ? 'badge-success' : state === 'offline' ? 'badge-error' : 'badge-neutral')}
      onClick={onRefresh} title={`${API_BASE_URL} — click to re-check`} aria-label={`${text}. Click to re-check connection`}
      style={{ cursor: 'pointer', font: 'inherit', fontSize: '.75rem', fontWeight: 700 }}
    >
      <RefreshCw size={11} className={state === 'checking' ? 'spin' : ''} aria-hidden="true" /> {text}
    </button>
  )
}
