export type ReportPeriod = 'daily' | 'weekly' | 'monthly'
export type ReportExportFormat = 'pdf' | 'excel'

export interface ReportDayEntry {
  date: string
  tasks_completed: number
  habits_completed: number
}

export interface ReportSummary {
  period: ReportPeriod
  start_date: string
  end_date: string
  tasks_completed: number
  tasks_due: number
  task_completion_rate: number
  habits_active: number
  habit_checkins: number
  habit_completion_rate: number
  goals_completed: number
  best_streak: number
  daily_breakdown: ReportDayEntry[]
}
