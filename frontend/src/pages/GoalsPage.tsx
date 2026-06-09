import { useMemo, useState } from 'react'

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Plus, Target } from 'lucide-react'

import { goalsApi } from '@/api/goals'
import { Alert } from '@/components/ui/Alert'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { GoalFormModal } from '@/components/goals/GoalFormModal'
import { GoalItem } from '@/components/goals/GoalItem'
import { getErrorMessage } from '@/lib/errors'
import type { Goal, GoalPayload, GoalStatus } from '@/types/goal'

type FilterValue = 'all' | GoalStatus

const FILTERS: { value: FilterValue; label: string }[] = [
  { value: 'all', label: 'Todas' },
  { value: 'in_progress', label: 'Em andamento' },
  { value: 'completed', label: 'Concluídas' },
  { value: 'failed', label: 'Não atingidas' },
]

export function GoalsPage() {
  const queryClient = useQueryClient()
  const [filter, setFilter] = useState<FilterValue>('in_progress')
  const [modalOpen, setModalOpen] = useState(false)
  const [editingGoal, setEditingGoal] = useState<Goal | null>(null)
  const [feedback, setFeedback] = useState<string | null>(null)

  const { data: goals, isLoading, isError } = useQuery({
    queryKey: ['goals'],
    queryFn: () => goalsApi.list(),
  })

  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: ['goals'] })
    queryClient.invalidateQueries({ queryKey: ['dashboard-stats'] })
    queryClient.invalidateQueries({ queryKey: ['gamification-profile'] })
  }

  const createMutation = useMutation({
    mutationFn: (payload: GoalPayload) => goalsApi.create(payload),
    onSuccess: invalidate,
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, payload }: { id: number; payload: GoalPayload }) => goalsApi.update(id, payload),
    onSuccess: invalidate,
  })

  const deleteMutation = useMutation({
    mutationFn: (goal: Goal) => goalsApi.remove(goal.id),
    onSuccess: invalidate,
    onError: (error) => setFeedback(getErrorMessage(error, 'Não foi possível excluir a meta.')),
  })

  const visibleGoals = useMemo(() => {
    if (!goals) return []
    if (filter === 'all') return goals
    return goals.filter((goal) => goal.status === filter)
  }, [goals, filter])

  const openCreateModal = () => {
    setEditingGoal(null)
    setModalOpen(true)
  }

  const openEditModal = (goal: Goal) => {
    setEditingGoal(goal)
    setModalOpen(true)
  }

  const handleSubmit = async (payload: GoalPayload) => {
    if (editingGoal) {
      await updateMutation.mutateAsync({ id: editingGoal.id, payload })
    } else {
      await createMutation.mutateAsync(payload)
    }
  }

  const handleDelete = (goal: Goal) => {
    if (window.confirm(`Excluir a meta "${goal.title}"?`)) {
      deleteMutation.mutate(goal)
    }
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-surface-900 dark:text-surface-50">Metas</h1>
          <p className="mt-1 text-sm text-surface-500 dark:text-surface-400">
            Defina metas semanais, mensais e anuais e acompanhe seu progresso até a conclusão.
          </p>
        </div>
        <Button onClick={openCreateModal}>
          <Plus className="size-4" />
          Nova meta
        </Button>
      </div>

      {feedback && <Alert variant="error">{feedback}</Alert>}

      <div className="flex flex-wrap gap-2">
        {FILTERS.map(({ value, label }) => (
          <button
            key={value}
            type="button"
            onClick={() => setFilter(value)}
            className={`rounded-full px-4 py-1.5 text-sm font-medium transition-colors ${
              filter === value
                ? 'bg-brand-600 text-white'
                : 'bg-surface-100 text-surface-600 hover:bg-surface-200 dark:bg-surface-800 dark:text-surface-300 dark:hover:bg-surface-700'
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      {isLoading && <p className="text-sm text-surface-500 dark:text-surface-400">Carregando metas…</p>}

      {isError && <Alert variant="error">Não foi possível carregar suas metas. Tente novamente.</Alert>}

      {!isLoading && !isError && visibleGoals.length === 0 && (
        <Card className="flex flex-col items-center justify-center gap-3 px-6 py-16 text-center">
          <div className="flex size-14 items-center justify-center rounded-2xl bg-brand-50 text-brand-600 dark:bg-brand-900/30 dark:text-brand-300">
            <Target className="size-7" />
          </div>
          <h2 className="text-lg font-semibold text-surface-900 dark:text-surface-50">Nenhuma meta por aqui</h2>
          <p className="max-w-md text-sm text-surface-500 dark:text-surface-400">
            {filter === 'completed'
              ? 'Você ainda não concluiu nenhuma meta nesse filtro.'
              : 'Crie sua primeira meta para acompanhar seu progresso ao longo do tempo.'}
          </p>
        </Card>
      )}

      <div className="grid gap-3 sm:grid-cols-2">
        {visibleGoals.map((goal) => (
          <GoalItem key={goal.id} goal={goal} onEdit={openEditModal} onDelete={handleDelete} />
        ))}
      </div>

      <GoalFormModal open={modalOpen} goal={editingGoal} onClose={() => setModalOpen(false)} onSubmit={handleSubmit} />
    </div>
  )
}
