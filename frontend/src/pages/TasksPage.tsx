import { useMemo, useState } from 'react'

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { ListChecks, Plus } from 'lucide-react'

import { tasksApi } from '@/api/tasks'
import { TaskFormModal } from '@/components/tasks/TaskFormModal'
import { TaskItem } from '@/components/tasks/TaskItem'
import { Alert } from '@/components/ui/Alert'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { getErrorMessage } from '@/lib/errors'
import type { Task, TaskPayload, TaskStatus } from '@/types/task'

type FilterValue = 'all' | TaskStatus

const FILTERS: { value: FilterValue; label: string }[] = [
  { value: 'all', label: 'Todas' },
  { value: 'pending', label: 'Pendentes' },
  { value: 'completed', label: 'Concluídas' },
]

export function TasksPage() {
  const queryClient = useQueryClient()
  const [filter, setFilter] = useState<FilterValue>('pending')
  const [modalOpen, setModalOpen] = useState(false)
  const [editingTask, setEditingTask] = useState<Task | null>(null)
  const [feedback, setFeedback] = useState<string | null>(null)

  const { data: tasks, isLoading, isError } = useQuery({
    queryKey: ['tasks'],
    queryFn: () => tasksApi.list(),
  })

  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: ['tasks'] })
    queryClient.invalidateQueries({ queryKey: ['dashboard-stats'] })
  }

  const createMutation = useMutation({
    mutationFn: (payload: TaskPayload) => tasksApi.create(payload),
    onSuccess: invalidate,
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, payload }: { id: number; payload: TaskPayload }) => tasksApi.update(id, payload),
    onSuccess: invalidate,
  })

  const toggleMutation = useMutation({
    mutationFn: (task: Task) => (task.status === 'completed' ? tasksApi.reopen(task.id) : tasksApi.complete(task.id)),
    onSuccess: invalidate,
    onError: (error) => setFeedback(getErrorMessage(error, 'Não foi possível atualizar a tarefa.')),
  })

  const deleteMutation = useMutation({
    mutationFn: (task: Task) => tasksApi.remove(task.id),
    onSuccess: invalidate,
    onError: (error) => setFeedback(getErrorMessage(error, 'Não foi possível excluir a tarefa.')),
  })

  const visibleTasks = useMemo(() => {
    if (!tasks) return []
    if (filter === 'all') return tasks
    return tasks.filter((task) => task.status === filter)
  }, [tasks, filter])

  const openCreateModal = () => {
    setEditingTask(null)
    setModalOpen(true)
  }

  const openEditModal = (task: Task) => {
    setEditingTask(task)
    setModalOpen(true)
  }

  const handleSubmit = async (payload: TaskPayload) => {
    if (editingTask) {
      await updateMutation.mutateAsync({ id: editingTask.id, payload })
    } else {
      await createMutation.mutateAsync(payload)
    }
  }

  const handleDelete = (task: Task) => {
    if (window.confirm(`Excluir a tarefa "${task.title}"?`)) {
      deleteMutation.mutate(task)
    }
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-surface-900 dark:text-surface-50">Tarefas</h1>
          <p className="mt-1 text-sm text-surface-500 dark:text-surface-400">
            Organize o que precisa ser feito, defina prioridades e acompanhe sua recorrência.
          </p>
        </div>
        <Button onClick={openCreateModal}>
          <Plus className="size-4" />
          Nova tarefa
        </Button>
      </div>

      {feedback && <Alert variant="error">{feedback}</Alert>}

      <div className="flex gap-2">
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

      {isLoading && <p className="text-sm text-surface-500 dark:text-surface-400">Carregando tarefas…</p>}

      {isError && <Alert variant="error">Não foi possível carregar suas tarefas. Tente novamente.</Alert>}

      {!isLoading && !isError && visibleTasks.length === 0 && (
        <Card className="flex flex-col items-center justify-center gap-3 px-6 py-16 text-center">
          <div className="flex size-14 items-center justify-center rounded-2xl bg-brand-50 text-brand-600 dark:bg-brand-900/30 dark:text-brand-300">
            <ListChecks className="size-7" />
          </div>
          <h2 className="text-lg font-semibold text-surface-900 dark:text-surface-50">Nenhuma tarefa por aqui</h2>
          <p className="max-w-md text-sm text-surface-500 dark:text-surface-400">
            {filter === 'completed'
              ? 'Você ainda não concluiu nenhuma tarefa nesse filtro.'
              : 'Crie sua primeira tarefa para começar a organizar a sua rotina.'}
          </p>
        </Card>
      )}

      <div className="flex flex-col gap-3">
        {visibleTasks.map((task) => (
          <TaskItem
            key={task.id}
            task={task}
            onToggle={(value) => toggleMutation.mutate(value)}
            onEdit={openEditModal}
            onDelete={handleDelete}
            isToggling={toggleMutation.isPending && toggleMutation.variables?.id === task.id}
          />
        ))}
      </div>

      <TaskFormModal open={modalOpen} task={editingTask} onClose={() => setModalOpen(false)} onSubmit={handleSubmit} />
    </div>
  )
}
