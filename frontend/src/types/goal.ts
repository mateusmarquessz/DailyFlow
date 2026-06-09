export type GoalType = 'weekly' | 'monthly' | 'yearly'
export type GoalStatus = 'in_progress' | 'completed' | 'failed'

export interface Goal {
  id: number
  title: string
  description: string | null
  type: GoalType
  status: GoalStatus
  target_value: number
  current_value: number
  progress_percent: number
  deadline: string | null
  created_at: string
  updated_at: string
}

export interface GoalPayload {
  title: string
  description?: string | null
  type?: GoalType
  target_value?: number
  deadline?: string | null
}

export interface GoalUpdatePayload extends Partial<GoalPayload> {
  status?: GoalStatus
  current_value?: number
}
