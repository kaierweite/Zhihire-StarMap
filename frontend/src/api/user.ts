import request from '@/utils/request'
import type { ApiResponse } from '@/types/api'

export interface SkillItem {
  skill_id: number
  name: string
  category: string | null
  proficiency_level: number
}

export interface UserProfileData {
  id: number
  username: string
  avatar_url: string | null
  real_name: string | null
  gender: string | null
  birth_date: string | null
  phone: string | null
  email: string | null
  education: string | null
  school: string | null
  major: string | null
  work_years: number | null
  current_city: string | null
  expected_city: string | null
  expected_salary_min: number | null
  expected_salary_max: number | null
  bio: string | null
  profile_completeness: number
  skills: SkillItem[]
  created_at: string | null
}

export interface UserProfileUpdateForm {
  real_name?: string | null
  gender?: string | null
  birth_date?: string | null
  phone?: string | null
  email?: string | null
  education?: string | null
  school?: string | null
  major?: string | null
  work_years?: number | null
  current_city?: string | null
  expected_city?: string | null
  expected_salary_min?: number | null
  expected_salary_max?: number | null
  bio?: string | null
  skills?: string[] | null
}

export function getProfile() {
  return request.get<ApiResponse<UserProfileData>>('/user/profile')
}

export function updateProfile(data: UserProfileUpdateForm) {
  return request.put<ApiResponse<UserProfileData>>('/user/profile', data)
}
