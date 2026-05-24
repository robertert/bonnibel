import { apiFetch } from '@/lib/api'
import type { User, UserStatus } from '@/types/domain'

export const userService = {
  getCurrentUser: (): Promise<User> => {
    return apiFetch<User>('/users/user-1')
  },

  updateCurrentUser: (data: { name: string; surname: string; status: UserStatus }): Promise<User> => {
    return apiFetch<User>('/users/user-1', {
      method: 'PATCH',
      body: JSON.stringify(data),
    })
  }
}