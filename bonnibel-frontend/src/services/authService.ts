import { apiFetch } from '@/lib/api';
import type { AuthResponse, AuthTokens } from '@/types/domain';

export const authService = {
  signup: (email: string, password: string, name: string, surname: string): Promise<AuthTokens> => {
    return apiFetch<AuthTokens>('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, password, name, surname }),
    });
  },

  login: (email: string, password: string): Promise<AuthResponse> => {
    return apiFetch<AuthResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
  },

  refresh: (refreshToken: string): Promise<AuthTokens> => {
    return apiFetch<AuthTokens>('/auth/refresh', {
      method: 'POST',
      body: JSON.stringify({ refreshToken }),
    });
  }
};
