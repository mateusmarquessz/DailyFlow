import { apiClient } from '@/api/client'
import type { Habit, HabitHistoryEntry, HabitPayload, HabitUpdatePayload } from '@/types/habit'

export const habitsApi = {
  list: () => apiClient.get<Habit[]>('/habits').then((res) => res.data),

  get: (id: number) => apiClient.get<Habit>(`/habits/${id}`).then((res) => res.data),

  create: (payload: HabitPayload) => apiClient.post<Habit>('/habits', payload).then((res) => res.data),

  update: (id: number, payload: HabitUpdatePayload) =>
    apiClient.patch<Habit>(`/habits/${id}`, payload).then((res) => res.data),

  remove: (id: number) => apiClient.delete<void>(`/habits/${id}`).then((res) => res.data),

  history: (id: number) => apiClient.get<HabitHistoryEntry[]>(`/habits/${id}/history`).then((res) => res.data),

  checkIn: (id: number, onDate?: string) =>
    apiClient.post<Habit>(`/habits/${id}/check-in`, { on_date: onDate ?? null }).then((res) => res.data),

  removeCheckIn: (id: number, onDate?: string) =>
    apiClient
      .delete<Habit>(`/habits/${id}/check-in`, { params: onDate ? { on_date: onDate } : undefined })
      .then((res) => res.data),
}
