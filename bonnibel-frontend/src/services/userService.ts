import { apiFetch } from '@/lib/api'
import type { User, UserStatus } from '@/types/domain'

export const userService = {

  listUsers: async (): Promise<User[]> => {
    return apiFetch<User[]>('/users')
  },

  getCurrentUser: async (): Promise<User> => {
    const userId = localStorage.getItem('userId')
    if (!userId) throw new Error('Brak zalogowanego użytkownika')
    return apiFetch<User>(`/users/${userId}`)
  },

  
  updateCurrentUser: async (data: { name: string; surname: string; status: UserStatus; email: string }): Promise<User> => {
    const userId = localStorage.getItem('userId')
    if (!userId) throw new Error('Brak zalogowanego użytkownika')

    
    await apiFetch(`/users/${userId}/profile`, {
      method: 'PUT',
      body: JSON.stringify({
        email: data.email,
        name: data.name,
        surname: data.surname
      })
    })

    
    const updatedUser = await apiFetch<User>(`/users/${userId}/status`, {
      method: 'PUT',
      body: JSON.stringify({
        status: data.status
      })
    })

    
    return updatedUser
  }
}