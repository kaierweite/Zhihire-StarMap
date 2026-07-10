export type UserRole = 'ADMIN' | 'USER' | 'COMPANY'

export interface LoginForm {
  username: string
  password: string
}

export interface RegisterForm {
  username: string
  password: string
  role: UserRole
  company_name?: string
  email?: string
  phone?: string
}

export interface LoginResult {
  token: string
  role: UserRole
  username: string
}
