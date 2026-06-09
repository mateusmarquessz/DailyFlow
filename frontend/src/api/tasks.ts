import { apiClient } from '@/api/client'
import type { Task, TaskFilters, TaskPayload, TaskUpdatePayload } from '@/types/task'

export const tasksApi = {
  list: (filters: TaskFilters = {}) =>
    apiClient.get<Task[]>('/tasks', { params: filters }).then((res) => res.data),

  get: (id: number) => apiClient.get<Task>(`/tasks/${id}`).then((res) => res.data),

  create: (payload: TaskPayload) => apiClient.post<Task>('/tasks', payload).then((res) => res.data),

  update: (id: number, payload: TaskUpdatePayload) =>
    apiClient.patch<Task>(`/tasks/${id}`, payload).then((res) => res.data),

  remove: (id: number) => apiClient.delete<void>(`/tasks/${id}`).then((res) => res.data),

  complete: (id: number) => apiClient.post<Task>(`/tasks/${id}/complete`).then((res) => res.data),

  reopen: (id: number) => apiClient.post<Task>(`/tasks/${id}/reopen`).then((res) => res.data),
}
