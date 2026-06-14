import { useEffect, useMemo, useState } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { notificationService, openNotificationSocket } from '@/services/notificationService'
import { useNotificationStore } from '@/store/notificationStore'
import { useAuthStore } from '@/modules/auth/store/authStore'
import type { Notification, NotificationType } from '@/types/domain'

type Filter = 'all' | 'unread'

const TYPE_LABELS: Record<NotificationType, string> = {
  TASK_ASSIGNED: 'Przypisanie',
  TASK_UPDATED: 'Aktualizacja',
  PR_CREATED: 'Nowy PR',
  PR_REVIEWED: 'Review',
  CHAT_MESSAGE: 'Wiadomość',
}

const TYPE_COLORS: Record<NotificationType, string> = {
  TASK_ASSIGNED: 'bg-blue-100 text-blue-700',
  TASK_UPDATED: 'bg-yellow-100 text-yellow-700',
  PR_CREATED: 'bg-purple-100 text-purple-700',
  PR_REVIEWED: 'bg-green-100 text-green-700',
  CHAT_MESSAGE: 'bg-gray-100 text-gray-600',
}

function formatDate(iso: string): string {
  return new Intl.DateTimeFormat('pl-PL', {
    day: 'numeric',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(iso))
}

export default function NotificationsPage() {
  const [filter, setFilter] = useState<Filter>('all')
  const queryClient = useQueryClient()
  const { notifications: liveNotifications, markOneRead, markAllRead, setUnreadCount, decrementUnreadCount, prependNotification, incrementUnreadCount } = useNotificationStore()
  const userId = useAuthStore((s) => s.userId)
  const accessToken = useAuthStore((s) => s.accessToken)

  const { data: fetched = [], isLoading } = useQuery({
    queryKey: ['notifications'],
    queryFn: () => notificationService.getNotifications({ limit: 100 }),
  })

  // Powiadomienia na żywo przez WebSocket.
  useEffect(() => {
    if (!userId) return
    const socket = openNotificationSocket(
      userId,
      {
        onNotification: (n) => {
          prependNotification(n)
          incrementUnreadCount()
        },
      },
      accessToken,
    )
    return () => socket.close()
  }, [userId, accessToken, prependNotification, incrementUnreadCount])

  // Merge realtime-prepended notifications with fetched ones (dedup by id)
  const merged = useMemo(() => {
    const seen = new Set<number>()
    const all: Notification[] = []
    for (const n of [...liveNotifications, ...fetched]) {
      if (!seen.has(n.notificationId)) {
        seen.add(n.notificationId)
        all.push(n)
      }
    }
    return all
  }, [liveNotifications, fetched])

  const displayed = filter === 'unread' ? merged.filter((n) => !n.isRead) : merged

  async function handleMarkRead(n: Notification) {
    if (n.isRead) return
    try {
      await notificationService.markRead(n.notificationId)
      markOneRead(n.notificationId)
      decrementUnreadCount()
      queryClient.setQueryData<Notification[]>(['notifications'], (old = []) =>
        old.map((item) =>
          item.notificationId === n.notificationId ? { ...item, isRead: true } : item
        )
      )
    } catch {
      // keep as unread on failure
    }
  }

  async function handleMarkAllRead() {
    try {
      await notificationService.markAllRead()
      markAllRead()
      setUnreadCount(0)
      queryClient.setQueryData<Notification[]>(['notifications'], (old = []) =>
        old.map((n) => ({ ...n, isRead: true }))
      )
    } catch {
      // ignore
    }
  }

  const unreadTotal = merged.filter((n) => !n.isRead).length

  return (
    <div className="p-8 max-w-2xl">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-semibold">Powiadomienia</h1>
        {unreadTotal > 0 && (
          <button
            onClick={handleMarkAllRead}
            className="text-sm text-blue-600 hover:text-blue-800"
          >
            Oznacz wszystkie jako przeczytane
          </button>
        )}
      </div>

      <div className="flex gap-2 mb-4">
        {(['all', 'unread'] as Filter[]).map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`px-4 py-1.5 rounded-full text-sm font-medium transition-colors ${
              filter === f
                ? 'bg-gray-900 text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            {f === 'all' ? 'Wszystkie' : `Nieprzeczytane${unreadTotal > 0 ? ` (${unreadTotal})` : ''}`}
          </button>
        ))}
      </div>

      {isLoading ? (
        <p className="text-sm text-gray-500">Wczytywanie…</p>
      ) : displayed.length === 0 ? (
        <p className="text-sm text-gray-500 py-8 text-center">
          {filter === 'unread' ? 'Brak nieprzeczytanych powiadomień.' : 'Brak powiadomień.'}
        </p>
      ) : (
        <ul className="space-y-2">
          {displayed.map((n) => (
            <li
              key={n.notificationId}
              onClick={() => handleMarkRead(n)}
              className={`flex gap-3 p-4 rounded-xl border transition-colors cursor-pointer ${
                n.isRead
                  ? 'border-gray-100 bg-white opacity-60'
                  : 'border-gray-200 bg-white hover:bg-gray-50'
              }`}
            >
              {!n.isRead && (
                <div className="mt-1.5 w-2 h-2 rounded-full bg-blue-500 shrink-0" />
              )}
              {n.isRead && <div className="mt-1.5 w-2 h-2 shrink-0" />}
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-0.5">
                  <span className={`text-[11px] font-semibold px-2 py-0.5 rounded-full ${TYPE_COLORS[n.type] ?? 'bg-gray-100 text-gray-600'}`}>
                    {TYPE_LABELS[n.type] ?? n.type}
                  </span>
                  <span className="text-xs text-gray-400">{formatDate(n.createdAt)}</span>
                </div>
                <p className="text-sm font-medium text-gray-900 truncate">{n.title}</p>
                <p className="text-sm text-gray-500 truncate">{n.message}</p>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
