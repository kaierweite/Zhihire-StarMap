export type UserRole = 'ADMIN' | 'USER' | 'COMPANY'

export interface LoginForm {
  username: string
  password: string
}

export interface RegisterForm {
  username: string
  password: string
  role: UserRole
}

export interface LoginResult {
  token: string
  role: UserRole
  username: string
}
