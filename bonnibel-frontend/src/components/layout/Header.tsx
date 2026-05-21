export default function Header() {
  return (
    <header className="h-14 border-b border-gray-200 flex items-center justify-between px-6 bg-white">
      <div className="text-sm text-gray-500">System zarządzania postępem prac zespołu</div>
      <div className="flex items-center gap-3">
        <button className="text-sm text-gray-600 hover:text-gray-900">
          Powiadomienia
        </button>
        <div className="w-8 h-8 rounded-full bg-gray-300" />
      </div>
    </header>
  )
}
