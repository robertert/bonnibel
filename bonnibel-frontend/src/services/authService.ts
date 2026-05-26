import { apiFetch } from '@/lib/api';
import type { AuthResponse, AuthTokens } from '@/types/domain';

export const authService = {
  // POST /api/auth/signup
  signup: (userId: string, password: string): Promise<AuthResponse> => {
    return apiFetch<AuthResponse>('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ userId, password }),
    });
  },

  // POST /api/auth/login
  login: (userId: string, password: string): Promise<AuthResponse> => {
    return apiFetch<AuthResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ userId, password }),
    });
  },

  // POST /api/auth/refresh
  refresh: (refreshToken: string): Promise<AuthTokens> => {
    return apiFetch<AuthTokens>('/auth/refresh', {
      method: 'POST',
      body: JSON.stringify({ refreshToken }),
    });
  }
};