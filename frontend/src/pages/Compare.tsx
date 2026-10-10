
import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { GitCompare, Plus, X } from 'lucide-react'
import { api, errorMessage } from '../api'
import { fadeUp, stagger } from '../lib/motion'
import { num } from '../lib/utils'
import type { UploadedCandidatesResponse } from '../types/api'
import { PredictionBadge, SkillChips } from '../components/Badges'
import { Emoji } from '../components/Emoji'
import { EmptyState, ErrorBox } from '../components/States'

type UploadedCandidate =
  UploadedCandidatesResponse['candidates'][number]

export default function Compare() {
  const [candidates, setCandidates] = useState<UploadedCandidate[]>([])
  const [ids, setIds] = useState<string[]>([])
  const [draft, setDraft] = useState('')
  const [busy, setBusy] = useState(false)
  const [loading, setLoading] = useState(true)
  const [err, setErr] = useState<string | null>(null)
  const [selected, setSelected] = useState<UploadedCandidate[]>([])

  async function loadCandidates() {
    setLoading(true)
    setErr(null)

    try {
      const response = await api.listUploadedCandidates()
      setCandidates(response.candidates ?? [])
    } catch (error) {
      setErr(errorMessage(error))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void loadCandidates()
  }, [])

  const add = () => {
    const id = draft.trim()

    if (!id) return

    const candidate = candidates.find(
      item => item.candidate_id === id
    )

    if (!candidate) {
      setErr('Choose a candidate ID from the saved candidates list below.')
      return
    }

    if (ids.includes(id)) {
      setErr('This candidate is already selected.')
      return
    }

    if (ids.length >= 10) {
      setErr('A maximum of 10 candidates can be compared.')
      return
    }

    setErr(null)
    setIds(previous => [...previous, id])
    setDraft('')
    setSelected([])
  }

  const run = async () => {
    setBusy(true)
    setErr(null)

    try {
      const response = await api.compareUploadedCandidates(ids)
      setSelected(response.candidates ?? [])
    } catch (error) {
      setSelected([])
      setErr(errorMessage(error))
    } finally {
      setBusy(false)
    }
  }

  const remove = (id: string) => {
    setIds(previous => previous.filter(item => item !== id))
    setSelected([])
  }

  return (
    <div className="stack">
      <div className="page-head row spread wrap">
        <div>
          <h1>
            Compare candidates{' '}
            <Emoji symbol="🏆" anim="bounce" size={26} />
          </h1>
          <p className="muted">
            Compare real resumes saved by recruiters.
          </p>
        </div>
      </div>

      <div className="card stack">
        <h3>Saved uploaded candidates</h3>

        {loading && (
          <p className="muted">Loading saved candidates…</p>
        )}

        {!loading && candidates.length === 0 && !err && (
          <p className="muted">
            No uploaded candidates found. Upload and screen resumes first.
          </p>
        )}

        {!loading && candidates.length > 0 && (
          <div className="table-wrap">
            <table className="tbl">
              <thead>
                <tr>
                  <th>Select</th>
                  <th>Candidate ID</th>
                  <th>Name</th>
                  <th>Job role</th>
                  <th>Experience</th>
                  <th>Screening score</th>
                </tr>
              </thead>
              <tbody>
                {candidates.map(candidate => (
                  <tr key={candidate.candidate_id}>
                    <td>
                      <button
                        className="btn btn-ghost"
                        disabled={
                          ids.includes(candidate.candidate_id) ||
                          ids.length >= 10
                        }
                        onClick={() => {
                          setErr(null)
                          setIds(previous => [
                            ...previous,
                            candidate.candidate_id,
                          ])
                          setSelected([])
                        }}
                      >
                        <Plus size={14} /> Select
                      </button>
                    </td>
                    <td>{candidate.candidate_id}</td>
                    <td>
                      {candidate.candidate.candidate_name ||
                        candidate.filename}
                    </td>
                    <td>{candidate.job.job_role || 'Not specified'}</td>
                    <td>
                      {num(candidate.candidate.experience_years, 1)} years
                    </td>
                    <td>
                      {candidate.evaluation.screening_match_score == null
                        ? 'Not available'
                        : `${num(
                            candidate.evaluation.screening_match_score,
                            1
                          )}%`}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        <div className="row wrap">
          <label className="field" style={{ flex: 1, minWidth: 200 }}>
            Add candidate by exact ID
            <input
              className="input"
              value={draft}
              onChange={event => setDraft(event.target.value)}
              onKeyDown={event => {
                if (event.key === 'Enter') {
                  event.preventDefault()
                  add()
                }
              }}
              placeholder="Enter an ID from the table"
            />
          </label>

          <button
            className="btn btn-ghost"
            style={{ alignSelf: 'flex-end' }}
            onClick={add}
          >
            <Plus size={16} /> Add
          </button>
        </div>

        <div className="chips" aria-live="polite">
          {ids.map(id => {
            const candidate = candidates.find(
              item => item.candidate_id === id
            )

            return (
              <span
                key={id}
                className="chip chip-link row"
                style={{ gap: 6 }}
              >
                {candidate?.candidate.candidate_name || candidate?.filename || id}
                <button
                  aria-label={`Remove candidate ${id}`}
                  onClick={() => remove(id)}
                  style={{
                    all: 'unset',
                    cursor: 'pointer',
                    display: 'inline-flex',
                  }}
                >
                  <X size={12} />
                </button>
              </span>
            )
          })}
        </div>

        <div className="row wrap">
          <button
            className="btn btn-primary"
            disabled={ids.length < 2 || busy || loading}
            onClick={run}
          >
            <GitCompare size={16} />
            {busy ? 'Comparing…' : `Compare ${ids.length || ''} candidates`}
          </button>

          {ids.length < 2 && (
            <span className="muted small">
              Select at least two candidates.
            </span>
          )}
        </div>

        {err && (
          <ErrorBox
            message={err}
            onRetry={ids.length >= 2 ? run : loadCandidates}
          />
        )}
      </div>

      {!loading && !busy && selected.length === 0 && (
        <EmptyState emoji="🏆" title="No comparison yet">
          Select at least two saved candidates and run the comparison.
        </EmptyState>
      )}

      {selected.length > 0 && (
        <>
          <motion.div
            className="grid g-2"
            variants={stagger}
            initial="hidden"
            animate="show"
          >
            {selected.map((candidate, index) => (
              <motion.div
                key={candidate.candidate_id}
                variants={fadeUp}
                className="card hover stack"
              >
                <div className="row spread">
                  <div>
                    <h3>
                      {candidate.candidate.candidate_name ||
                        candidate.filename}
                    </h3>
                    <p className="muted small">
                      {candidate.job.job_role || 'Role not available'}
                    </p>
                    <p className="muted small">
                      ID: {candidate.candidate_id}
                    </p>
                  </div>
                  <span className="rank-badge">{index + 1}</span>
                </div>

                <p className="small muted">Saved screening result</p>
                <PredictionBadge
                  label={candidate.prediction.prediction || 'Not available'}
                />

                <div>
                  <strong>Screening match score</strong>
                  <p>
                    {candidate.evaluation.screening_match_score == null
                      ? 'Not available'
                      : `${num(
                          candidate.evaluation.screening_match_score,
                          1
                        )}%`}
                  </p>
                </div>

                <div>
                  <strong>Experience</strong>
                  <p>
                    {num(candidate.candidate.experience_years, 1)} years
                    {' / '}
                    {num(candidate.job.required_experience, 1)} required
                  </p>
                </div>

                <div>
                  <strong>Skills</strong>
                  <SkillChips
                    skills={candidate.candidate.skills ?? []}
                  />
                </div>

                <div>
                  <strong>Required skills</strong>
                  <SkillChips
                    skills={candidate.job.required_skills ?? []}
                  />
                </div>

                <div>
                  <strong>Previous role</strong>
                  <p>{candidate.candidate.previous_role || 'Not available'}</p>
                </div>

                <div>
                  <strong>Projects</strong>
                  <ul className="small">
                    {(candidate.candidate.projects ?? []).map(
                      (project, projectIndex) => (
                        <li key={`${candidate.candidate_id}-${projectIndex}`}>
                          {typeof project === 'string'
                            ? project
                            : JSON.stringify(project)}
                        </li>
                      )
                    )}
                  </ul>
                </div>

                <p className="muted small">
                  Resume: {candidate.filename}
                </p>
              </motion.div>
            ))}
          </motion.div>

          <div className="card">
            <div className="card-title">Side-by-side comparison</div>
            <div className="table-wrap">
              <table className="tbl">
                <thead>
                  <tr>
                    <th>Measure</th>
                    {selected.map(candidate => (
                      <th key={candidate.candidate_id}>
                        {candidate.candidate.candidate_name ||
                          candidate.filename}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td>Candidate ID</td>
                    {selected.map(candidate => (
                      <td key={candidate.candidate_id}>
                        {candidate.candidate_id}
                      </td>
                    ))}
                  </tr>
                  <tr>
                    <td>Job role</td>
                    {selected.map(candidate => (
                      <td key={candidate.candidate_id}>
                        {candidate.job.job_role || 'Not specified'}
                      </td>
                    ))}
                  </tr>
                  <tr>
                    <td>Screening match score</td>
                    {selected.map(candidate => (
                      <td key={candidate.candidate_id}>
                        {candidate.evaluation.screening_match_score == null
                          ? 'Not available'
                          : `${num(
                              candidate.evaluation.screening_match_score,
                              1
                            )}%`}
                      </td>
                    ))}
                  </tr>
                  <tr>
                    <td>Saved prediction</td>
                    {selected.map(candidate => (
                      <td key={candidate.candidate_id}>
                        {candidate.prediction.prediction || 'Not available'}
                      </td>
                    ))}
                  </tr>
                  <tr>
                    <td>Experience</td>
                    {selected.map(candidate => (
                      <td key={candidate.candidate_id}>
                        {num(candidate.candidate.experience_years, 1)} years
                      </td>
                    ))}
                  </tr>
                  <tr>
                    <td>Previous role</td>
                    {selected.map(candidate => (
                      <td key={candidate.candidate_id}>
                        {candidate.candidate.previous_role || 'Not available'}
                      </td>
                    ))}
                  </tr>
                  <tr>
                    <td>Skills</td>
                    {selected.map(candidate => (
                      <td key={candidate.candidate_id}>
                        {(candidate.candidate.skills ?? []).join(', ') ||
                          'Not available'}
                      </td>
                    ))}
                  </tr>
                  <tr>
                    <td>Projects</td>
                    {selected.map(candidate => (
                      <td key={candidate.candidate_id}>
                        {(candidate.candidate.projects ?? [])
                          .map(project =>
                            typeof project === 'string'
                              ? project
                              : JSON.stringify(project)
                          )
                          .join(', ') || 'Not available'}
                      </td>
                    ))}
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  )
}
