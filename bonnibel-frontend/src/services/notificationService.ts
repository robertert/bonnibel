import { apiFetch } from '@/lib/api'
import { API_BASE_URL, BYPASS_AUTH, BYPASS_USER_ID } from '@/lib/env'
import type { Notification } from '@/types/domain'

// Notification endpoints are always on the FastAPI backend (no json-server equivalent).
// In bypass mode apiFetch skips the Bearer token, so we inject X-User-Id manually.
function notifFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const extra: Record<string, string> = BYPASS_AUTH ? { 'X-User-Id': BYPASS_USER_ID } : {}
  return apiFetch<T>(path, {
    ...init,
    headers: { ...extra, ...(init?.headers as Record<string, string> ?? {}) },
  })
}

export interface NotificationsParams {
  unread?: boolean
  limit?: number
  offset?: number
}

export const notificationService = {
  getNotifications: (params?: NotificationsParams): Promise<Notification[]> => {
    const qs = new URLSearchParams()
    if (params?.unread) qs.set('unread', 'true')
    if (params?.limit !== undefined) qs.set('limit', String(params.limit))
    if (params?.offset !== undefined) qs.set('offset', String(params.offset))
    const query = qs.toString() ? `?${qs}` : ''
    return notifFetch<Notification[]>(`/notifications${query}`)
  },

  getUnreadCount: (): Promise<{ unreadCount: number }> =>
    notifFetch<{ unreadCount: number }>('/notifications/unread-count'),

  markRead: (notificationId: number): Promise<Notification> =>
    notifFetch<Notification>(`/notifications/${notificationId}/read`, { method: 'PATCH' }),

  markAllRead: (): Promise<{ updated: number }> =>
    notifFetch<{ updated: number }>('/notifications/read-all', { method: 'PATCH' }),
}

interface NotificationSocketHandlers {
  onNotification: (n: Notification) => void
}

export function openNotificationSocket(
  userId: string,
  handlers: NotificationSocketHandlers,
  token?: string | null
): WebSocket {
  const wsBase = API_BASE_URL.replace(/^http/, 'ws')
  const url = new URL(`${wsBase}/ws/notifications`)
  if (token) {
    url.searchParams.set('token', token)
  } else {
    url.searchParams.set('userId', userId)
  }

  const ws = new WebSocket(url.toString())

  ws.onmessage = (event) => {
    try {
      const parsed = JSON.parse(event.data) as { event: string; data: unknown }
      if (parsed.event === 'notification_created') {
        handlers.onNotification(parsed.data as Notification)
      }
    } catch {
      // ignore malformed frames
    }
  }

  return ws
}
