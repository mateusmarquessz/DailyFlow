import { Calendar, Clock, Pencil, Repeat, Trash2 } from 'lucide-react'

import { Badge } from '@/components/ui/Badge'
import { Card } from '@/components/ui/Card'
import type { Task, TaskPriority } from '@/types/task'

const PRIORITY_LABEL: Record<TaskPriority, string> = {
  low: 'Baixa',
  medium: 'Média',
  high: 'Alta',
}

const PRIORITY_TONE: Record<TaskPriority, 'neutral' | 'brand' | 'danger'> = {
  low: 'neutral',
  medium: 'brand',
  high: 'danger',
}

const RECURRENCE_LABEL: Record<string, string> = {
  none: '',
  daily: 'Repete diariamente',
  weekly: 'Repete semanalmente',
  monthly: 'Repete mensalmente',
}

function formatDate(value: string | null): string | null {
  if (!value) return null
  const [year, month, day] = value.split('-')
  return `${day}/${month}/${year}`
}

interface TaskItemProps {
  task: Task
  onToggle: (task: Task) => void
  onEdit: (task: Task) => void
  onDelete: (task: Task) => void
  isToggling?: boolean
}

export function TaskItem({ task, onToggle, onEdit, onDelete, isToggling }: TaskItemProps) {
  const completed = task.status === 'completed'
  const dueDate = formatDate(task.due_date)

  return (
    <Card className="flex items-start gap-3 p-4">
      <button
        type="button"
        role="checkbox"
        aria-checked={completed}
        aria-label={completed ? 'Marcar como pendente' : 'Marcar como concluída'}
        onClick={() => onToggle(task)}
        disabled={isToggling}
        className={`mt-0.5 flex size-5 shrink-0 items-center justify-center rounded-full border-2 transition-colors ${
          completed
            ? 'border-brand-600 bg-brand-600 text-white'
            : 'border-surface-300 text-transparent hover:border-brand-500 dark:border-surface-600'
        }`}
      >
        <svg viewBox="0 0 12 12" fill="none" className="size-3">
          <path d="M2 6.5L4.5 9L10 3" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      </button>

      <div className="min-w-0 flex-1">
        <div className="flex flex-wrap items-center gap-2">
          <p
            className={`text-sm font-medium ${
              completed ? 'text-surface-400 line-through dark:text-surface-500' : 'text-surface-900 dark:text-surface-50'
            }`}
          >
            {task.title}
          </p>
          <Badge tone={PRIORITY_TONE[task.priority]}>{PRIORITY_LABEL[task.priority]}</Badge>
        </div>

        {task.description && (
          <p className="mt-1 line-clamp-2 text-sm text-surface-500 dark:text-surface-400">{task.description}</p>
        )}

        <div className="mt-2 flex flex-wrap items-center gap-3 text-xs text-surface-500 dark:text-surface-400">
          {dueDate && (
            <span className="inline-flex items-center gap-1">
              <Calendar className="size-3.5" />
              {dueDate}
            </span>
          )}
          {task.due_time && (
            <span className="inline-flex items-center gap-1">
              <Clock className="size-3.5" />
              {task.due_time.slice(0, 5)}
            </span>
          )}
          {task.recurrence !== 'none' && (
            <span className="inline-flex items-center gap-1">
              <Repeat className="size-3.5" />
              {RECURRENCE_LABEL[task.recurrence]}
            </span>
          )}
        </div>
      </div>

      <div className="flex shrink-0 items-center gap-1">
        <button
          type="button"
          aria-label="Editar tarefa"
          onClick={() => onEdit(task)}
          className="rounded-lg p-2 text-surface-400 transition-colors hover:bg-surface-100 hover:text-surface-700 dark:hover:bg-surface-800 dark:hover:text-surface-200"
        >
          <Pencil className="size-4" />
        </button>
        <button
          type="button"
          aria-label="Excluir tarefa"
          onClick={() => onDelete(task)}
          className="rounded-lg p-2 text-surface-400 transition-colors hover:bg-red-50 hover:text-red-600 dark:hover:bg-red-950/40 dark:hover:text-red-400"
        >
          <Trash2 className="size-4" />
        </button>
      </div>
    </Card>
  )
}
