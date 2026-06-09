import { apiClient } from '@/api/client'
import type { Goal, GoalPayload, GoalUpdatePayload } from '@/types/goal'

export const goalsApi = {
  list: () => apiClient.get<Goal[]>('/goals').then((res) => res.data),

  create: (payload: GoalPayload) => apiClient.post<Goal>('/goals', payload).then((res) => res.data),

  update: (id: number, payload: GoalUpdatePayload) =>
    apiClient.patch<Goal>(`/goals/${id}`, payload).then((res) => res.data),

  remove: (id: number) => apiClient.delete<void>(`/goals/${id}`).then((res) => res.data),
}
