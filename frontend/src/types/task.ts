export type TaskPriority = 'low' | 'medium' | 'high'
export type TaskStatus = 'pending' | 'completed'
export type RecurrenceType = 'none' | 'daily' | 'weekly' | 'monthly'

export interface Task {
  id: number
  title: string
  description: string | null
  priority: TaskPriority
  status: TaskStatus
  due_date: string | null
  due_time: string | null
  recurrence: RecurrenceType
  parent_task_id: number | null
  completed_at: string | null
  xp_awarded: number
  created_at: string
  updated_at: string
}

export interface TaskPayload {
  title: string
  description?: string | null
  priority?: TaskPriority
  due_date?: string | null
  due_time?: string | null
  recurrence?: RecurrenceType
}

export type TaskUpdatePayload = Partial<TaskPayload>

export interface TaskFilters {
  status_filter?: TaskStatus
  due_before?: string
  due_after?: string
}
