import request from '@/utils/request'
import type { ApiResponse } from '@/types/api'
import type { LoginForm, RegisterForm, LoginResult } from '@/types/auth'

export function login(data: LoginForm) {
  return request.post<ApiResponse<LoginResult>>('/auth/login', data)
}

export function register(data: RegisterForm) {
  return request.post<ApiResponse<null>>('/auth/register', data)
}

export function ping() {
  return request.get<ApiResponse<string>>('/ping')
}
