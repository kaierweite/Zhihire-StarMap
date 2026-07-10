import request from '@/utils/request'
import type { ApiResponse, PageData } from '@/types/api'
import type {
  AdminStat, UserAdminItem, CompanyAuditItem,
  LogItem, SkillAuditItem, JobAdminItem,
} from '@/types/admin'

// ---- Statistics ----
export function getAdminStat() {
  return request.get<ApiResponse<AdminStat>>('/admin/stat')
}

// ---- User Management ----
export function listUsers(keyword?: string, role?: string, page = 1, size = 20) {
  return request.get<ApiResponse<PageData<UserAdminItem>>>('/admin/user', {
    params: { keyword, role, page, size },
  })
}

export function updateUserStatus(userId: number, status: 'BANNED' | 'NORMAL') {
  return request.put<ApiResponse<UserAdminItem>>(`/admin/user/${userId}/status`, { status })
}

// ---- Company Audit ----
export function listCompanyAudit(page = 1, size = 20) {
  return request.get<ApiResponse<PageData<CompanyAuditItem>>>('/admin/company/audit', {
    params: { page, size },
  })
}

export function auditCompany(companyId: number, action: 'pass' | 'reject', reason?: string) {
  return request.put<ApiResponse<CompanyAuditItem>>(`/admin/company/${companyId}/audit`, { action, reason })
}

// ---- Operation Logs ----
export function listOperationLogs(logType?: string, keyword?: string, page = 1, size = 20) {
  return request.get<ApiResponse<PageData<LogItem>>>('/admin/log', {
    params: { log_type: logType, keyword, page, size },
  })
}

// ---- Job Management ----
export function updateJobStatus(jobId: number, status: 'CLOSED' | 'OPEN') {
  return request.put<ApiResponse<JobAdminItem>>(`/admin/job/${jobId}/status`, { status })
}

// ---- Skill Audit ----
export function listSkillAudit(page = 1, size = 20) {
  return request.get<ApiResponse<PageData<SkillAuditItem>>>('/admin/skill/audit', {
    params: { page, size },
  })
}

export function auditSkill(skillId: number, action: 'approve' | 'reject', targetId?: number) {
  return request.put<ApiResponse<SkillAuditItem>>(`/admin/skill/${skillId}/audit`, { action, target_id: targetId })
}
