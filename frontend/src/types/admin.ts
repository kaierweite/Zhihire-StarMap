export interface AdminStat {
  user_count: number
  company_count: number
  job_count: number
  match_count: number
  parse_count: number
  application_count: number
}

export interface UserAdminItem {
  id: number
  username: string
  email: string | null
  phone: string | null
  role: string          // USER / COMPANY / ADMIN
  status: string        // NORMAL / BANNED / DISABLED
  avatar_url: string | null
  created_at: string | null
  updated_at: string | null
}

export interface CompanyAuditItem {
  id: number
  company_name: string
  industry: string | null
  scale: string | null
  website: string | null
  description: string | null
  address: string | null
  contact_name: string | null
  contact_phone: string | null
  contact_email: string | null
  audit_status: string   // PENDING / VERIFIED / REJECTED
  audit_reason: string | null
  created_at: string | null
}

export interface LogItem {
  id: number
  user_id: number
  module: string | null
  action: string | null
  detail: Record<string, unknown> | null
  ip: string | null
  created_at: string | null
}

export interface SkillAuditItem {
  id: number
  name: string
  category: string | null
  status: string         // CANDIDATE / ACTIVE / MERGED
  created_at: string | null
}

export interface JobAdminItem {
  id: number
  title: string
  company_id: number
  company_name: string | null
  city: string | null
  status: string         // OPEN / CLOSED
  views: number
  created_at: string | null
  updated_at: string | null
}
