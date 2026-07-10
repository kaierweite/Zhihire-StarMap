import request from '@/utils/request'
import type { ApiResponse } from '@/types/api'

/** Company profile returned by GET /api/company/me */
export interface CompanyProfile {
  id: number
  company_name: string
  audit_status: string
  industry: string | null
  scale: string | null
  description: string | null
  contact_name: string | null
  contact_phone: string | null
}

/** Get current user's company profile (requires COMPANY token) */
export function getCompanyProfile() {
  return request.get<ApiResponse<CompanyProfile>>('/company/me')
}
