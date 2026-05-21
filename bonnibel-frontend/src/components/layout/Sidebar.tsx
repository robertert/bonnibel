import { NavLink } from 'react-router-dom'

const navItems = [
  { to: '/projects', label: 'Projekty' },
  { to: '/my-tasks', label: 'Moje zadania' },
  { to: '/reviews', label: 'Review' },
  { to: '/notifications', label: 'Powiadomienia' },
  { to: '/analytics', label: 'Analityka' },
  { to: '/profile', label: 'Profil' },
]

export default function Sidebar() {
  return (
    <aside className="w-60 bg-gray-900 text-gray-100 flex flex-col">
      <div className="px-6 py-5 text-xl font-bold border-b border-gray-800">
        Bonnibel
      </div>
      <nav className="flex-1 p-3 space-y-1">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              `block px-3 py-2 rounded text-sm transition-colors ${
                isActive
                  ? 'bg-gray-700 text-white'
                  : 'hover:bg-gray-800 text-gray-300'
              }`
            }
          >
            {item.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  )
}
