import request from '@/utils/request'
import type { ApiResponse, PageData } from '@/types/api'

/* ========== Types ========== */

export type JobType = 'FULL_TIME' | 'PART_TIME' | 'INTERN'

export type RequiredLevel = 'MUST' | 'NICE' | 'BONUS'

/** Create job request body (COMPANY only) */
export interface CreateJobForm {
  title: string
  city: string
  education_requirement: string
  experience_min: number
  salary_min: number
  salary_max: number
  job_type: JobType
  description: string
  company_id: number
  occupation_role_id?: number | null
  benefits?: string[] | null
}

/** Update job request body - all fields optional, only send changed fields */
export interface UpdateJobForm {
  title?: string
  city?: string
  education_requirement?: string
  experience_min?: number
  salary_min?: number
  salary_max?: number
  job_type?: JobType
  description?: string
  occupation_role_id?: number | null
  benefits?: string[] | null
}

/** Job item returned in search/list results */
export interface JobListItem {
  id: number
  company_id: number
  company_name: string
  title: string
  city: string
  education_requirement: string
  experience_min: number
  salary_min: number
  salary_max: number
  job_type: JobType
  status: string
  views: number
  benefits: string[] | null
  occupation_role_id: number | null
  created_at: string | null
  updated_at: string | null
}

/** Skill requirement item for a job */
export interface JobSkillItem {
  id: number
  job_id: number
  skill_id: number
  skill_name: string
  skill_category: string
  importance: number
  required_level: RequiredLevel
}

/** Job detail response (includes nested skills) */
export interface JobDetail {
  id: number
  company_name: string
  title: string
  description: string
  views: number
  benefits: string[] | null
  skills: JobSkillItem[]
}

/** Add skill requirement request body */
export interface AddSkillForm {
  skill_id: number
  importance: number
  required_level: RequiredLevel
}

/** Search/query parameters for listing jobs */
export interface JobSearchParams {
  keyword?: string
  city?: string
  education_requirement?: string
  experience_min?: number
  salary_min?: number
  salary_max?: number
  job_type?: JobType
  company_id?: number
  status?: string
  page?: number
  size?: number
}

/* ========== Job CRUD ========== */

/** Create a job posting (requires COMPANY role, company must be VERIFIED) */
export function createJob(data: CreateJobForm) {
  return request.post<ApiResponse<{ id: number; title: string }>>('/job', data)
}

/** Search/list job postings (public, no token required) */
export function listJobs(params?: JobSearchParams) {
  return request.get<ApiResponse<PageData<JobListItem>>>('/job', { params })
}

/** Get job detail with nested skills (public, auto-increments views) */
export function getJobDetail(jobId: number) {
  return request.get<ApiResponse<JobDetail>>(`/job/${jobId}`)
}

/** Update a job posting (COMPANY only, only owned jobs) */
export function updateJob(jobId: number, data: UpdateJobForm) {
  return request.put<ApiResponse<null>>(`/job/${jobId}`, data)
}

/** Soft-delete a job posting (COMPANY only) */
export function deleteJob(jobId: number) {
  return request.delete<ApiResponse<null>>(`/job/${jobId}`)
}

/* ========== Skill Requirements ========== */

/** Add a skill requirement to a job (COMPANY only) */
export function addJobSkill(jobId: number, data: AddSkillForm) {
  return request.post<ApiResponse<null>>(`/job/${jobId}/skills`, data)
}

/** Query all skill requirements for a job (public) */
export function listJobSkills(jobId: number) {
  return request.get<ApiResponse<JobSkillItem[]>>(`/job/${jobId}/skills`)
}

/** Remove a skill requirement from a job (COMPANY only, hard delete) */
export function removeJobSkill(jobId: number, skillId: number) {
  return request.delete<ApiResponse<null>>(`/job/${jobId}/skills/${skillId}`)
}
