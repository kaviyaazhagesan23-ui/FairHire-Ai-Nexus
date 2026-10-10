/**
 * DEMO DATA ONLY. These records are invented for UI development and are shown
 * with a "Demo data" badge. They are NOT FairHire model output, and the
 * comparison below re-implements the backend's heuristic formula for preview.
 */
import type { Candidate, ComparisonResponse, RankedCandidate } from '../types/api'
import { ApiError } from './client'

type Row = [id: string, role: string, pred: string, skills: string[], req: string[], exp: number, reqExp: number, roleOk: boolean, proj: number, overlap: number, summary: string]

const DEVOPS = ['Docker', 'Kubernetes', 'AWS', 'CI/CD', 'Linux', 'Terraform', 'Python']
const DATA = ['Python', 'SQL', 'Pandas', 'Machine Learning', 'Statistics', 'Tableau']
const WEB = ['JavaScript', 'React', 'TypeScript', 'Node.js', 'SQL', 'Git']

const rows: Row[] = [
  ['101', 'DevOps Engineer', 'Strong Match', [...DEVOPS, 'Ansible'], DEVOPS, 6, 4, true, 0.72, 0.41, 'Demo record: platform engineer with broad infrastructure coverage.'],
  ['102', 'DevOps Engineer', 'Weak Match', ['Docker', 'Linux', 'Python'], DEVOPS, 2, 4, false, 0.18, 0.12, 'Demo record: early-career profile with partial tooling coverage.'],
  ['103', 'DevOps Engineer', 'Strong Match', ['Docker', 'Kubernetes', 'AWS', 'CI/CD', 'Linux', 'Python'], DEVOPS, 5, 4, true, 0.55, 0.33, 'Demo record: strong container and cloud background.'],
  ['104', 'Data Scientist', 'Strong Match', [...DATA, 'PyTorch'], DATA, 4, 3, true, 0.68, 0.46, 'Demo record: modeling-focused with dashboard experience.'],
  ['105', 'Data Scientist', 'Weak Match', ['Python', 'SQL'], DATA, 1, 3, false, 0.1, 0.09, 'Demo record: limited modeling exposure so far.'],
  ['106', 'Data Scientist', 'Strong Match', ['Python', 'SQL', 'Pandas', 'Statistics', 'Machine Learning'], DATA, 3, 3, true, 0.49, 0.37, 'Demo record: solid analytics fundamentals.'],
  ['107', 'Frontend Developer', 'Strong Match', [...WEB, 'Jest'], WEB, 4, 3, true, 0.61, 0.39, 'Demo record: component-library and testing experience.'],
  ['108', 'Frontend Developer', 'Weak Match', ['JavaScript', 'Git'], WEB, 1, 3, false, 0.14, 0.1, 'Demo record: knows basics, limited framework experience.'],
  ['109', 'Frontend Developer', 'Strong Match', ['JavaScript', 'React', 'TypeScript', 'Git', 'SQL'], WEB, 3, 3, true, 0.44, 0.31, 'Demo record: close to the stated requirements.'],
  ['110', 'DevOps Engineer', 'Weak Match', ['AWS', 'Linux'], DEVOPS, 3, 4, true, 0.22, 0.15, 'Demo record: cloud familiarity, gaps in orchestration.'],
  ['111', 'Data Scientist', 'Weak Match', ['Python', 'Pandas', 'Tableau'], DATA, 2, 3, true, 0.28, 0.2, 'Demo record: BI-oriented background.'],
  ['112', 'Frontend Developer', 'Strong Match', [...WEB], WEB, 5, 3, true, 0.7, 0.43, 'Demo record: complete coverage of listed skills.'],
]

export const demoCandidates: Candidate[] = rows.map(([id, role, pred, skills, req, exp, reqExp, roleOk, proj, overlap, summary]) => {
  const lower = new Set(skills.map((s) => s.toLowerCase()))
  const matched = req.filter((s) => lower.has(s.toLowerCase()))
  const missing = req.filter((s) => !lower.has(s.toLowerCase()))
  return {
    candidate_name: `Candidate ${id}`,
    job_role: role,
    prediction: pred,
    candidate_skills: skills,
    required_skills: req,
    matched_skills: matched,
    missing_skills: missing,
    matched_skill_count: matched.length,
    required_skill_count: req.length,
    experience: { candidate_experience_years: exp, required_experience_years: reqExp, experience_compatible: exp >= reqExp },
    role_analysis: { role_compatible: roleOk },
    project_analysis: { project_relevance: proj },
    model_features: { semantic_overlap: overlap },
    summary,
  }
})

const WEIGHTS = { skill_match: 0.4, experience_fit: 0.2, semantic_overlap: 0.15, project_relevance: 0.15, role_compatibility: 0.1 }

function record(c: Candidate): Omit<RankedCandidate, 'rank'> {
  const req = c.required_skill_count ?? 0
  const matched = c.matched_skill_count ?? 0
  const m = {
    skill_match: req > 0 ? Math.min(1, matched / req) : 1,
    experience_fit: c.experience?.experience_compatible ? 1 : 0,
    semantic_overlap: c.model_features?.semantic_overlap ?? 0,
    project_relevance: c.project_analysis?.project_relevance ?? 0,
    role_compatibility: c.role_analysis?.role_compatible ? 1 : 0,
  }
  const score = Math.round(Object.entries(WEIGHTS).reduce((s, [k, w]) => s + m[k as keyof typeof m] * w, 0) * 10000) / 100
  const strengths: string[] = []
  const improve: string[] = []
  if (m.skill_match >= 0.75) strengths.push('Strong required-skill coverage'); else if (m.skill_match < 0.5) improve.push('Review required-skill gaps')
  if (m.experience_fit) strengths.push('Meets or exceeds the experience requirement'); else improve.push('Review experience compatibility')
  if (m.semantic_overlap >= 0.3) strengths.push('Good resume and job-description text overlap'); else improve.push('Improve job-specific resume alignment')
  if (m.project_relevance >= 0.5) strengths.push('Highly relevant project experience'); else if (m.project_relevance < 0.2) improve.push('Highlight role-relevant projects')
  if (m.role_compatibility) strengths.push('Previous role is compatible with the target role'); else improve.push('Review previous-role relevance')
  return {
    candidate_name: c.candidate_name,
    job_role: c.job_role,
    model_prediction: c.prediction ?? 'Not available',
    ranking_score: score,
    ranking_score_type: 'Heuristic score, not model probability',
    metrics: m,
    skills: {
      candidate_skills: c.candidate_skills ?? [], required_skills: c.required_skills ?? [],
      matched_skills: c.matched_skills ?? [], missing_skills: c.missing_skills ?? [],
      matched_skill_count: matched, required_skill_count: req,
    },
    experience: c.experience ?? {}, role_analysis: c.role_analysis ?? {}, project_analysis: c.project_analysis ?? {},
    strengths, improvement_areas: improve,
  }
}

export const mockApi = {
  async getCandidate(id: string): Promise<Candidate> {
    const found = demoCandidates.find((c) => c.candidate_name === `Candidate ${id}`)
    if (!found) throw new ApiError('not_found', `Demo candidate ${id} not found (demo IDs are 101–112).`, 404)
    return found
  },
  async compare(ids: string[]): Promise<ComparisonResponse> {
    if (ids.length < 2) throw new ApiError('client', 'At least 2 candidates are required for comparison.', 400)
    if (new Set(ids).size !== ids.length) throw new ApiError('client', 'Duplicate candidate IDs are not allowed.', 400)
    const list = await Promise.all(ids.map((i) => mockApi.getCandidate(i)))
    const ranked = list.map(record).sort((a, b) => b.ranking_score - a.ranking_score).map((r, i) => ({ ...r, rank: i + 1 }))
    return {
      comparison_type: 'Candidate Comparison and Ranking (DEMO DATA)',
      candidate_count: ranked.length,
      score_explanation:
        'Scores use weighted skill match (40%), experience fit (20%), semantic overlap (15%), project relevance (15%), and role compatibility (10%). Scores are heuristic comparisons, not SVM probabilities or hiring recommendations.',
      weights: WEIGHTS,
      ranked_candidates: ranked,
    }
  },
}
