
import { useEffect, useMemo, useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { useSearchParams } from 'react-router-dom'
import { ChevronLeft, ChevronRight, Search } from 'lucide-react'

import { api, errorMessage } from '../api'
import { useSettings } from '../lib/settings'
import { fadeUp, stagger } from '../lib/motion'
import { idFromName } from '../lib/utils'
import type { Candidate, SavedUploadedCandidate } from '../types/api'
import { CandidateDetail } from '../components/CandidateDetail'
import { DemoBadge, PredictionBadge, SkillChips } from '../components/Badges'
import { Emoji } from '../components/Emoji'
import { CardSkeleton, EmptyState, ErrorBox } from '../components/States'

const PAGE = 6

type Sort = 'id' | 'skills' | 'experience'

export default function Candidates() {
  const { dataMode } = useSettings()
  const [params, setParams] = useSearchParams()
  const [selected, setSelected] = useState<Candidate | null>(null)
  const [q, setQ] = useState('')
  const [role, setRole] = useState('all')
  const [pred, setPred] = useState('all')
  const [sort, setSort] = useState<Sort>('id')
  const [page, setPage] = useState(1)

  const [uploaded, setUploaded] = useState<SavedUploadedCandidate[]>([])
  const [uploadedBusy, setUploadedBusy] = useState(false)
  const [uploadedErr, setUploadedErr] = useState<string | null>(null)

  const list = api.listCandidates()

  useEffect(() => {
    if (dataMode === 'demo') return

    let active = true

    async function loadUploaded() {
      setUploadedBusy(true)
      setUploadedErr(null)

      try {
        const response = await api.listUploadedCandidates()
        if (active) setUploaded(response.candidates ?? [])
      } catch (error) {
        if (active) setUploadedErr(errorMessage(error))
      } finally {
        if (active) setUploadedBusy(false)
      }
    }

    void loadUploaded()

    return () => {
      active = false
    }
  }, [dataMode])

  const find = async (id: string) => {
    const clean = id.trim().replace(/^candidate\s*/i, '')
    if (!clean) return

    try {
      const candidate = await api.getCandidate(clean)
      setSelected(candidate)
    } catch (error) {
      console.error(errorMessage(error))
    }
  }

  useEffect(() => {
    const id = params.get('id')
    if (id) {
      void find(id)
      setParams({}, { replace: true })
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const roles = useMemo(
    () =>
      Array.from(
        new Set(
          (list ?? [])
            .map((candidate) => candidate.job_role)
            .filter(Boolean),
        ),
      ) as string[],
    [list],
  )

  const filtered = useMemo(() => {
    if (!list) return []

    const needle = q.trim().toLowerCase()

    const result = list.filter(
      (candidate) =>
        (role === 'all' || candidate.job_role === role) &&
        (pred === 'all' || candidate.prediction === pred) &&
        (!needle ||
          [
            candidate.candidate_name,
            candidate.job_role,
            ...(candidate.candidate_skills ?? []),
          ]
            .join(' ')
            .toLowerCase()
            .includes(needle)),
    )

    result.sort((a, b) =>
      sort === 'id'
        ? Number(idFromName(a.candidate_name)) -
          Number(idFromName(b.candidate_name))
        : sort === 'skills'
          ? (b.matched_skill_count ?? 0) -
            (a.matched_skill_count ?? 0)
          : (b.experience?.candidate_experience_years ?? 0) -
            (a.experience?.candidate_experience_years ?? 0),
    )

    return result
  }, [list, q, role, pred, sort])

  useEffect(() => {
    setPage(1)
  }, [q, role, pred, sort, dataMode])

  const pages = Math.max(1, Math.ceil(filtered.length / PAGE))
  const view = filtered.slice((page - 1) * PAGE, page * PAGE)

  const card = (candidate: Candidate) => (
    <motion.button
      key={candidate.candidate_name}
      variants={fadeUp}
      className="card hover cand-card"
      onClick={() => setSelected(candidate)}
    >
      <div className="row spread">
        <h3>{candidate.candidate_name}</h3>
        <PredictionBadge label={candidate.prediction} />
      </div>

      <p className="muted small" style={{ margin: '4px 0 10px' }}>
        {candidate.job_role ?? 'Role not available'} ·{' '}
        {typeof candidate.experience?.candidate_experience_years === 'number'
          ? `${candidate.experience.candidate_experience_years} yrs`
          : 'experience n/a'}
      </p>

      <SkillChips
        skills={(candidate.candidate_skills ?? []).slice(0, 5)}
      />

      <p className="small" style={{ marginTop: 10 }}>
        <strong>
          {candidate.matched_skill_count ??
            candidate.matched_skills?.length ??
            '–'}
        </strong>
        /
        {candidate.required_skill_count ??
          candidate.required_skills?.length ??
          '–'}{' '}
        required skills matched
      </p>
    </motion.button>
  )

  return (
    <div className="stack">
      <div className="page-head row spread wrap">
        <div>
          <h1>
            Candidates <Emoji symbol="👥" anim="bounce" size={26} />
          </h1>
          <p className="muted">
            Browse candidate intelligence and open full profiles.
          </p>
        </div>
        {dataMode === 'demo' && <DemoBadge />}
      </div>

      {dataMode === 'demo' && list ? (
        <>
          <div className="card grid g-4" style={{ alignItems: 'end' }}>
            <label className="field">
              Search
              <span className="input-wrap">
                <Search size={16} aria-hidden="true" />
                <input
                  className="input"
                  value={q}
                  onChange={(event) => setQ(event.target.value)}
                  placeholder="ID, role or skill"
                />
              </span>
            </label>

            <label className="field">
              Role
              <select
                className="select"
                value={role}
                onChange={(event) => setRole(event.target.value)}
              >
                <option value="all">All roles</option>
                {roles.map((item) => (
                  <option key={item}>{item}</option>
                ))}
              </select>
            </label>

            <label className="field">
              Prediction
              <select
                className="select"
                value={pred}
                onChange={(event) => setPred(event.target.value)}
              >
                <option value="all">All</option>
                <option>Strong Match</option>
                <option>Weak Match</option>
              </select>
            </label>

            <label className="field">
              Sort by
              <select
                className="select"
                value={sort}
                onChange={(event) => setSort(event.target.value as Sort)}
              >
                <option value="id">Candidate ID</option>
                <option value="skills">Matched skills</option>
                <option value="experience">Experience</option>
              </select>
            </label>
          </div>

          {view.length === 0 ? (
            <EmptyState emoji="🔍" title="No candidates match">
              Try clearing filters or searching for a different skill.
            </EmptyState>
          ) : (
            <motion.div
              className="grid g-3"
              variants={stagger}
              initial="hidden"
              animate="show"
              key={`${page}-${q}-${role}-${pred}-${sort}`}
            >
              {view.map(card)}
            </motion.div>
          )}

          <div className="pager">
            <button
              className="btn btn-ghost btn-sm"
              disabled={page <= 1}
              onClick={() => setPage(page - 1)}
              aria-label="Previous page"
            >
              <ChevronLeft size={16} />
            </button>

            <span className="small">
              Page {page} of {pages} · {filtered.length} candidates
            </span>

            <button
              className="btn btn-ghost btn-sm"
              disabled={page >= pages}
              onClick={() => setPage(page + 1)}
              aria-label="Next page"
            >
              <ChevronRight size={16} />
            </button>
          </div>
        </>
      ) : (
        <>
          <div className="card row spread wrap">
            <div>
              <h2>Uploaded Candidates</h2>
              <p className="muted small">
                Manage and review resumes screened by FairHire AI.
              </p>
            </div>
            <strong>{uploaded.length} candidates</strong>
          </div>

          {uploadedErr && <ErrorBox message={uploadedErr} />}

          {uploadedBusy ? (
            <CardSkeleton />
          ) : uploaded.length === 0 && !uploadedErr ? (
            <EmptyState emoji="📄" title="No uploaded candidates yet">
              Upload and screen a resume first.
            </EmptyState>
          ) : (
            <div
              className="card"
              style={{ padding: 0, overflowX: 'auto' }}
            >
              <table
                style={{
                  width: '100%',
                  borderCollapse: 'collapse',
                  textAlign: 'left',
                  minWidth: 850,
                }}
              >
                <thead>
                  <tr
                    style={{
                      background: 'var(--surface, #f8f7ff)',
                    }}
                  >
                    {[
                      'Candidate',
                      'Job role',
                      'Experience',
                      'Match score',
                      'Status',
                      'Actions',
                    ].map((heading) => (
                      <th
                        key={heading}
                        style={{
                          padding: 16,
                          fontSize: 12,
                          textTransform: 'uppercase',
                          letterSpacing: '0.04em',
                          whiteSpace: 'nowrap',
                          borderBottom:
                            '1px solid var(--border, #e5e7eb)',
                        }}
                      >
                        {heading}
                      </th>
                    ))}
                  </tr>
                </thead>

                <tbody>
                  {uploaded.map((record) => (
                    <tr key={record.candidate_id}>
                      <td
                        style={{
                          padding: 16,
                          borderBottom:
                            '1px solid var(--border, #e5e7eb)',
                        }}
                      >
                        <strong>
                          {record.candidate.candidate_name ||
                            record.filename}
                        </strong>
                        <p
                          className="muted small"
                          style={{ margin: '5px 0 0' }}
                        >
                          {record.candidate_id}
                        </p>
                        <p
                          className="muted small"
                          style={{ margin: '3px 0 0' }}
                        >
                          {record.filename}
                        </p>
                      </td>

                      <td
                        style={{
                          padding: 16,
                          borderBottom:
                            '1px solid var(--border, #e5e7eb)',
                        }}
                      >
                        {record.job.job_role || 'Not specified'}
                      </td>

                      <td
                        style={{
                          padding: 16,
                          whiteSpace: 'nowrap',
                          borderBottom:
                            '1px solid var(--border, #e5e7eb)',
                        }}
                      >
                        {record.candidate.experience_years} years
                      </td>

                      <td
                        style={{
                          padding: 16,
                          whiteSpace: 'nowrap',
                          borderBottom:
                            '1px solid var(--border, #e5e7eb)',
                        }}
                      >
                        {record.evaluation.screening_match_score == null
                          ? '—'
                          : `${record.evaluation.screening_match_score.toFixed(1)}%`}
                      </td>

                      <td
                        style={{
                          padding: 16,
                          whiteSpace: 'nowrap',
                          borderBottom:
                            '1px solid var(--border, #e5e7eb)',
                        }}
                      >
                        <PredictionBadge
                          label={record.prediction.prediction}
                        />
                      </td>

                      <td
                        style={{
                          padding: 16,
                          whiteSpace: 'nowrap',
                          borderBottom:
                            '1px solid var(--border, #e5e7eb)',
                        }}
                      >
                        <button
                          type="button"
                          className="btn btn-primary btn-sm"
                          onClick={() =>
                            setSelected({
                              candidate_name:
                                record.candidate.candidate_name ||
                                record.filename,
                              job_role: record.job.job_role,
                              prediction: record.prediction.prediction,
                              candidate_skills:
                                record.candidate.skills ?? [],
                              required_skills:
                                record.job.required_skills ?? [],
                              experience: {
                                candidate_experience_years:
                                  record.candidate.experience_years,
                                required_experience_years:
                                  record.job.required_experience,
                              },
                              summary: `Uploaded resume: ${record.filename}`,
                            })
                          }
                        >
                          View profile
                        </button>

                        
<button
  type="button"
  className="btn btn-ghost btn-sm"
  style={{ marginLeft: 8, color: '#dc2626' }}
  onClick={async () => {
    const name =
      record.candidate.candidate_name || record.filename

    if (!window.confirm(`Permanently delete ${name}?`)) return

    try {
      setUploadedErr(null)

      await api.deleteUploadedCandidate(record.candidate_id)

      setUploaded((current) =>
        current.filter(
          (item) => item.candidate_id !== record.candidate_id,
        ),
      )

      if (selected?.candidate_name === name) {
        setSelected(null)
      }
    } catch (error) {
      setUploadedErr(errorMessage(error))
    }
  }}
>
  Delete
</button>

                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}

      <AnimatePresence>
        {selected && (
          <>
            <motion.div
              className="drawer-scrim"
              onClick={() => setSelected(null)}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            />

            <motion.aside
              className="drawer"
              role="dialog"
              aria-modal="true"
              aria-label="Candidate details"
              initial={{ x: 60, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              exit={{ x: 60, opacity: 0 }}
              transition={{
                type: 'spring',
                damping: 30,
                stiffness: 300,
              }}
            >
              <CandidateDetail
                candidate={selected}
                onClose={() => setSelected(null)}
              />
            </motion.aside>
          </>
        )}
      </AnimatePresence>
    </div>
  )
}
