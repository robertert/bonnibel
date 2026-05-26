import { create } from 'zustand';

interface AuthState {
  isAuthenticated: boolean;
  userId: string | null;
  accessToken: string | null;
  login: (accessToken: string, refreshToken: string, userId: string) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  isAuthenticated: !!localStorage.getItem('accessToken'),
  userId: localStorage.getItem('userId'),
  accessToken: localStorage.getItem('accessToken'),

  login: (accessToken, refreshToken, userId) => {
    localStorage.setItem('accessToken', accessToken);
    localStorage.setItem('refreshToken', refreshToken);
    localStorage.setItem('userId', userId);
    set({ isAuthenticated: true, userId, accessToken });
  },

  logout: () => {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('userId');
    set({ isAuthenticated: false, userId: null, accessToken: null });
  },
}));