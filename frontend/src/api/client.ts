import type {
 Candidate, ChatResponse, ComparisonResponse, ExplanationEnvelope,
HealthResponse, UploadPredictResponse, UploadCompareResponse,UploadedCandidatesResponse,
  UploadedCandidateResponse,
} from '../types/api'

export const API_BASE_URL: string =
  (import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8001').replace(/\/$/, '')

export type ApiErrorKind = 'network' | 'timeout' | 'client' | 'server' | 'not_found'

export class ApiError extends Error {
  kind: ApiErrorKind
  status?: number
  constructor(kind: ApiErrorKind, message: string, status?: number) {
    super(message)
    this.kind = kind
    this.status = status
  }
}

/** FastAPI returns {detail: string} or {detail: [{msg}...]} for validation errors. */
function readDetail(body: unknown): string | null {
  if (body && typeof body === 'object' && 'detail' in body) {
    const d = (body as { detail: unknown }).detail
    if (typeof d === 'string') return d
    if (Array.isArray(d)) return d.map((x) => (x && typeof x === 'object' && 'msg' in x ? String((x as { msg: unknown }).msg) : '')).filter(Boolean).join('; ')
  }
  return null
}

async function request<T>(path: string, init: RequestInit = {}, timeoutMs = 20000): Promise<T> {
  const controller = new AbortController()
  const timer = setTimeout(() => controller.abort(), timeoutMs)
  let res: Response
  try {
    res = await fetch(`${API_BASE_URL}${path}`, { ...init, signal: controller.signal })
  } catch (e) {
    if ((e as Error).name === 'AbortError') throw new ApiError('timeout', 'The backend took too long to respond.')
    throw new ApiError('network', `Cannot reach the FairHire API at ${API_BASE_URL}. Is the backend running?`)
  } finally {
    clearTimeout(timer)
  }

  let body: unknown = null
  try { body = await res.json() } catch { /* non-JSON body */ }

  if (!res.ok) {
    const detail = readDetail(body)
    if (res.status === 404) throw new ApiError('not_found', detail ?? 'Not found.', 404)
    // 4xx details are user-facing validation messages. 5xx details can contain
    // internal error text, so show a generic message instead.
    if (res.status >= 400 && res.status < 500) throw new ApiError('client', detail ?? 'The request was rejected.', res.status)
    throw new ApiError('server', 'The server could not process this request. Check the backend terminal for details.', res.status)
  }
  return body as T
}

const json = (data: unknown): RequestInit => ({
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(data),
})

export const liveApi = {
  health: () => request<HealthResponse>('/api/health', {}, 6000),
 chat: (message: string, candidateId?: string) =>
  request<ChatResponse>(
    '/api/chat',
    json({
      message,
      ...(candidateId ? { candidate_id: candidateId } : {}),
    }),
    30000
  ),
  getCandidate: (id: string) => request<Candidate>(`/api/candidate/${encodeURIComponent(id)}`),
  
compare: (candidate_ids: string[]) =>
  request<ComparisonResponse>(
    '/api/compare',
    json({ candidate_ids })
  ),

compareUploadedCandidates: (candidate_ids: string[]) =>
  request<UploadedCandidatesResponse>(
    '/api/compare/uploaded',
    json({ candidate_ids })
  ),

  shapGlobal: () => request<ExplanationEnvelope>('/api/explain/shap/global'),
  shapStructured: () => request<ExplanationEnvelope>('/api/explain/shap/structured'),
  shapCandidate: (id: string) => request<ExplanationEnvelope>(`/api/explain/shap/${encodeURIComponent(id)}`),
  limeCandidate: (id: string) => request<ExplanationEnvelope>(`/api/explain/lime/${encodeURIComponent(id)}`),
  uploadPredict: (form: FormData) => request<UploadPredictResponse>('/api/upload/predict', { method: 'POST', body: form }, 120000),
  
  
    
listUploadedCandidates: () =>
  request<UploadedCandidatesResponse>('/api/uploaded-candidates'),

getUploadedCandidate: (id: string) =>
  request<UploadedCandidateResponse>(
    `/api/uploaded-candidates/${encodeURIComponent(id)}`
  ),
  deleteUploadedCandidate: (id: string) =>
  request<{ status: string; message: string; candidate_id: string }>(
    `/api/uploaded-candidates/${encodeURIComponent(id)}`,
    { method: 'DELETE' },
  ),


    compareUploads: (form: FormData) =>
    request<UploadCompareResponse>(
      '/api/compare/uploads',
      { method: 'POST', body: form },
      120000
    ),
} 
  