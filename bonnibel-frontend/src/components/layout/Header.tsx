import { Link } from 'react-router-dom'
import { useNotificationStore } from '@/store/notificationStore'

export default function Header() {
  const unreadCount = useNotificationStore((s) => s.unreadCount)
  const badgeLabel = unreadCount > 99 ? '99+' : String(unreadCount)

  return (
    <header className="h-14 border-b border-gray-200 flex items-center justify-between px-6 bg-white">
      <div className="text-sm text-gray-500">System zarządzania postępem prac zespołu</div>
      <div className="flex items-center gap-3">
        <Link to="/notifications" className="relative text-sm text-gray-600 hover:text-gray-900">
          Powiadomienia
          {unreadCount > 0 && (
            <span className="absolute -top-2 -right-4 min-w-[18px] h-[18px] flex items-center justify-center rounded-full bg-red-500 text-white text-[10px] font-semibold px-1">
              {badgeLabel}
            </span>
          )}
        </Link>
        <div className="w-8 h-8 rounded-full bg-gray-300" />
      </div>
    </header>
  )
}
