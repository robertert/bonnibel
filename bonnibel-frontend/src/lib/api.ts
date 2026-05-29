// RĘCZNY BASE URL: Wpisany na sztywno port 8000 dla Twojego backendu w Pythonie
import type { AuthResponse } from '@/types/domain';
export const API_BASE_URL = 'http://localhost:8000/api'

export async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const headers = new Headers(init?.headers)
  if (!headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json')
  }

  const token = localStorage.getItem('accessToken')
  if (token) {
    headers.set('Authorization', `Bearer ${token}`)
  }

  let res = await fetch(`${API_BASE_URL}${path}`, { ...init, headers })

  if (res.status === 401 && !path.startsWith('/auth/')) {
    const refreshToken = localStorage.getItem('refreshToken')

    if (refreshToken) {
      try {
        const refreshRes = await fetch(`${API_BASE_URL}/auth/refresh`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ "refresh_token": refreshToken }),
        })

        if (refreshRes.ok) {
          const data : AuthResponse = await refreshRes.json()
          
          localStorage.setItem('accessToken', data.access_token)
          if (data.refresh_token) {
            localStorage.setItem('refreshToken', data.refresh_token)
          }

          headers.set('Authorization', `Bearer ${data.access_token}`)
          res = await fetch(`${API_BASE_URL}${path}`, { ...init, headers })
        } else {
          localStorage.clear()
          window.location.href = '/login'
          throw new Error('Sesja wygasła. Zaloguj się ponownie.')
        }
      } catch (err) {
        localStorage.clear()
        window.location.href = '/login'
        return Promise.reject(err)
      }
    }
  }

  if (!res.ok) {
    throw new Error(`API error ${res.status}`)
  }

  if (res.status === 204 || res.headers.get('content-length') === '0') {
    return {} as T
  }

  const text = await res.text()
  return text ? (JSON.parse(text) as T) : ({} as T)
}