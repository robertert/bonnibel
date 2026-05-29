import { create } from 'zustand'
import type { Notification } from '@/types/domain'

interface NotificationState {
  unreadCount: number
  notifications: Notification[]
  setUnreadCount: (n: number) => void
  incrementUnreadCount: () => void
  decrementUnreadCount: () => void
  prependNotification: (n: Notification) => void
  markOneRead: (id: number) => void
  markAllRead: () => void
}

export const useNotificationStore = create<NotificationState>((set) => ({
  unreadCount: 0,
  notifications: [],

  setUnreadCount: (n) => set({ unreadCount: n }),
  incrementUnreadCount: () => set((s) => ({ unreadCount: s.unreadCount + 1 })),
  decrementUnreadCount: () => set((s) => ({ unreadCount: Math.max(0, s.unreadCount - 1) })),

  prependNotification: (n) =>
    set((state) => ({
      notifications: [n, ...state.notifications],
    })),

  markOneRead: (id) =>
    set((state) => ({
      notifications: state.notifications.map((n) =>
        n.notificationId === id ? { ...n, isRead: true } : n
      ),
    })),

  markAllRead: () =>
    set((state) => ({
      notifications: state.notifications.map((n) => ({ ...n, isRead: true })),
    })),
}))
