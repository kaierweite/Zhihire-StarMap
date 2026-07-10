import request from '@/utils/request'
import type { ApiResponse, PageData } from '@/types/api'

/* ========== Types ========== */

export type JobStatus = 'OPEN' | 'CLOSED' | 'DRAFT'
export type JobType = 'FULL_TIME' | 'PART_TIME' | 'INTERN'
export type RequiredLevel = 'MUST' | 'NICE' | 'BONUS'

/** Create job request body.
 *  company_id is NOT sent - backend resolves it from the JWT company user.
 */
export interface CreateJobForm {
  title: string
  city?: string | null
  education_requirement?: string | null
  experience_min?: number | null
  salary_min?: number | null
  salary_max?: number | null
  job_type: JobType
  description?: string | null
  occupation_role_id?: number | null
  is_campus?: boolean
  major?: string | null
  job_category?: string | null
  benefits?: string[] | null
}

export interface CreateJobResult {
  id: number
  title: string
}

/** Update job request body - all fields optional, only send changed fields.
 *  To clear a nullable field, pass "" instead of null (null fields are skipped).
 */
export interface UpdateJobForm {
  title?: string
  city?: string | null
  education_requirement?: string | null
  experience_min?: number | null
  salary_min?: number | null
  salary_max?: number | null
  job_type?: JobType
  status?: JobStatus
  description?: string | null
  requirements?: string | null
  source?: string | null
  occupation_role_id?: number | null
  benefits?: string[] | null
}

/** Job item in search/list results.
 *  Compared to JobDetail, this omits description / requirements / source / skills / occupation_role_name.
 */
export interface JobItem {
  id: number
  company_id: number
  company_name: string | null
  industry: string | null
  scale: string | null
  company_type: string | null
  title: string
  city: string | null
  education_requirement: string | null
  experience_min: number | null
  salary_min: number | null
  salary_max: number | null
  job_type: JobType
  status: JobStatus
  views: number
  is_campus: boolean
  major: string | null
  job_category: string | null
  benefits: string[] | null
  occupation_role_id: number | null
  created_at: string
  updated_at: string
}

/** Skill requirement item (appears in JobDetail.skills and GET /job/{id}/skills) */
export interface JobSkillItem {
  id: number
  job_id: number
  skill_id: number
  skill_name: string | null
  skill_category: string | null
  importance: number   // 1-5 scale, default 3.0
  required_level: RequiredLevel  // MUST / NICE / BONUS, default NICE
}

/** Job detail returned by GET /api/job/{id} */
export interface JobDetail {
  id: number
  company_id: number
  company_name: string | null
  occupation_role_id: number | null
  occupation_role_name: string | null
  title: string
  city: string | null
  education_requirement: string | null
  experience_min: number | null
  salary_min: number | null
  salary_max: number | null
  job_type: JobType
  description: string | null
  is_campus: boolean
  requirements: string | null
  source: string            // MANUAL / UPLOAD
  status: JobStatus
  views: number
  benefits: string[] | null
  skills: JobSkillItem[]
  created_at: string
  updated_at: string
}

/** Response from POST /api/job/{id}/skills */
export interface AddSkillResult {
  id: number
  job_id: number
  skill_id: number
  required_level: RequiredLevel
}

/** Request body for POST /api/job/{id}/skills */
export interface AddSkillForm {
  skill_id: number
  /** 1-5 scale, backend defaults to 3.0 */
  importance?: number
  /** MUST / NICE / BONUS, backend defaults to NICE */
  required_level?: RequiredLevel
}

/** Request body for POST /api/job/{id}/apply */
export interface ApplyJobForm {
  resume_id?: number
}

/** Response from POST /api/job/{id}/apply */
export interface ApplyJobResult {
  id: number
  user_id: number
  job_id: number
  status: string
}

export interface JobSearchParams {
  keyword?: string
  city?: string
  education_requirement?: string
  experience_min?: number
  /** Filter job.salary_max >= this value */
  salary_min?: number
  /** Filter job.salary_min <= this value */
  salary_max?: number
  job_type?: JobType
  major?: string
  job_category?: string
  company_id?: number
  /** Omit -> default OPEN (public search); "ALL" -> skip filter (admin panel) */
  status?: JobStatus | 'ALL'
  page?: number
  size?: number
}

/* ========== Job CRUD ========== */

/** Create a job posting (COMPANY only, company must be VERIFIED).
 *  company_id is NOT sent - backend resolves it from JWT. */
export function createJob(data: CreateJobForm) {
  return request.post<ApiResponse<CreateJobResult>>('/job', data)
}

/** Search/list job postings (public, no token required).
 *  Only returns OPEN jobs from VERIFIED companies by default. */
export function listJobs(params?: JobSearchParams) {
  return request.get<ApiResponse<PageData<JobItem>>>('/job', { params })
}

/** Get job detail with nested skills (public, auto-increments views) */
export function getJobDetail(jobId: number, config?: any) {
  return request.get<ApiResponse<JobDetail>>(`/job/${jobId}`, config)
}

/** Update a job posting (COMPANY only, only owned jobs). Returns full JobDetail.
 *  Skips null fields; pass "" to clear a nullable field. */
export function updateJob(jobId: number, data: UpdateJobForm) {
  return request.put<ApiResponse<JobDetail>>(`/job/${jobId}`, data)
}

/** Soft-delete a job posting (COMPANY only) */
export function deleteJob(jobId: number) {
  return request.delete<ApiResponse<null>>(`/job/${jobId}`)
}

/* ========== Apply ========== */

/** Apply (submit resume) to a job (USER only).
 *  resume_id is optional; omit for a simple application without a specific resume. */
export function applyJob(jobId: number, data?: ApplyJobForm) {
  return request.post<ApiResponse<ApplyJobResult>>(`/job/${jobId}/apply`, data || {})
}


/* ========== Job Applications ========== */

/** Application item as returned by GET /api/job/{id}/applications */
export interface JobApplicationItem {
  id: number
  job_id: number
  user_id: number
  applicant_name: string | null
  applicant_email: string | null
  phone: string | null
  resume_id: number | null
  status: string
  created_at: string
  updated_at: string
}

/** Get applications for a specific job (COMPANY only) */
export function getJobApplications(jobId: number, page = 1, size = 20) {
  return request.get<ApiResponse<PageData<JobApplicationItem>>>(`/job/${jobId}/applications`, {
    params: { page, size },
  })
}

/** Request body for PUT /api/job/{job_id}/applications/{application_id}/status */
export interface UpdateApplicationStatusForm {
  status: 'ACCEPTED' | 'REJECTED'
}

/** Update application status (COMPANY only) */
export function updateApplicationStatus(
  jobId: number, applicationId: number, data: UpdateApplicationStatusForm
) {
  return request.put<ApiResponse<null>>(`/job/${jobId}/applications/${applicationId}/status`, data)
}
/* ========== Skill Requirements ========== */

/** Add a skill requirement to a job (COMPANY only).
 *  importance defaults to 3.0 (1-5 scale), required_level defaults to NICE. */
export function addJobSkill(jobId: number, data: AddSkillForm) {
  return request.post<ApiResponse<AddSkillResult>>(`/job/${jobId}/skills`, data)
}

/** Query all skill requirements for a job (public) */
export function listJobSkills(jobId: number) {
  return request.get<ApiResponse<JobSkillItem[]>>(`/job/${jobId}/skills`)
}

/** Remove a skill requirement from a job (COMPANY only, hard delete) */
export function removeJobSkill(jobId: number, skillId: number) {
  return request.delete<ApiResponse<null>>(`/job/${jobId}/skills/${skillId}`)
}

/* ========== JD Parsing ========== */

export interface JdParseResult {
  task_id: number
  status: string
  file_id: number
  title?: string | null
  city?: string | null
  education_requirement?: string | null
  experience_min?: number | null
  salary_min?: number | null
  salary_max?: number | null
  job_type?: string | null
  description?: string | null
  benefits?: string[] | null
  skills: { name: string; skill_id: number; category?: string }[]
  parsed_at?: string | null
}

export interface JdUploadResult {
  file_id: number
  task_id: number
  file_name: string
}

/** Upload JD file for parsing (COMPANY only) */
export function uploadJd(file: File) {
  const formData = new FormData()
  formData.append('file', file)
  return request.post<ApiResponse<JdUploadResult>>('/job/jd/upload', formData, {
    headers: { 'Content-Type': undefined },
  })
}

/** Get JD parse result by task ID (COMPANY only) */
export function getJdParseResult(taskId: number) {
  return request.get<ApiResponse<JdParseResult>>(`/job/jd/parse-result/${taskId}`)
}

export interface BatchAddJobSkillRequest {
  skill_id: number
  importance?: number
  required_level?: string
}

export interface BatchAddJobSkillResult {
  id: number
  job_id: number
  skill_id: number
  required_level: string
}

export function batchAddJobSkills(jobId: number, skills: BatchAddJobSkillRequest[]) {
  return request.post<ApiResponse<BatchAddJobSkillResult[]>>(`/job/${jobId}/skills/batch`, { skills })
}
