export type HabitFrequency = 'daily' | 'weekly'

export interface Habit {
  id: number
  name: string
  description: string | null
  frequency: HabitFrequency
  target_days: number[] | null
  color: string
  icon: string
  is_active: boolean
  current_streak: number
  longest_streak: number
  completed_today: boolean
  created_at: string
  updated_at: string
}

export interface HabitPayload {
  name: string
  description?: string | null
  frequency?: HabitFrequency
  target_days?: number[] | null
  color?: string
  icon?: string
}

export type HabitUpdatePayload = Partial<HabitPayload> & { is_active?: boolean }

export interface HabitHistoryEntry {
  date: string
  completed: boolean
  streak_snapshot: number
}
