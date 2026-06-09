import { Flame, Pencil, Trash2, Trophy } from 'lucide-react'

import { getHabitIcon } from '@/components/habits/habitIcons'
import { Card } from '@/components/ui/Card'
import type { Habit } from '@/types/habit'

interface HabitCardProps {
  habit: Habit
  onToggleToday: (habit: Habit) => void
  onEdit: (habit: Habit) => void
  onDelete: (habit: Habit) => void
  isToggling?: boolean
}

export function HabitCard({ habit, onToggleToday, onEdit, onDelete, isToggling }: HabitCardProps) {
  const Icon = getHabitIcon(habit.icon)

  return (
    <Card className="flex flex-col gap-4 p-5">
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-3">
          <div
            className="flex size-11 shrink-0 items-center justify-center rounded-2xl"
            style={{ backgroundColor: `${habit.color}1a`, color: habit.color }}
          >
            <Icon className="size-5" />
          </div>
          <div>
            <p className="font-medium text-surface-900 dark:text-surface-50">{habit.name}</p>
            {habit.description && (
              <p className="line-clamp-1 text-sm text-surface-500 dark:text-surface-400">{habit.description}</p>
            )}
          </div>
        </div>

        <div className="flex shrink-0 items-center gap-1">
          <button
            type="button"
            aria-label="Editar hábito"
            onClick={() => onEdit(habit)}
            className="rounded-lg p-2 text-surface-400 transition-colors hover:bg-surface-100 hover:text-surface-700 dark:hover:bg-surface-800 dark:hover:text-surface-200"
          >
            <Pencil className="size-4" />
          </button>
          <button
            type="button"
            aria-label="Excluir hábito"
            onClick={() => onDelete(habit)}
            className="rounded-lg p-2 text-surface-400 transition-colors hover:bg-red-50 hover:text-red-600 dark:hover:bg-red-950/40 dark:hover:text-red-400"
          >
            <Trash2 className="size-4" />
          </button>
        </div>
      </div>

      <div className="flex items-center gap-4 text-sm">
        <span className="inline-flex items-center gap-1.5 text-amber-600 dark:text-amber-400">
          <Flame className="size-4" />
          <strong>{habit.current_streak}</strong> {habit.current_streak === 1 ? 'dia seguido' : 'dias seguidos'}
        </span>
        <span className="inline-flex items-center gap-1.5 text-surface-500 dark:text-surface-400">
          <Trophy className="size-4" />
          recorde de <strong>{habit.longest_streak}</strong>
        </span>
      </div>

      <button
        type="button"
        onClick={() => onToggleToday(habit)}
        disabled={isToggling}
        className={`flex h-11 items-center justify-center gap-2 rounded-lg text-sm font-medium transition-colors ${
          habit.completed_today
            ? 'bg-emerald-50 text-emerald-700 hover:bg-emerald-100 dark:bg-emerald-950/40 dark:text-emerald-300'
            : 'bg-brand-600 text-white hover:bg-brand-700'
        } disabled:cursor-not-allowed disabled:opacity-60`}
      >
        {habit.completed_today ? 'Concluído hoje ✓ (clique para desfazer)' : 'Marcar como feito hoje'}
      </button>
    </Card>
  )
}
