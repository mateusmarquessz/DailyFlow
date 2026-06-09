import { apiClient } from '@/api/client'
import type { DashboardStats } from '@/types/dashboard'

export const dashboardApi = {
  stats: () => apiClient.get<DashboardStats>('/dashboard/stats').then((res) => res.data),
}
