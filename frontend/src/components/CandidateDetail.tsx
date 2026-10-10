import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { X } from 'lucide-react'
import { api, errorMessage, ApiError } from '../api'
import { useSettings } from '../lib/settings'
import { idFromName, num, pct } from '../lib/utils'
import type { Candidate, ExplainRow } from '../types/api'
import { PredictionBadge, SkillChips, ModelNotice } from './Badges'
import { MetricBar, ProgressRing } from './Visuals'
import { ExplanationView } from './ExplanationChart'
import { CardSkeleton } from './States'

type Load<T> = { status: 'idle' | 'loading' | 'ok' | 'missing' | 'error'; data?: T; message?: string }

function useExplanation(kind: 'shap' | 'lime', id: string, enabled: boolean) {
  const [s, setS] = useState<Load<ExplainRow[]>>({ status: 'idle' })
  useEffect(() => {
    if (!enabled) { setS({ status: 'idle' }); return }
    let live = true
    setS({ status: 'loading' })
    const call = kind === 'shap' ? api.shapCandidate(id) : api.limeCandidate(id)
    call.then((r) => { if (live) setS({ status: 'ok', data: r.data }) })
      .catch((e) => { if (live) setS(e instanceof ApiError && e.kind === 'not_found' ? { status: 'missing' } : { status: 'error', message: errorMessage(e) }) })
    return () => { live = false }
  }, [kind, id, enabled])
  return s
}

function ExplainSection({ title, state }: { title: string; state: Load<ExplainRow[]> }) {
  return (
    <div className="card">
      <div className="card-title">{title}</div>
      {state.status === 'loading' && <CardSkeleton lines={2} />}
      {state.status === 'missing' && <p className="muted small">No {title} explanation exists for this candidate in the backend data.</p>}
      {state.status === 'error' && <p className="muted small">Could not load: {state.message}</p>}
      {state.status === 'ok' && state.data && state.data.length > 0 && <ExplanationView rows={state.data} />}
      {state.status === 'ok' && (!state.data || state.data.length === 0) && <p className="muted small">The backend returned no rows.</p>}
    </div>
  )
}

export function CandidateDetail({ candidate, onClose }: { candidate: Candidate; onClose: () => void }) {
  const { dataMode } = useSettings()
  const id = idFromName(candidate.candidate_name)
  const live = dataMode === 'live'
  const shap = useExplanation('shap', id, live)
  const lime = useExplanation('lime', id, live)

  const req = candidate.required_skill_count ?? candidate.required_skills?.length
  const matched = candidate.matched_skill_count ?? candidate.matched_skills?.length
  const ratio = typeof req === 'number' && req > 0 && typeof matched === 'number' ? matched / req : undefined
  const exp = candidate.experience
  const reqExp = exp?.required_experience_years

  return (
    <div className="stack">
      <div className="row spread">
        <div>
          <h2>{candidate.candidate_name}</h2>
          <p className="muted">{candidate.job_role ?? 'Target role not available'}</p>
        </div>
        <button className="btn btn-ghost btn-icon" onClick={onClose} aria-label="Close details"><X size={18} /></button>
      </div>

      <div className="card row wrap" style={{ gap: 18 }}>
        {ratio !== undefined && <ProgressRing value={ratio} label="Required skills matched" display={`${matched}/${req}`} />}
        <div className="stack" style={{ gap: 8 }}>
          <div className="row"><span className="muted small">Model prediction</span><PredictionBadge label={candidate.prediction} /></div>
          <div className="small"><span className="muted">Experience: </span>{typeof exp?.candidate_experience_years === 'number' ? `${exp.candidate_experience_years} yrs` : 'Not available'}
            {typeof reqExp === 'number' && <> <span className="muted">(required {reqExp})</span></>}
            {typeof exp?.experience_compatible === 'boolean' && <> — {exp.experience_compatible ? 'compatible' : 'below requirement'}</>}</div>
          <div className="small"><span className="muted">Role compatibility: </span>{typeof candidate.role_analysis?.role_compatible === 'boolean' ? (candidate.role_analysis.role_compatible ? 'Compatible' : 'Not compatible') : 'Not available'}</div>
        </div>
      </div>

      <div className="card">
        <div className="card-title">🎯 Skills</div>
        <p className="small muted">Candidate skills</p><SkillChips skills={candidate.candidate_skills} />
        <p className="small muted" style={{ marginTop: 12 }}>Required skills</p><SkillChips skills={candidate.required_skills} />
        <p className="small muted" style={{ marginTop: 12 }}>Matched</p><SkillChips skills={candidate.matched_skills} tone="success" />
        <p className="small muted" style={{ marginTop: 12 }}>Missing</p><SkillChips skills={candidate.missing_skills} tone="warn" />
      </div>

      <div className="card">
        <div className="card-title">📊 Signals</div>
        <MetricBar label="Project relevance" value={candidate.project_analysis?.project_relevance} />
        <MetricBar label="Resume / job text overlap" value={candidate.model_features?.semantic_overlap} />
        <p className="small muted">Overlap: {pct(candidate.model_features?.semantic_overlap)} · Relevance: {num(candidate.project_analysis?.project_relevance)}</p>
      </div>

      {candidate.summary && <div className="card"><div className="card-title">📝 Summary</div><p>{candidate.summary}</p></div>}

      {live ? (
        <>
          <ExplainSection title="SHAP" state={shap} />
          <ExplainSection title="LIME" state={lime} />
        </>
      ) : (
        <div className="alert alert-info">SHAP and LIME explanations come from the backend. Switch to Live backend in Settings to view them.</div>
      )}
      <ModelNotice />
      <Link className="btn btn-ghost" to={`/app/recruiter`}>Ask the AI recruiter about Candidate {id}</Link>
    </div>
  )
}
