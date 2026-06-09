export interface DayCompletion {
  date: string
  tasks_completed: number
  habits_completed: number
}

export interface DashboardStats {
  tasks_due_today: number
  tasks_completed_today: number
  habits_total: number
  habits_completed_today: number
  best_current_streak: number
  goals_in_progress: number
  weekly_completions: DayCompletion[]
}
