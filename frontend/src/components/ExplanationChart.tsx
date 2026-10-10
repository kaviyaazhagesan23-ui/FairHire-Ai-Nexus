import { Bar, BarChart, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { normalizeRows, type BarRow } from '../lib/utils'
import type { ExplainRow } from '../types/api'

export function BarsChart({ rows, height }: { rows: BarRow[]; height?: number }) {
  const top = [...rows].sort((a, b) => Math.abs(b.value) - Math.abs(a.value)).slice(0, 15)
  const h = height ?? Math.max(220, top.length * 28 + 30)
  return (
    <div style={{ width: '100%', height: h }} role="img" aria-label="Feature contribution bar chart. Positive values support Strong Match, negative values support Weak Match.">
      <ResponsiveContainer>
        <BarChart data={top} layout="vertical" margin={{ left: 8, right: 16, top: 4, bottom: 4 }}>
          <XAxis type="number" tick={{ fontSize: 11, fill: '#64748B' }} />
          <YAxis type="category" dataKey="label" width={130} tick={{ fontSize: 11, fill: '#172033' }} interval={0} />
          <Tooltip formatter={(v) => Number(v).toFixed(4)} cursor={{ fill: '#F1F5FF' }} />
          <Bar dataKey="value" radius={[0, 8, 8, 0]} animationDuration={900}>
            {top.map((r, i) => <Cell key={i} fill={r.value >= 0 ? '#4F46E5' : '#F59E0B'} />)}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}

/** Renders explanation rows as a chart when columns are recognisable, otherwise as a raw table (never invents values). */
export function ExplanationView({ rows }: { rows: ExplainRow[] }) {
  const bars = normalizeRows(rows)
  if (bars && bars.length) {
    return (
      <>
        <BarsChart rows={bars} />
        <p className="muted small">
          <span style={{ color: '#4F46E5', fontWeight: 700 }}>■</span> supports Strong Match &nbsp;
          <span style={{ color: '#D97706', fontWeight: 700 }}>■</span> supports Weak Match
        </p>
      </>
    )
  }
  const cols = Object.keys(rows[0] ?? {}).slice(0, 6)
  return (
    <div className="table-wrap">
      <table className="tbl">
        <thead><tr>{cols.map((c) => <th key={c}>{c}</th>)}</tr></thead>
        <tbody>
          {rows.slice(0, 25).map((r, i) => <tr key={i}>{cols.map((c) => <td key={c}>{String(r[c] ?? '')}</td>)}</tr>)}
        </tbody>
      </table>
    </div>
  )
}
