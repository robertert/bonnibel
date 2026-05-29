import { apiFetch } from '@/lib/api'; // poprawiłem ścieżkę importu na Twój api.ts, upewnij się czy jest ok
import type { AuthTokens, AuthResponse } from '@/types/domain';

// Definiujemy interfejs dla danych rejestracji, dokładnie tak jak w Pydantic (UserCreate)
export interface SignupData {
  email: string;
  password: string;
  name: string;
  surname: string;
}

export const authService = {
  // POST /auth/register - Rejestracja wymaga teraz pełnego obiektu SignupData
  signup: (data: SignupData): Promise<{ message: string; user_id: string }> => {
    return apiFetch<{ message: string; user_id: string }>('/auth/register', {
      method: 'POST',
      body: JSON.stringify(data), // Wysyłamy email, password, name, surname w formacie JSON
    });
  },

  // POST /auth/login - Logujemy się za pomocą adresu e-mail
  login: (email: string, password: string): Promise<AuthResponse> => {
    return apiFetch<AuthResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }), // Backend oczekuje pól "email" i "password"
    });
  },

  // POST /auth/refresh - Odświeżanie tokenu (Silent Refresh z api.ts)
  refresh: (refreshToken: string): Promise<AuthResponse> => {
    return apiFetch<AuthResponse>('/auth/refresh', {
      method: 'POST',
      body: JSON.stringify({"refresh_token": refreshToken }),
    });
  }
};