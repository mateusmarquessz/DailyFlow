export interface AchievementCatalogEntry {
  code: string
  title: string
  description: string
  icon: string
  unlocked: boolean
  unlocked_at: string | null
}

export interface GamificationProfile {
  xp_total: number
  level: number
  xp_for_next_level: number
  level_progress_percent: number
  current_streak: number
  longest_streak: number
  achievements: AchievementCatalogEntry[]
}
