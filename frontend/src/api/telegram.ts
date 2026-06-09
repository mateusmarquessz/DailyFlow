import { apiClient } from '@/api/client'
import type { TelegramStatus } from '@/types/telegram'

export const telegramApi = {
  status: () => apiClient.get<TelegramStatus>('/telegram/status').then((res) => res.data),

  link: (code: string) => apiClient.post<TelegramStatus>('/telegram/link', { code }).then((res) => res.data),

  unlink: () => apiClient.delete<{ message: string }>('/telegram/link').then((res) => res.data),
}
