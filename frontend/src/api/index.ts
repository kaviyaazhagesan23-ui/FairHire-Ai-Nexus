
import { getSettings } from '../lib/settings'
import { liveApi, ApiError } from './client'
import { mockApi, demoCandidates } from './mock'

import type {
  Candidate,
  ComparisonResponse,
  UploadCompareResponse,
} from '../types/api'

export { API_BASE_URL, ApiError } from './client'

const demo = () => getSettings().dataMode === 'demo'

/**
 * Single entry point for pages. Demo mode is explicit (Settings) and always
 * labeled in the UI; live mode never falls back to demo data.
 * Chat, health, explainability and uploads ALWAYS use the real backend.
 */
export const api = {
  health: liveApi.health,
  chat: liveApi.chat,
  shapGlobal: liveApi.shapGlobal,
  shapStructured: liveApi.shapStructured,
  shapCandidate: liveApi.shapCandidate,
  limeCandidate: liveApi.limeCandidate,
  uploadPredict: liveApi.uploadPredict,
  compareUploads: liveApi.compareUploads,
  deleteUploadedCandidate: liveApi.deleteUploadedCandidate,

compareUploadedCandidates: (candidate_ids: string[]) =>
  liveApi.compareUploadedCandidates(candidate_ids),

  // Real uploaded resumes
  listUploadedCandidates: liveApi.listUploadedCandidates,
  getUploadedCandidate: liveApi.getUploadedCandidate,

  getCandidate: (id: string): Promise<Candidate> =>
    demo() ? mockApi.getCandidate(id) : liveApi.getCandidate(id),

  compare: (ids: string[]): Promise<ComparisonResponse> =>
    demo() ? mockApi.compare(ids) : liveApi.compare(ids),

  // Synthetic candidates are available only in demo mode
  listCandidates: (): Candidate[] | null =>
    demo() ? demoCandidates : null,
}

export const errorMessage = (e: unknown): string =>
  e instanceof ApiError ? e.message : 'Something unexpected went wrong.'
