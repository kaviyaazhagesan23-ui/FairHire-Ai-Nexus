import { AlertTriangle, RotateCw } from 'lucide-react'
import type { ReactNode } from 'react'
import { Emoji } from './Emoji'

export function Skeleton({ h = 16, w = '100%', r = 10 }: { h?: number; w?: number | string; r?: number }) {
  return <div className="skeleton" style={{ height: h, width: w, borderRadius: r }} aria-hidden="true" />
}

export function CardSkeleton({ lines = 3 }: { lines?: number }) {
  return (
    <div className="card" role="status" aria-label="Loading">
      <Skeleton h={14} w="40%" />
      <div style={{ height: 14 }} />
      {Array.from({ length: lines }).map((_, i) => (
        <div key={i} style={{ marginBottom: 10 }}><Skeleton h={12} w={`${90 - i * 14}%`} /></div>
      ))}
    </div>
  )
}

export function EmptyState({ emoji = '🔍', title, children, action }: { emoji?: string; title: string; children?: ReactNode; action?: ReactNode }) {
  return (
    <div className="empty">
      <Emoji symbol={emoji} anim="float" size={40} />
      <h3>{title}</h3>
      {children && <p className="muted">{children}</p>}
      {action}
    </div>
  )
}

export function ErrorBox({ message, onRetry }: { message: string; onRetry?: () => void }) {
  return (
    <div className="alert alert-error" role="alert">
      <AlertTriangle size={18} aria-hidden="true" />
      <div style={{ flex: 1 }}>{message}</div>
      {onRetry && (
        <button className="btn btn-sm btn-ghost" onClick={onRetry}><RotateCw size={14} /> Retry</button>
      )}
    </div>
  )
}
