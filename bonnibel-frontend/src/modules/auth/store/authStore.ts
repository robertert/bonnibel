import { create } from 'zustand'
import { authService } from '@/services/authService'

interface AuthState {
  isAuthenticated: boolean
  userId: string | null
  accessToken: string | null
  // Usunęliśmy isBypass
  login: (accessToken: string, refreshToken: string, userId: string) => void
  logout: () => Promise<void>
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

  logout: async () => {
    const refreshToken = localStorage.getItem('refreshToken')

    if (refreshToken) {
      try {
        // 2. Wysyłamy żądanie wylogowania na serwer
        await authService.logout(refreshToken)
      } catch (error) {
        // Jeśli backend sypnie błędem (np. token już wygasł), 
        // i tak chcemy wylogować użytkownika lokalnie, więc logujemy błąd w konsoli
        console.error("Błąd podczas wylogowywania na serwerze:", error)
      }
    }
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