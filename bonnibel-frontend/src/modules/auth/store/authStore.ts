import { create } from 'zustand'
import { BYPASS_AUTH, BYPASS_USER_ID } from '@/lib/env'

interface AuthState {
  isAuthenticated: boolean
  userId: string | null
  accessToken: string | null
  isBypass: boolean
  login: (accessToken: string, refreshToken: string, userId: string) => void
  logout: () => void
}

function initialState() {
  if (BYPASS_AUTH) {
    const userId = localStorage.getItem('userId') ?? BYPASS_USER_ID
    localStorage.setItem('userId', userId)
    localStorage.setItem('accessToken', 'bypass-token')
    return {
      isAuthenticated: true,
      userId,
      accessToken: 'bypass-token',
      isBypass: true,
    }
  }

  return {
    isAuthenticated: !!localStorage.getItem('accessToken'),
    userId: localStorage.getItem('userId'),
    accessToken: localStorage.getItem('accessToken'),
    isBypass: false,
  }
}

export const useAuthStore = create<AuthState>((set) => ({
  ...initialState(),

  login: (accessToken, refreshToken, userId) => {
    localStorage.setItem('accessToken', accessToken)
    localStorage.setItem('refreshToken', refreshToken)
    localStorage.setItem('userId', userId)
    set({ isAuthenticated: true, userId, accessToken, isBypass: BYPASS_AUTH })
  },

  logout: () => {
    if (BYPASS_AUTH) {
      // W trybie bypass nie wylogowujemy: admin user zostaje aktywny.
      return
    }
    localStorage.removeItem('accessToken')
    localStorage.removeItem('refreshToken')
    localStorage.removeItem('userId')
    set({
      isAuthenticated: false,
      userId: null,
      accessToken: null,
      isBypass: false,
    })
  },
}))
