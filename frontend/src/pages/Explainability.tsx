
import { useEffect, useState } from 'react'
import { api, errorMessage } from '../api'
import type { ExplainRow } from '../types/api'
import { Emoji } from '../components/Emoji'
import { ExplanationView } from '../components/ExplanationChart'
import { ModelNotice } from '../components/Badges'
import { CardSkeleton, EmptyState, ErrorBox } from '../components/States'

type S = {
  loading: boolean
  rows?: ExplainRow[]
  error?: string
}

function GlobalCard({
  title,
  fetcher,
  caption,
}: {
  title: string
  fetcher: () => Promise<{ data: ExplainRow[] }>
  caption: string
}) {
  const [s, setS] = useState<S>({ loading: true })

  const load = () => {
    setS({ loading: true })

    fetcher()
      .then((r) => {
        setS({ loading: false, rows: r.data })
      })
      .catch((e) => {
        setS({ loading: false, error: errorMessage(e) })
      })
  }

  useEffect(() => {
    load()
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <div className="card">
      <div className="card-title">{title}</div>

      <p className="muted small" style={{ marginBottom: 10 }}>
        {caption}
      </p>

      {s.loading && <CardSkeleton lines={4} />}

      {s.error && <ErrorBox message={s.error} onRetry={load} />}

      {s.rows &&
        (s.rows.length > 0 ? (
          <ExplanationView rows={s.rows} />
        ) : (
          <EmptyState title="No rows returned" />
        ))}
    </div>
  )
}

export default function Explainability() {
  return (
    <div className="stack">
      <div className="page-head">
        <h1>
          Explainability{' '}
          <Emoji symbol="💡" anim="sparkle" size={26} />
        </h1>

        <p className="muted">
          Explore global SHAP feature importance and structured-feature
          explanations returned by the backend.
        </p>
      </div>

      <ModelNotice />

      <div className="grid g-2">
        <GlobalCard
          title="🧠 Global SHAP importance"
          fetcher={api.shapGlobal}
          caption="Features that influence the model most across the dataset."
        />

        <GlobalCard
          title="📊 Structured-feature SHAP"
          fetcher={api.shapStructured}
          caption="Importance of the structured (non-text) features."
        />
      </div>
    </div>
  )
}
