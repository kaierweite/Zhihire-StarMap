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


// ---- AI Provider Config ----
import type { AiProviderItem, AiProviderCreateRequest, AiProviderUpdateRequest, AiProviderTestResult } from '@/types/admin'

export function listAiProviders() {
  return request.get<ApiResponse<AiProviderItem[]>>('/admin/ai-config')
}

export function createAiProvider(data: AiProviderCreateRequest) {
  return request.post<ApiResponse<AiProviderItem>>('/admin/ai-config', data)
}

export function updateAiProvider(id: number, data: AiProviderUpdateRequest) {
  return request.put<ApiResponse<AiProviderItem>>('/admin/ai-config/' + id, data)
}

export function testAiProvider(id: number) {
  return request.post<ApiResponse<AiProviderTestResult>>('/admin/ai-config/' + id + '/test')
}

export function deleteAiProvider(id: number) {
  return request.delete<ApiResponse<null>>('/admin/ai-config/' + id)
}
