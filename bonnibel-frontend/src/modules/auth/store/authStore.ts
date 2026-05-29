import { create } from 'zustand'

interface AuthState {
  isAuthenticated: boolean
  userId: string | null
  accessToken: string | null
  // Usunęliśmy isBypass
  login: (accessToken: string, refreshToken: string, userId: string) => void
  logout: () => void
}

function initialState() {
  // Teraz pobieramy dane tylko z prawdziwego localStorage
  const accessToken = localStorage.getItem('accessToken');
  return {
    isAuthenticated: !!accessToken,
    userId: localStorage.getItem('userId'),
    accessToken: accessToken,
  }
}

export const useAuthStore = create<AuthState>((set) => ({
  ...initialState(),

  login: (accessToken, refreshToken, userId) => {
    localStorage.setItem('accessToken', accessToken)
    localStorage.setItem('refreshToken', refreshToken)
    localStorage.setItem('userId', userId)
    set({ isAuthenticated: true, userId, accessToken })
  },

  logout: () => {
    localStorage.removeItem('accessToken')
    localStorage.removeItem('refreshToken')
    localStorage.removeItem('userId')
    set({
      isAuthenticated: false,
      userId: null,
      accessToken: null,
    })
  },
}))