export const idFromName = (name: string): string => (name.match(/(\d+)/)?.[1] ?? name)

export const pct = (v: number | undefined | null, digits = 0): string =>
  typeof v === 'number' && Number.isFinite(v) ? `${(v * 100).toFixed(digits)}%` : 'Not available'

export const num = (v: unknown, digits = 2): string =>
  typeof v === 'number' && Number.isFinite(v) ? v.toFixed(digits) : 'Not available'

export const isStrong = (label?: string): boolean => (label ?? '').toLowerCase().includes('strong')

export const cx = (...parts: Array<string | false | null | undefined>): string => parts.filter(Boolean).join(' ')

export interface BarRow { label: string; value: number }

/** Best-effort conversion of unknown explainability CSV rows into label/value bars. */
export function normalizeRows(rows: Record<string, unknown>[]): BarRow[] | null {
  if (!rows.length) return null
  const sample = rows[0]
  const keys = Object.keys(sample)
  const labelKey = keys.find((k) => typeof sample[k] === 'string' && k !== 'candidate_name' && k !== 'direction')
  const numericKeys = keys.filter((k) => typeof sample[k] === 'number')
  const valueKey =
    numericKeys.find((k) => /shap|lime|weight|importance|value/i.test(k)) ?? numericKeys[0]
  if (!labelKey || !valueKey) return null
  return rows
    .map((r) => ({ label: String(r[labelKey]), value: Number(r[valueKey]) }))
    .filter((r) => Number.isFinite(r.value))
}
