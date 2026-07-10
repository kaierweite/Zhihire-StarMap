import request from '@/utils/request'
import type { ApiResponse, PageData } from '@/types/api'
import type { NotificationItem } from '@/types/notification'

export function listNotifications(page = 1, size = 20) {
  return request.get<ApiResponse<PageData<NotificationItem>>>('/notification/list', {
    params: { page, size },
  })
}

export function getUnreadCount() {
  return request.get<ApiResponse<{ count: number }>>('/notification/unread-count')
}

export function markRead(id: number) {
  return request.put<ApiResponse<null>>(`/notification/${id}/read`)
}

export function markAllRead() {
  return request.put<ApiResponse<null>>('/notification/read-all')
}
