import { Outlet } from 'react-router-dom'

export default function AuthLayout() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="w-full max-w-md bg-white rounded-lg shadow p-8">
        <div className="text-center mb-6">
          <h1 className="text-2xl font-bold">Bonnibel</h1>
          <p className="text-sm text-gray-500">System zarządzania postępem prac</p>
        </div>
        <Outlet />
      </div>
    </div>
  )
}
