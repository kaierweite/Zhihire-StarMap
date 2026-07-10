import request from '@/utils/request'
import type { ApiResponse, PageData } from '@/types/api'

/* ========== Types ========== */

export interface ResumeUploadResult {
  resume_id: number
  file_id: number
  task_id: number
  title: string
}

export interface ResumeListItem {
  id: number
  title: string | null
  status: string
  created_at: string | null
  updated_at: string | null
  file_name: string | null
}

export interface ResumeDetail {
  id: number
  user_id: number
  file_id: number | null
  title: string | null
  content_text: string | null
  /** Deserialized JSON object from content_text */
  parsed: Record<string, any> | null
  status: string
  created_at: string | null
  updated_at: string | null
}

export interface TaskStatus {
  task_id: number
  status: 'WAITING' | 'PARSING' | 'SUCCESS' | 'FAILED'
  result: Record<string, any> | null
}

export interface SyncProfileResult {
  auto_synced: boolean
  synced_to_profile: boolean
  synced_fields: string[]
  reason?: string
}

export interface OptimizeSuggestion {
  section: string
  current: string
  suggestion: string
  relates_to_skill: string | null
}

export interface OptimizeResult {
  resume_id: number
  suggestions: OptimizeSuggestion[]
}

/* ========== Resume CRUD ========== */

/** Upload a resume file (PDF/DOC/DOCX), returns resume_id + task_id for polling */
export function uploadResume(file: File, title?: string) {
  const fd = new FormData()
  fd.append('file', file)
  if (title) fd.append('title', title)
  return request.post<ApiResponse<ResumeUploadResult>>('/resume/upload', fd, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 30000,
  })
}

/** Paginated resume list (only basic metadata, no parsed content) */
export function listResumes(page = 1, size = 20) {
  return request.get<ApiResponse<PageData<ResumeListItem>>>('/resume', {
    params: { page, size },
  })
}

/** Full resume detail including parsed content */
export function getResumeDetail(resumeId: number) {
  return request.get<ApiResponse<ResumeDetail>>(`/resume/${resumeId}`)
}

/** Update resume title and/or content_text (full JSON string) */
export function updateResume(resumeId: number, data: { title?: string | null; content_text?: string | null }) {
  return request.put<ApiResponse<ResumeDetail>>(`/resume/${resumeId}`, data)
}

/** Delete a resume */
export function deleteResume(resumeId: number) {
  return request.delete<ApiResponse<null>>(`/resume/${resumeId}`)
}

/* ========== Parse Task ========== */

/** Poll parse task status (poll every 2s until SUCCESS or FAILED) */
export function getParseTaskStatus(taskId: number) {
  return request.get<ApiResponse<TaskStatus>>(`/parse/task/${taskId}`)
}

/* ========== AI Optimize ========== */

/** AI-powered resume optimization (calls DeepSeek, may be slow) */
export function optimizeResume(resumeId: number, jobDescription?: string | null) {
  return request.post<ApiResponse<OptimizeResult>>('/resume/optimize', {
    resume_id: resumeId,
    job_description: jobDescription ?? null,
  })
}

/** Sync parsed resume data to user profile (one-click sync to profile) */
export function syncToProfile(resumeId: number) {
  return request.post<ApiResponse<SyncProfileResult>>(`/resume/${resumeId}/sync-profile`)
}
