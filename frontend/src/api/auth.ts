import { apiClient } from '@/api/client'
import type {
  AuthResponse,
  ChangePasswordPayload,
  LoginPayload,
  RegisterPayload,
  UpdateProfilePayload,
  User,
} from '@/types/auth'

export const authApi = {
  register: (payload: RegisterPayload) =>
    apiClient.post<AuthResponse>('/auth/register', payload).then((res) => res.data),

  login: (payload: LoginPayload) =>
    apiClient.post<AuthResponse>('/auth/login', payload).then((res) => res.data),

  logout: (refreshToken: string) => apiClient.post('/auth/logout', { refresh_token: refreshToken }),

  me: () => apiClient.get<User>('/auth/me').then((res) => res.data),

  forgotPassword: (email: string) =>
    apiClient.post<{ message: string }>('/auth/forgot-password', { email }).then((res) => res.data),

  resetPassword: (token: string, newPassword: string) =>
    apiClient
      .post<{ message: string }>('/auth/reset-password', { token, new_password: newPassword })
      .then((res) => res.data),

  updateProfile: (payload: UpdateProfilePayload) =>
    apiClient.patch<User>('/users/me', payload).then((res) => res.data),

  changePassword: (payload: ChangePasswordPayload) =>
    apiClient.post<{ message: string }>('/users/me/change-password', payload).then((res) => res.data),
}
