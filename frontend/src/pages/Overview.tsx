
import { useEffect, useMemo, useState } from 'react'
import { motion } from 'framer-motion'
import { Link, useOutletContext } from 'react-router-dom'
import {
  Bar,
  BarChart,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { api, errorMessage } from '../api'
import { useSettings } from '../lib/settings'
import { fadeUp, stagger } from '../lib/motion'
import { Emoji } from '../components/Emoji'
import { CountUp, TiltCard } from '../components/Visuals'
import { ModelNotice } from '../components/Badges'
import { CardSkeleton, ErrorBox, EmptyState } from '../components/States'
import type { useApiHealth } from '../components/ApiStatus'
import type { UploadedCandidatesResponse } from '../types/api'

const actions = [
  {
    to: '/app/candidates',
    emoji: '🔍',
    title: 'Browse candidates',
    text: 'Search and open candidate profiles.',
  },
  {
    to: '/app/screening',
    emoji: '📄',
    title: 'Screen a resume',
    text: 'Upload a PDF or DOCX for a prediction.',
  },
  {
    to: '/app/compare',
    emoji: '🏆',
    title: 'Compare candidates',
    text: 'Compare saved candidate profiles.',
  },
  {
    to: '/app/recruiter',
    emoji: '🤖',
    title: 'Ask the AI recruiter',
    text: 'Chat, listen and speak.',
  },
]

type UploadedCandidate = UploadedCandidatesResponse['candidates'][number]

export default function Overview() {
  const { dataMode } = useSettings()
  const health = useOutletContext<ReturnType<typeof useApiHealth>>()

  const [candidates, setCandidates] = useState<UploadedCandidate[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const loadCandidates = async () => {
    setLoading(true)
    setError(null)

    try {
      const response = await api.listUploadedCandidates()
      setCandidates(response.candidates ?? [])
    } catch (e) {
      setError(errorMessage(e))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void loadCandidates()
  }, [])

  const analytics = useMemo(() => {
    const strong = candidates.filter(
      (c) => c.prediction?.prediction?.toLowerCase() === 'strong match',
    ).length

    const weak = candidates.filter(
      (c) => c.prediction?.prediction?.toLowerCase() === 'weak match',
    ).length

    const roleCounts = Object.entries(
      candidates.reduce<Record<string, number>>((counts, candidate) => {
        const role = candidate.job?.job_role?.trim() || 'Unspecified'
        counts[role] = (counts[role] ?? 0) + 1
        return counts
      }, {}),
    ).map(([role, count]) => ({ role, count }))

    return { strong, weak, roleCounts }
  }, [candidates])

  const hasPredictions = analytics.strong + analytics.weak > 0

  return (
    <div className="stack">
      <div className="page-head row spread wrap">
        <div>
          <h1>
            Welcome back <Emoji symbol="👋" anim="wiggle" size={30} />
          </h1>
          <p className="muted">
            Your recruiter workspace. Explanations support, but never replace,
            human judgement.
          </p>
        </div>

        {dataMode === 'demo' && (
          <p className="muted small">
            Demo mode is selected. These analytics use saved uploaded candidates
            only.
          </p>
        )}
      </div>

      <div className="card">
        <div className="card-title">🧠 Backend status</div>
        <p>
          API status:{' '}
          <strong>
            {health.state === 'online'
              ? 'Connected'
              : health.state === 'checking'
                ? 'Checking…'
                : 'Not reachable'}
          </strong>
          {health.model && (
            <>
              {' · '}Reported model: <strong>{health.model}</strong>
            </>
          )}
        </p>
        <p className="muted small">
          API connectivity does not by itself confirm that the prediction model
          is ready.
        </p>
        <ModelNotice />
      </div>

      <div className="row spread wrap">
        <h2>📊 Candidate analytics</h2>
        <button
          type="button"
          className="btn btn-secondary"
          onClick={() => void loadCandidates()}
          disabled={loading}
        >
          {loading ? 'Refreshing…' : 'Refresh data'}
        </button>
      </div>

      {loading ? (
        <div className="grid g-4">
          {[1, 2, 3, 4].map((n) => (
            <div className="card" key={n}>
              <CardSkeleton lines={3} />
            </div>
          ))}
        </div>
      ) : error ? (
        <div className="card">
          <ErrorBox message={error} onRetry={() => void loadCandidates()} />
          <p className="muted small">
            Candidate analytics could not be loaded. No sample numbers are
            substituted for live data.
          </p>
        </div>
      ) : candidates.length === 0 ? (
        <div className="card">
          <EmptyState emoji="📂" title="No saved uploaded candidates yet">
            Upload and screen resumes to create candidate records. Once records
            are saved, their actual data will appear here.
          </EmptyState>
          <Link className="btn btn-primary" to="/app/screening">
            Screen a resume
          </Link>
        </div>
      ) : (
        <>
          <motion.div
            className="grid g-4"
            variants={stagger}
            initial="hidden"
            animate="show"
          >
            {[
              {
                emoji: '👥',
                label: 'Saved uploaded candidates',
                value: candidates.length,
              },
              {
                emoji: '🌟',
                label: 'Strong Match',
                value: analytics.strong,
              },
              {
                emoji: '🧭',
                label: 'Weak Match',
                value: analytics.weak,
              },
              {
                emoji: '📋',
                label: 'Other / unclassified predictions',
                value: candidates.length - analytics.strong - analytics.weak,
              },
            ].map((k) => (
             
                <motion.div
  key={k.label}
  variants={fadeUp}
  whileHover={{ y: -6, scale: 1.015 }}
  transition={{ duration: 0.25, ease: 'easeOut' }}
>
                <TiltCard>
                  <div className="card kpi">
                    <div className="kpi-icon">
                      <Emoji symbol={k.emoji} anim="pulse" size={26} />
                    </div>
                    <div>
                      <div className="kpi-value">
                        <CountUp value={k.value} digits={0} suffix="" />
                      </div>
                      <div className="kpi-label">{k.label}</div>
                    </div>
                  </div>
                </TiltCard>
              </motion.div>
            ))}
          </motion.div>

          <div className="grid g-2">
            <div className="card">
              <div className="card-title">📊 Prediction distribution</div>

              {hasPredictions ? (
                <>
                  <div
                    style={{ height: 240 }}
                    role="img"
                    aria-label="Prediction counts among saved uploaded candidates"
                  >
                    <ResponsiveContainer>
                      <PieChart>
                        <Pie
                          data={[
                            { name: 'Strong Match', value: analytics.strong },
                            { name: 'Weak Match', value: analytics.weak },
                            {
                              name: 'Other / unclassified',
                              value:
                                candidates.length -
                                analytics.strong -
                                analytics.weak,
                            },
                          ].filter((item) => item.value > 0)}
                          dataKey="value"
                          nameKey="name"
                          innerRadius={55}
                          outerRadius={90}
                          paddingAngle={4}
                        >
                          <Cell fill="#4F46E5" />
                          <Cell fill="#F59E0B" />
                          <Cell fill="#94A3B8" />
                        </Pie>
                        <Tooltip />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                  <p className="small muted">
                    Counts are calculated from saved candidate prediction
                    records.
                  </p>
                </>
              ) : (
                <EmptyState title="No classified predictions">
                  Saved candidates exist, but their prediction values do not
                  contain Strong Match or Weak Match labels.
                </EmptyState>
              )}
            </div>

            <div className="card">
              <div className="card-title">🎯 Candidates by job role</div>

              <div
                style={{ height: 240 }}
                role="img"
                aria-label="Saved uploaded candidates grouped by job role"
              >
                <ResponsiveContainer>
                  <BarChart data={analytics.roleCounts} margin={{ left: -10 }}>
                    <XAxis dataKey="role" tick={{ fontSize: 11 }} />
                    <YAxis allowDecimals={false} tick={{ fontSize: 11 }} />
                    <Tooltip />
                    <Bar
                      dataKey="count"
                      name="Candidates"
                      fill="#7C3AED"
                      radius={[8, 8, 0, 0]}
                    />
                  </BarChart>
                </ResponsiveContainer>
              </div>
              <p className="small muted">
                Based on job roles stored with uploaded candidate records.
              </p>
            </div>
          </div>

          <div className="card">
            <div className="card-title">🕒 Recently saved candidates</div>
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Candidate</th>
                    <th>Job role</th>
                    <th>Prediction</th>
                    <th>Saved</th>
                  </tr>
                </thead>
                <tbody>
                  {[...candidates]
                    .sort(
                      (a, b) =>
                        new Date(b.created_at ?? 0).getTime() -
                        new Date(a.created_at ?? 0).getTime(),
                    )
                    .slice(0, 5)
                    .map((candidate) => (
                      <tr key={candidate.candidate_id}>
                        <td>
                          {candidate.candidate?.candidate_name ||
                            candidate.filename ||
                            candidate.candidate_id}
                        </td>
                        <td>{candidate.job?.job_role || 'Unspecified'}</td>
                        <td>
                          {candidate.prediction?.prediction || 'Not available'}
                        </td>
                        <td>
                          {candidate.created_at
                            ? new Date(candidate.created_at).toLocaleDateString()
                            : 'Not recorded'}
                        </td>
                      </tr>
                    ))}
                </tbody>
              </table>
            </div>
            <Link className="btn btn-secondary" to="/app/candidates">
              Browse candidates
            </Link>
          </div>
        </>
      )}

      <h3>🚀 Quick actions</h3>
      <motion.div
        className="grid g-4"
        variants={stagger}
        initial="hidden"
        animate="show"
      >
        {actions.map((action) => (
          <motion.div
  key={action.to}
  variants={fadeUp}
  whileHover={{ y: -10, scale: 1.04 }}
whileTap={{ scale: 0.97 }}
transition={{ type: 'spring', stiffness: 300, damping: 18 }}
>
            <Link
              to={action.to}
              className="card hover"
              style={{
                display: 'block',
                textDecoration: 'none',
                color: 'inherit',
                height: '100%',
              }}
            >
              <Emoji symbol={action.emoji} anim="bounce" size={30} />
              <h3 style={{ margin: '10px 0 4px' }}>{action.title}</h3>
              <p className="muted small">{action.text}</p>
            </Link>
          </motion.div>
        ))}
      </motion.div>
    </div>
  )
}
