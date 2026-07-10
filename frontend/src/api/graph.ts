import request from '@/utils/request'
import type { ApiResponse } from '@/types/api'
import type { GraphResult, UserGraphResult, OccupationRole } from '@/types/graph'

/** Fetch user's personal ability graph, optionally with gap analysis */
export function getUserGraph(roleId?: number | null) {
  const params: Record<string, number> = {}
  if (roleId != null) params.role_id = roleId
  return request.get<ApiResponse<UserGraphResult>>('/graph/user', { params })
}

/** Fetch job ability graph */
export function getJobGraph(jobId: number) {
  return request.get<ApiResponse<GraphResult>>(`/graph/job/${jobId}`)
}

/** Admin: reload the in-memory graph */
export function reloadGraph() {
  return request.post<ApiResponse<null>>('/graph/reload')
}

/** Fetch active occupation roles for the role selector */
export function listRoles() {
  return request.get<ApiResponse<OccupationRole[]>>('/graph/roles')
}
