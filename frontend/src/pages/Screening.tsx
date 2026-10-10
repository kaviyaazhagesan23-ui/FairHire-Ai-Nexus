import { useRef, useState } from 'react'
import { motion } from 'framer-motion'
import { FileUp } from 'lucide-react'
import { api, errorMessage } from '../api'
import { num } from '../lib/utils'
import type {
  UploadPredictResponse,
  UploadCompareResponse,
} from '../types/api'
import { Emoji } from '../components/Emoji'
import { ModelNotice, PredictionBadge, SkillChips } from '../components/Badges'
import { BarsChart } from '../components/ExplanationChart'
import { ErrorBox } from '../components/States'

const MAX_MB = 5 // client-side guard only; the backend sets no explicit limit

export default function Screening() {
  const [file, setFile] = useState<File | null>(null)
  const [selectedFiles, setSelectedFiles] = useState<File[]>([])
const [comparisonResult, setComparisonResult] =useState<UploadCompareResponse | null>(null)
  const [over, setOver] = useState(false)
  const [role, setRole] = useState('')
  const [jd, setJd] = useState('')
  const [reqSkills, setReqSkills] = useState('')
  const [reqExp, setReqExp] = useState('0')
  const [busy, setBusy] = useState(false)
  const [err, setErr] = useState<string | null>(null)
  const [res, setRes] = useState<UploadPredictResponse | null>(null)
  const input = useRef<HTMLInputElement>(null)

  const pick = (f: File | undefined | null) => {
    if (!f) return
    const ok = /\.(pdf|docx)$/i.test(f.name)
    if (!ok) { setErr('Unsupported file type. Please upload a PDF or DOCX resume.'); return }
    if (f.size > MAX_MB * 1024 * 1024) { setErr(`File is larger than ${MAX_MB} MB.`); return }
    setErr(null); setFile(f)
  }

  const submit = (e: React.FormEvent) => { e.preventDefault(); void run() }

  const run = async () => {
    if (!file) { setErr('Choose a resume first.'); return }
    if (!role.trim() || !jd.trim()) { setErr('Job role and job description are required.'); return }
    const form = new FormData()
    form.append('file', file)
    form.append('job_role', role.trim())
    form.append('job_description', jd.trim())
    form.append('required_skills', reqSkills.trim())
    form.append('required_experience', String(Number(reqExp) || 0))
    setBusy(true); setErr(null); setRes(null)
    try { setRes(await api.uploadPredict(form)) } catch (er) { setErr(errorMessage(er)) } finally { setBusy(false) }
  }
  const compareResumes = async () => {
  if (selectedFiles.length < 2 || selectedFiles.length > 10) {
    setErr('Please select between 2 and 10 resumes to compare.')
    return
  }

  setBusy(true)
  setErr(null)
  setComparisonResult(null)

  try {
    const form = new FormData()

    selectedFiles.forEach((file) => {
      form.append('files', file)
    })

    form.append('job_role', role)
    form.append('job_description', jd)
    form.append('required_skills', reqSkills)
    form.append('required_experience', reqExp || '0')

    const response = await api.compareUploads(form)
    setComparisonResult(response)
  } catch (error) {
    setErr(errorMessage(error))
  } finally {
    setBusy(false)
  }
}
  const required = res ? res.job.required_skills.split(',').map((s) => s.trim()).filter(Boolean) : []
  const have = new Set((res?.candidate.skills ?? []).map((s) => s.toLowerCase()))
  const missing = required.filter((s) => !have.has(s.toLowerCase()))

  return (
    <div className="stack">
      <div className="page-head"><h1>Resume screening <Emoji symbol="📄" anim="bounce" size={26} /></h1>
        <p className="muted">Upload a PDF or DOCX. The backend extracts skills, runs the SVM pipeline and returns SHAP and LIME explanations.</p></div>

      <form className="grid g-2" onSubmit={submit}>
        <div className="card stack">
          <div className={`drop ${over ? 'over' : ''}`} onClick={() => input.current?.click()} role="button" tabIndex={0} aria-label="Choose or drop a resume file"
            onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); input.current?.click() } }}
            onDragOver={(e) => { e.preventDefault(); setOver(true) }} onDragLeave={() => setOver(false)}
            onDrop={(e) => { e.preventDefault(); setOver(false); pick(e.dataTransfer.files?.[0]) }}>
            <Emoji symbol="📥" anim="float" size={38} />
            <p style={{ fontWeight: 700, marginTop: 8 }}>{file ? file.name : 'Drag & drop a resume, or click to browse'}</p>
            <p className="muted small">PDF or DOCX · up to {MAX_MB} MB</p>
            <input ref={input} type="file" accept=".pdf,.docx" hidden onChange={(e) => pick(e.target.files?.[0])} />
          </div>
        </div>
        <div className="card stack">
          <label className="field">Job role *<input className="input" value={role} onChange={(e) => setRole(e.target.value)} placeholder="e.g. DevOps Engineer" /></label>
          <label className="field">Job description *<textarea className="textarea" value={jd} onChange={(e) => setJd(e.target.value)} /></label>
          <label className="field">Required skills (comma separated)<input className="input" value={reqSkills} onChange={(e) => setReqSkills(e.target.value)} placeholder="Docker, Kubernetes, AWS" /></label>
          <label className="field">Required experience (years)<input className="input" type="number" min="0" step="0.5" value={reqExp} onChange={(e) => setReqExp(e.target.value)} /></label>
      <div className="card stack">
        <label className="field">
          Job role *
          <input
            className="input"
            value={role}
            onChange={(e) => setRole(e.target.value)}
            placeholder="e.g. DevOps Engineer"
          />
        </label>

        <label className="field">
          Job description *
          <textarea
            className="textarea"
            value={jd}
            onChange={(e) => setJd(e.target.value)}
          />
        </label>

        <label className="field">
          Required skills (comma separated)
          <input
            className="input"
            value={reqSkills}
            onChange={(e) => setReqSkills(e.target.value)}
            placeholder="Docker, Kubernetes, AWS"
          />
        </label>

        <label className="field">
          Required experience (years)
          <input
            className="input"
            type="number"
            min="0"
            step="0.5"
            value={reqExp}
            onChange={(e) => setReqExp(e.target.value)}
          />
        </label>

        <button
          type="submit"
          className="btn btn-primary"
          disabled={busy}
        >
          <FileUp size={16} />
          {busy ? 'Analysing…' : 'Analyse resume'}
        </button>

        <hr />

        <h3>Compare real resumes</h3>
        <p className="muted small">
          Select 2–10 PDF or DOCX resumes for comparison against the same job.
        </p>

                <label className="field">
          Select multiple resumes
          <input
            className="input"
            type="file"
            accept=".pdf,.docx"
            multiple
            onChange={(e) => {
              setSelectedFiles(Array.from(e.target.files ?? []))
              setComparisonResult(null)
              setErr(null)
            }}
          />
        </label>
        {selectedFiles.length > 0 && (
          <p className="small">
            {selectedFiles.length} resume(s) selected
          </p>
        )}

        <button
          type="button"
          className="btn"
          disabled={busy || selectedFiles.length < 2 || selectedFiles.length > 10}
          onClick={() => void compareResumes()}
        >
          {busy ? 'Comparing…' : 'Compare Resumes'}
        </button>
      </div>
              </div>
      </form>

      {err && <ErrorBox message={err} onRetry={file ? () => void run() : undefined} />}

      {busy && (
        <div className="card" role="status" aria-live="polite">
          <div className="scan"><i /><i /><i /><i /><i /><i /><i /></div>
          <p style={{ textAlign: 'center', marginTop: 14 }}><Emoji symbol="⚡" anim="pulse" size={18} /> Parsing resume and running the model…</p>
          <p className="muted small" style={{ textAlign: 'center' }}>Upload progress isn't reported by the backend, so this indicator is indeterminate.</p>
        </div>
      )}

      {res && (
        <motion.div className="stack" initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }}>
          <div className="alert alert-info">
  <Emoji symbol="🎉" anim="bounce" size={18} />
  Analysis complete for {res.filename}.
  <p>
    Candidate ID: <strong className="mono">{res.candidate_id}</strong>
    <button
      type="button"
      className="btn"
      onClick={() => void navigator.clipboard.writeText(res.candidate_id)}
    >
      Copy ID
    </button>
  </p>
</div>
          <div className="grid g-2">
            <div className="card">
              <div className="card-title">🎯 Prediction</div>
              <div className="row"><PredictionBadge label={res.prediction.label} /></div>
              <p className="small muted" style={{ marginTop: 10 }}>SVM decision score: <strong className="mono">{num(res.prediction.decision_score, 4)}</strong>. This is a signed distance from the decision boundary, not a probability.</p>
              <p style={{ marginTop: 10 }}><strong>{res.candidate.candidate_name || 'Name not detected'}</strong> · {res.candidate.experience_years} yrs · {res.candidate.previous_role || 'previous role not detected'}</p>
            </div>
            <div className="card">
              <div className="card-title">🧠 Skills</div>
              <p className="small muted">Detected in resume</p><SkillChips skills={res.candidate.skills} />
              {required.length > 0 && <><p className="small muted" style={{ marginTop: 10 }}>Required skills not found (computed in browser from your input)</p><SkillChips skills={missing} tone="warn" /></>}
            </div>
          </div>
          {res.candidate.projects.length > 0 && <div className="card"><div className="card-title">🚀 Projects detected</div><ul style={{ margin: 0, paddingLeft: 18 }}>{res.candidate.projects.map((p) => <li key={p}>{p}</li>)}</ul></div>}
          {res.explanations.available && (
            <div className="grid g-2">
              <div className="card"><div className="card-title">SHAP — top features</div><BarsChart rows={res.explanations.shap.top_features.map((f) => ({ label: f.feature, value: f.shap_value ?? 0 }))} /></div>
              <div className="card"><div className="card-title">LIME — top features</div><BarsChart rows={res.explanations.lime.top_features.map((f) => ({ label: f.feature, value: f.lime_weight ?? 0 }))} /></div>
            </div>
          )}
          <ModelNotice />
        </motion.div>
      )}
            

      
      {comparisonResult && (
        <motion.div
          className="card stack"
          initial={{ opacity: 0, y: 14 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <div className="card-title">🏆 Real Resume Comparison</div>

          <p className="muted small">
            Compared {comparisonResult.results.length} uploaded resumes for{' '}
            {comparisonResult.job.job_role}.
          </p>

          {comparisonResult.results.map((item) => (
            <div className="card" key={item.filename}>
              <div className="row">
                <strong>
                  #{item.rank} — {item.candidate.candidate_name || item.filename}
                </strong>
              </div>

              <p className="small">File: {item.filename}</p>
              <p className="small">
  Candidate ID: <strong className="mono">{item.candidate_id}</strong>
  <button
    type="button"
    className="btn"
    onClick={() => void navigator.clipboard.writeText(item.candidate_id)}
  >
    Copy ID
  </button>
</p>

                           <p className="small">
                AI model prediction: <strong>{item.evaluation.prediction}</strong>
              </p>

              <p className="small">
                Rule-based screening score:{' '}
                <strong>
                  {item.evaluation.screening_match_score != null
                    ? `${item.evaluation.screening_match_score.toFixed(1)}%`
                    : 'Not available'}
                </strong>
              </p>

              <p className="muted small">
                These are separate metrics. The screening score measures
                required-skill coverage and the experience requirement.
                The AI prediction comes from the trained classification model.
                Neither metric guarantees hiring suitability.
              </p>

              <p className="small">
                Matched skills:{' '}
                {item.evaluation.matched_skills.join(', ') || 'None detected'}
              </p>

              <p className="small">
                Missing skills:{' '}
                {item.evaluation.missing_skills.join(', ') || 'None'}
              </p>
            </div>
          ))}
        </motion.div>
      )}

    
    </div>
  )
}
