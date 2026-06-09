import { Calendar, Pencil, Trash2 } from 'lucide-react'

import { Badge } from '@/components/ui/Badge'
import { Card } from '@/components/ui/Card'
import type { Goal, GoalStatus, GoalType } from '@/types/goal'

const TYPE_LABEL: Record<GoalType, string> = {
  weekly: 'Semanal',
  monthly: 'Mensal',
  yearly: 'Anual',
}

const STATUS_LABEL: Record<GoalStatus, string> = {
  in_progress: 'Em andamento',
  completed: 'Concluída',
  failed: 'Não atingida',
}

const STATUS_TONE: Record<GoalStatus, 'brand' | 'success' | 'danger'> = {
  in_progress: 'brand',
  completed: 'success',
  failed: 'danger',
}

function formatDeadline(value: string | null): string | null {
  if (!value) return null
  const [year, month, day] = value.split('-')
  return `${day}/${month}/${year}`
}

interface GoalItemProps {
  goal: Goal
  onEdit: (goal: Goal) => void
  onDelete: (goal: Goal) => void
}

export function GoalItem({ goal, onEdit, onDelete }: GoalItemProps) {
  const deadline = formatDeadline(goal.deadline)
  const progress = Math.min(100, Math.max(0, goal.progress_percent))

  return (
    <Card className="flex flex-col gap-3 p-4">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <div className="flex flex-wrap items-center gap-2">
            <p className="text-sm font-medium text-surface-900 dark:text-surface-50">{goal.title}</p>
            <Badge tone="neutral">{TYPE_LABEL[goal.type]}</Badge>
            <Badge tone={STATUS_TONE[goal.status]}>{STATUS_LABEL[goal.status]}</Badge>
          </div>
          {goal.description && (
            <p className="mt-1 line-clamp-2 text-sm text-surface-500 dark:text-surface-400">{goal.description}</p>
          )}
        </div>

        <div className="flex shrink-0 items-center gap-1">
          <button
            type="button"
            aria-label="Editar meta"
            onClick={() => onEdit(goal)}
            className="rounded-lg p-2 text-surface-400 transition-colors hover:bg-surface-100 hover:text-surface-700 dark:hover:bg-surface-800 dark:hover:text-surface-200"
          >
            <Pencil className="size-4" />
          </button>
          <button
            type="button"
            aria-label="Excluir meta"
            onClick={() => onDelete(goal)}
            className="rounded-lg p-2 text-surface-400 transition-colors hover:bg-red-50 hover:text-red-600 dark:hover:bg-red-950/40 dark:hover:text-red-400"
          >
            <Trash2 className="size-4" />
          </button>
        </div>
      </div>

      <div>
        <div className="flex items-center justify-between text-xs text-surface-500 dark:text-surface-400">
          <span>
            {goal.current_value} / {goal.target_value}
          </span>
          <span>{progress.toFixed(0)}%</span>
        </div>
        <div className="mt-1.5 h-2 w-full overflow-hidden rounded-full bg-surface-100 dark:bg-surface-800">
          <div
            className={`h-full rounded-full transition-all ${
              goal.status === 'completed' ? 'bg-emerald-500' : 'bg-brand-600'
            }`}
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {deadline && (
        <span className="inline-flex items-center gap-1 text-xs text-surface-500 dark:text-surface-400">
          <Calendar className="size-3.5" />
          Prazo: {deadline}
        </span>
      )}
    </Card>
  )
}
