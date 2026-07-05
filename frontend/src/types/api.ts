/** Backend unified response wrapper */
export interface ApiResponse<T = unknown> {
  code: number
  message: string
  data: T
}

/** Paginated data envelope (matches backend pagination contract) */
export interface PageData<T = unknown> {
  records: T[]
  total: number
  page: number
  size: number
}

export interface PageQuery {
  page: number
  size: number
}
