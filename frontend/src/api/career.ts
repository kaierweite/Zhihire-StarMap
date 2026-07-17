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

/** AI suggestion item */
export interface AiSuggestion {
  title: string
  icon?: string
}

/** Strengths and weaknesses analysis */
export interface StrengthWeakness {
  strengths: string[]
  weaknesses: string[]
}

/** Career development stage */
export interface CareerStage {
  stage: string
  title: string
  icon?: string
}

/** Skill gap item with progress */
export interface SkillGapWithProgress {
  skill_name: string
  requirement_level: 'MUST' | 'NICE' | 'BONUS'
  current_level: number
  target_level: number
  description?: string
}

/** Growth curve point */
export interface GrowthCurvePoint {
  label: string
  value: number
}

/** Recommended learning resource */
export interface LearningResource {
  id: number
  title: string
  cover?: string
  rating: number
  duration?: string
  type?: string
}

/** Employment outlook */
export interface EmploymentOutlook {
  salary_range: string
  demand_level: string
  growth_rate: string
  trend?: 'up' | 'down' | 'stable'
}

/** Learning statistics overview */
export interface LearningStats {
  total_hours: number
  completed_courses: number
  planned_courses: number
  certificates: number
  completion_rate: number
  target_completion_rate: number
}

/** AI career plan response from backend */
export interface AiPlanResponse {
  target_role: string
  analysis_summary: string
  match_score: number
  has_resume: boolean
  ai_suggestions: AiSuggestion[]
  strength_weakness: StrengthWeakness
  career_stages: CareerStage[]
  gap_skills: SkillGapWithProgress[]
  growth_curve: GrowthCurvePoint[]
  learning_resources: LearningResource[]
  employment_outlook: EmploymentOutlook
  learning_stats: LearningStats
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
