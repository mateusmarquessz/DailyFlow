import { useState } from 'react'

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Flame, Plus } from 'lucide-react'

import { habitsApi } from '@/api/habits'
import { HabitCard } from '@/components/habits/HabitCard'
import { HabitFormModal } from '@/components/habits/HabitFormModal'
import { Alert } from '@/components/ui/Alert'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { getErrorMessage } from '@/lib/errors'
import type { Habit, HabitPayload } from '@/types/habit'

export function HabitsPage() {
  const queryClient = useQueryClient()
  const [modalOpen, setModalOpen] = useState(false)
  const [editingHabit, setEditingHabit] = useState<Habit | null>(null)
  const [feedback, setFeedback] = useState<string | null>(null)

  const { data: habits, isLoading, isError } = useQuery({
    queryKey: ['habits'],
    queryFn: () => habitsApi.list(),
  })

  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: ['habits'] })
    queryClient.invalidateQueries({ queryKey: ['dashboard-stats'] })
  }

  const createMutation = useMutation({
    mutationFn: (payload: HabitPayload) => habitsApi.create(payload),
    onSuccess: invalidate,
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, payload }: { id: number; payload: HabitPayload }) => habitsApi.update(id, payload),
    onSuccess: invalidate,
  })

  const toggleMutation = useMutation({
    mutationFn: (habit: Habit) =>
      habit.completed_today ? habitsApi.removeCheckIn(habit.id) : habitsApi.checkIn(habit.id),
    onSuccess: invalidate,
    onError: (error) => setFeedback(getErrorMessage(error, 'Não foi possível registrar o check-in.')),
  })

  const deleteMutation = useMutation({
    mutationFn: (habit: Habit) => habitsApi.remove(habit.id),
    onSuccess: invalidate,
    onError: (error) => setFeedback(getErrorMessage(error, 'Não foi possível excluir o hábito.')),
  })

  const openCreateModal = () => {
    setEditingHabit(null)
    setModalOpen(true)
  }

  const openEditModal = (habit: Habit) => {
    setEditingHabit(habit)
    setModalOpen(true)
  }

  const handleSubmit = async (payload: HabitPayload) => {
    if (editingHabit) {
      await updateMutation.mutateAsync({ id: editingHabit.id, payload })
    } else {
      await createMutation.mutateAsync(payload)
    }
  }

  const handleDelete = (habit: Habit) => {
    if (window.confirm(`Excluir o hábito "${habit.name}"? O histórico também será apagado.`)) {
      deleteMutation.mutate(habit)
    }
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-surface-900 dark:text-surface-50">Hábitos</h1>
          <p className="mt-1 text-sm text-surface-500 dark:text-surface-400">
            Construa rotinas consistentes e acompanhe sua sequência (streak) ao longo do tempo.
          </p>
        </div>
        <Button onClick={openCreateModal}>
          <Plus className="size-4" />
          Novo hábito
        </Button>
      </div>

      {feedback && <Alert variant="error">{feedback}</Alert>}

      {isLoading && <p className="text-sm text-surface-500 dark:text-surface-400">Carregando hábitos…</p>}

      {isError && <Alert variant="error">Não foi possível carregar seus hábitos. Tente novamente.</Alert>}

      {!isLoading && !isError && (habits?.length ?? 0) === 0 && (
        <Card className="flex flex-col items-center justify-center gap-3 px-6 py-16 text-center">
          <div className="flex size-14 items-center justify-center rounded-2xl bg-brand-50 text-brand-600 dark:bg-brand-900/30 dark:text-brand-300">
            <Flame className="size-7" />
          </div>
          <h2 className="text-lg font-semibold text-surface-900 dark:text-surface-50">Nenhum hábito cadastrado</h2>
          <p className="max-w-md text-sm text-surface-500 dark:text-surface-400">
            Crie seu primeiro hábito para começar a construir uma sequência (streak) e acompanhar sua consistência.
          </p>
        </Card>
      )}

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {habits?.map((habit) => (
          <HabitCard
            key={habit.id}
            habit={habit}
            onToggleToday={(value) => toggleMutation.mutate(value)}
            onEdit={openEditModal}
            onDelete={handleDelete}
            isToggling={toggleMutation.isPending && toggleMutation.variables?.id === habit.id}
          />
        ))}
      </div>

      <HabitFormModal open={modalOpen} habit={editingHabit} onClose={() => setModalOpen(false)} onSubmit={handleSubmit} />
    </div>
  )
}
