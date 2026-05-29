import { useEffect } from 'react'
import { Outlet } from 'react-router-dom'
import Sidebar from './Sidebar'
import Header from './Header'
import { useAuthStore } from '@/modules/auth/store/authStore'
import { useNotificationStore } from '@/store/notificationStore'
import { notificationService, openNotificationSocket } from '@/services/notificationService'

export default function AppLayout() {
  const { userId, accessToken, isBypass } = useAuthStore()
  const { setUnreadCount, incrementUnreadCount, prependNotification } = useNotificationStore()

  useEffect(() => {
    if (!userId) return

    notificationService.getUnreadCount()
      .then(({ unreadCount }) => setUnreadCount(unreadCount))
      .catch(() => {})

    const token = isBypass ? null : accessToken
    const ws = openNotificationSocket(userId, {
      onNotification: (n) => {
        prependNotification(n)
        incrementUnreadCount()
      },
    }, token)

    return () => ws.close()
  }, [userId])

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />
        <main className="flex-1 overflow-auto">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
