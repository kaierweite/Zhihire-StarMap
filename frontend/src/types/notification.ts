import type { ApiResponse, PageData } from '@/types/api'

export interface NotificationItem {
  id: number
  user_id: number
  title: string
  content: string | null
  type: 'APPLICATION' | 'INTERVIEW_INVITE' | 'SYSTEM'
  is_read: boolean
  created_at: string
}

/** Notification type display mapping */
export const NOTIFICATION_TYPE_LABELS: Record<NotificationItem['type'], string> = {
  APPLICATION: '投递状态',
  INTERVIEW_INVITE: '面试邀请',
  SYSTEM: '系统通知',
}
