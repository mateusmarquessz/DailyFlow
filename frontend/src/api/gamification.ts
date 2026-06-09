import { apiClient } from '@/api/client'
import type { GamificationProfile } from '@/types/gamification'

export const gamificationApi = {
  profile: () => apiClient.get<GamificationProfile>('/gamification/profile').then((res) => res.data),
}
