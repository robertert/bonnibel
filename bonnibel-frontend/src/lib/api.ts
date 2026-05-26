// TODO: kiedy wybierzemy backend, podstawić właściwy base URL i interceptor auth.
export const API_BASE_URL = 'http://localhost:3001';

export async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {

  const token = localStorage.getItem('accessToken');
  

  const headers = new Headers(init?.headers);
  headers.set('Content-Type', 'application/json');
  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  let res = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers,
  });

 
  if (res.status === 401 && !path.startsWith('/auth/')) {
    const refreshToken = localStorage.getItem('refreshToken');

    if (refreshToken) {
      try {
        
        const refreshRes = await fetch(`${API_BASE_URL}/auth/refresh`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ refreshToken }),
        });

        if (refreshRes.ok) {
          const data = await refreshRes.json();
          
          localStorage.setItem('accessToken', data.accessToken);
          if (data.refreshToken) {
            localStorage.setItem('refreshToken', data.refreshToken);
          }

          
          headers.set('Authorization', `Bearer ${data.accessToken}`);
          res = await fetch(`${API_BASE_URL}${path}`, {
            ...init,
            headers,
          });
        } else {
          
          localStorage.clear();
          window.location.href = '/login';
          throw new Error('Sesja wygasła. Zaloguj się ponownie.');
        }
      } catch (err) {
        localStorage.clear();
        window.location.href = '/login';
        return Promise.reject(err);
      }
    }
  }

  
  if (!res.ok) {
    throw new Error(`API error ${res.status}`);
  }

  
  if (res.status === 204 || res.headers.get('content-length') === '0') {
    return {} as T;
  }

  const text = await res.text();
  return text ? (JSON.parse(text) as T) : ({} as T);
}