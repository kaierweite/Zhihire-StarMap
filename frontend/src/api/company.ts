import request from '@/utils/request'
import type { ApiResponse } from '@/types/api'

/** Company profile returned by GET /api/company/me */
export interface CompanyProfile {
  id: number
  company_name: string
  audit_status: string
  industry: string | null
  company_type: string | null
  scale: string | null
  website: string | null
  logo_url: string | null
  description: string | null
  address: string | null
  contact_name: string | null
  contact_phone: string | null
  contact_email: string | null
  audit_reason: string | null
  created_at: string
  updated_at: string
}

/** Dashboard 统计数字 */
export interface DashboardStats {
  total_jobs: number
  active_jobs: number
  total_applications: number
}

/** Dashboard 最近岗位项 */
export interface DashboardJobItem {
  id: number
  title: string
  status: string
  city: string | null
  salary_min: number | null
  salary_max: number | null
  job_type: string
  views: number
  created_at: string
}

/** Dashboard 最近投递项 */
export interface DashboardApplicationItem {
  id: number
  job_id: number
  job_title: string | null
  user_id: number
  applicant_name: string | null
  status: string
  created_at: string
}

/** Dashboard 完整响应 */
export interface CompanyDashboard {
  stats: DashboardStats
  recent_jobs: DashboardJobItem[]
  recent_applications: DashboardApplicationItem[]
}

/** 编辑企业信息请求体 */
export interface CompanyUpdateData {
  company_name?: string
  industry?: string
  company_type?: string
  scale?: string
  website?: string
  logo_url?: string
  description?: string
  address?: string
  contact_name?: string
  contact_phone?: string
  contact_email?: string
}

/** Get current user company profile (COMPANY token required) */
export function getCompanyProfile() {
  return request.get<ApiResponse<CompanyProfile>>('/company/me')
}

/** Update company profile (resets audit_status to PENDING) */
export function updateCompanyProfile(data: CompanyUpdateData) {
  return request.put<ApiResponse<CompanyProfile>>('/company/info', data)
}

/** Get company dashboard stats and recent activities */
export function getCompanyDashboard() {
  return request.get<ApiResponse<CompanyDashboard>>('/company/dashboard')
}

/** Search companies by keyword */
export function searchCompanies(keyword: string) {
  return request.get<ApiResponse<string[]>>('/companies/search', {
    params: { keyword, limit: 10 },
  })
}
