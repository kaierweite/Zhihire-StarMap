import request from '@/utils/request'
import type { ApiResponse } from '@/types/api'
import type { GapSkill } from '@/types/graph'

/** Learning path step — a group of skills at one depth in the topological order */
export interface LearningPathStep {
  skills: string[]
}

/** Career plan data matching backend API response */
export interface CareerPlanData {
  target_role: string
  gap_skills: GapSkill[]
  learning_path: LearningPathStep[]
  graph_hints: string[]
  rationale: string
  score: number
  source: 'PROACTIVE' | 'INTERVIEW' | 'RECOMMEND'
  id?: number
  target_role_id?: number
  created_at?: string
  updated_at?: string
}

/** AI career plan request */
export interface AiPlanGenerateRequest {
  input_type: 'PROFESSION' | 'JOB_DESCRIPTION' | 'JOB_URL'
  target_text: string
}

/** Mind map node for tree visualization */
export interface MindMapNode {
  name: string
  children?: MindMapNode[]
}

/** AI career plan response from backend */
export interface AiPlanResponse {
  target_role: string
  analysis_summary: string
  match_score: number
  has_resume: boolean
  gap_skills: Array<{
    skill_name: string
    requirement_level: 'MUST' | 'NICE' | 'BONUS'
    description?: string
  }>
  mind_map: MindMapNode | null
}

/** Generate a career plan for the given target role */
export function generateCareerPlan(target_role_id: number) {
  return request.post<ApiResponse<CareerPlanData>>('/career/plan/generate', { target_role_id })
}

/** Get existing career plan (returns null if none) */
export function getCareerPlan() {
  return request.get<ApiResponse<CareerPlanData | null>>('/career/plan')
}

/** AI generate career plan from profession name or JD */
export function aiGenerateCareerPlan(data: AiPlanGenerateRequest) {
  return request.post<ApiResponse<AiPlanResponse>>('/career/plan/ai-generate', data)
}
