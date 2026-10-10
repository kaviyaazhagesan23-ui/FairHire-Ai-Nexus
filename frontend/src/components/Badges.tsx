import { CheckCircle2, CircleSlash, FlaskConical } from 'lucide-react'
import { cx, isStrong } from '../lib/utils'

export function PredictionBadge({ label }: { label?: string }) {
  if (!label) return <span className="badge badge-neutral">Not available</span>
  const strong = isStrong(label)
  return (
    <span className={cx('badge', strong ? 'badge-success' : 'badge-warn')}>
      {strong ? <CheckCircle2 size={12} aria-hidden="true" /> : <CircleSlash size={12} aria-hidden="true" />}
      {label}
    </span>
  )
}

export function DemoBadge() {
  return (
    <span className="badge badge-violet" title="Invented sample data for UI preview. Not FairHire model output.">
      <FlaskConical size={12} aria-hidden="true" /> Demo data
    </span>
  )
}

export function SkillChips({ skills, tone = 'neutral' }: { skills?: string[]; tone?: 'neutral' | 'success' | 'warn' }) {
  if (!skills) return <span className="muted small">Not available</span>
  if (!skills.length) return <span className="muted small">None</span>
  return (
    <div className="chips">
      {skills.map((s) => <span key={s} className={cx('chip', `chip-${tone}`)}>{s}</span>)}
    </div>
  )
}

export function ModelNotice() {
  return (
    <p className="notice small">
      🧭 FairHire AI is decision support for human recruiters.
    </p>
  )
}
