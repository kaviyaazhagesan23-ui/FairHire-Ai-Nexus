/**
 * Types mirror the FastAPI backend (backend/app/main.py and services).
 * Candidate records come from candidate_intelligence_v2.json, whose full schema
 * was not in the source bundle, so every field is optional and the UI shows
 * "Not available" instead of guessing.
 */
export interface ExperienceInfo {
  candidate_experience_years?: number | null
  required_experience_years?: number | null
  experience_compatible?: boolean
  [key: string]: unknown
}

export interface Candidate {
  candidate_name: string
  job_role?: string
  prediction?: string
  candidate_skills?: string[]
  required_skills?: string[]
  matched_skills?: string[]
  missing_skills?: string[]
  matched_skill_count?: number
  required_skill_count?: number
  experience?: ExperienceInfo
  role_analysis?: { role_compatible?: boolean; [key: string]: unknown }
  project_analysis?: { project_relevance?: number; [key: string]: unknown }
  model_features?: { semantic_overlap?: number; [key: string]: unknown }
  summary?: string
  [key: string]: unknown
}

export interface ChatResponse {
  answer: string
  candidate_ids: string[]
  intent: string
}

export interface ComparisonMetrics {
  skill_match: number
  experience_fit: number
  semantic_overlap: number
  project_relevance: number
  role_compatibility: number
}

export interface RankedCandidate {
  rank: number
  candidate_name: string
  job_role?: string
  model_prediction: string
  ranking_score: number
  ranking_score_type: string
  metrics: ComparisonMetrics
  skills: {
    candidate_skills: string[]
    required_skills: string[]
    matched_skills: string[]
    missing_skills: string[]
    matched_skill_count: number
    required_skill_count: number
  }
  experience: ExperienceInfo
  role_analysis: Record<string, unknown>
  project_analysis: Record<string, unknown>
  strengths: string[]
  improvement_areas: string[]
}

export interface ComparisonResponse {
  comparison_type: string
  candidate_count: number
  score_explanation: string
  weights: Record<string, number>
  ranked_candidates: RankedCandidate[]
}

export type ExplainRow = Record<string, unknown>

export interface ExplanationEnvelope {
  candidate_id?: string
  explanation_type: string
  scope?: string
  data: ExplainRow[]
}

export interface FeatureContribution {
  feature: string
  shap_value?: number
  lime_weight?: number
  direction: string
}

export interface UploadPredictResponse {
  status: string
  filename: string
  candidate_id: string
  candidate: {
    candidate_name: string
    skills: string[]
    experience_years: number
    previous_role: string
    projects: string[]
  }
  job: { job_role: string; required_skills: string; required_experience: number }
  prediction: { label: string; decision_score: number }
  explanations: {
    available: boolean
    shap: { explanation_type: string; prediction: string; decision_score: number; top_features: FeatureContribution[] }
    lime: { explanation_type: string; top_features: FeatureContribution[] }
  }
}

export interface HealthResponse { status: string; service: string; model: string }

export interface UploadCompareResponse {
  
  status: string
  source: string
  job: {
    job_role: string
    job_description: string
    required_skills: string[]
    required_experience: number
  }
  results: Array<{
    candidate_id: string
    rank: number
    filename: string
    candidate: {
      candidate_name?: string | null
      skills: string[]
      experience_years: number
      previous_role: string
      projects: string[]
    }
    evaluation: {
      prediction: string
      decision_score: number | null
      matched_skills: string[]
      missing_skills: string[]
      matched_skill_count: number
      required_skill_count: number
      experience_requirement_met: boolean
      screening_match_score?: number
    }
  }>
  ranking_method?: string
  score_note?: string
}

export interface SavedUploadedCandidate {
  candidate_id: string
  source: 'recruiter_upload'
  filename: string
  candidate: {
    candidate_name?: string | null
    skills: string[]
    experience_years: number
    previous_role: string
    projects: string[]
  }
  job: {
    job_role: string
    job_description: string
    required_skills: string[]
    required_experience: number
  }
  prediction: {
    prediction: string
    decision_score: number | null
  }
  evaluation: {
    screening_match_score: number | null
  }
  resume_path: string
  created_at: string
}

export interface UploadedCandidatesResponse {
  status: string
  count: number
  candidates: SavedUploadedCandidate[]
}

export interface UploadedCandidateResponse {
  status: string
  candidate: SavedUploadedCandidate
}

