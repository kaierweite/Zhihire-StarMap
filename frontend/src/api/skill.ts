import request from '@/utils/request'
import type { ApiResponse } from '@/types/api'

/** Skill item returned by GET /api/skills */
export interface SkillItem {
  id: number
  name: string
  category: string | null
}

/** Search skills by keyword (public, no token required) */
export function searchSkills(search?: string, limit?: number) {
  return request.get<ApiResponse<SkillItem[]>>('/skills', {
    params: { search: search || '', limit: limit || 20 },
  })
}
