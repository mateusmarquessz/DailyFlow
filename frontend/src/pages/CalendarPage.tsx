import { useMemo, useState } from 'react'

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import {
  addMonths,
  eachDayOfInterval,
  endOfMonth,
  endOfWeek,
  format,
  isSameMonth,
  isToday,
  startOfMonth,
  startOfWeek,
  subMonths,
} from 'date-fns'
import { ptBR } from 'date-fns/locale'
import { ChevronLeft, ChevronRight } from 'lucide-react'

import { tasksApi } from '@/api/tasks'
import { TaskFormModal } from '@/components/tasks/TaskFormModal'
import { Alert } from '@/components/ui/Alert'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { getErrorMessage } from '@/lib/errors'
import type { Task, TaskPayload, TaskPriority } from '@/types/task'

const WEEKDAY_LABELS = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb']

const PRIORITY_DOT: Record<TaskPriority, string> = {
  low: 'bg-surface-400',
  medium: 'bg-brand-500',
  high: 'bg-red-500',
}

interface CalendarTaskChipProps {
  task: Task
  onDragStart: (task: Task) => void
  onClick: (task: Task) => void
}

function CalendarTaskChip({ task, onDragStart, onClick }: CalendarTaskChipProps) {
  const completed = task.status === 'completed'

  return (
    <button
      type="button"
      draggable
      onDragStart={(event) => {
        event.dataTransfer.effectAllowed = 'move'
        event.dataTransfer.setData('text/plain', String(task.id))
        onDragStart(task)
      }}
      onClick={() => onClick(task)}
      title={task.title}
      className={`flex w-full items-center gap-1.5 rounded-md px-1.5 py-1 text-left text-xs transition-colors ${
        completed
          ? 'bg-surface-100 text-surface-400 line-through dark:bg-surface-800 dark:text-surface-500'
          : 'bg-white text-surface-700 hover:bg-surface-50 dark:bg-surface-800 dark:text-surface-200 dark:hover:bg-surface-700'
      } cursor-grab border border-surface-200 active:cursor-grabbing dark:border-surface-700`}
    >
      <span className={`size-1.5 shrink-0 rounded-full ${PRIORITY_DOT[task.priority]}`} />
      <span className="truncate">{task.title}</span>
    </button>
  )
}

export function CalendarPage() {
  const queryClient = useQueryClient()
  const [currentMonth, setCurrentMonth] = useState(() => startOfMonth(new Date()))
  const [draggingTask, setDraggingTask] = useState<Task | null>(null)
  const [dragOverDay, setDragOverDay] = useState<string | null>(null)
  const [editingTask, setEditingTask] = useState<Task | null>(null)
  const [modalOpen, setModalOpen] = useState(false)
  const [feedback, setFeedback] = useState<string | null>(null)

  const { data: tasks, isLoading, isError } = useQuery({
    queryKey: ['tasks'],
    queryFn: () => tasksApi.list(),
  })

  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: ['tasks'] })
    queryClient.invalidateQueries({ queryKey: ['dashboard-stats'] })
  }

  const rescheduleMutation = useMutation({
    mutationFn: ({ id, due_date }: { id: number; due_date: string }) => tasksApi.update(id, { due_date }),
    onSuccess: invalidate,
    onError: (error) => setFeedback(getErrorMessage(error, 'Não foi possível reagendar a tarefa.')),
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, payload }: { id: number; payload: TaskPayload }) => tasksApi.update(id, payload),
    onSuccess: invalidate,
  })

  const days = useMemo(() => {
    const start = startOfWeek(startOfMonth(currentMonth), { weekStartsOn: 0 })
    const end = endOfWeek(endOfMonth(currentMonth), { weekStartsOn: 0 })
    return eachDayOfInterval({ start, end })
  }, [currentMonth])

  const tasksByDay = useMemo(() => {
    const map = new Map<string, Task[]>()
    for (const task of tasks ?? []) {
      if (!task.due_date) continue
      const list = map.get(task.due_date) ?? []
      list.push(task)
      map.set(task.due_date, list)
    }
    return map
  }, [tasks])

  const handleDrop = (day: Date) => {
    setDragOverDay(null)
    if (!draggingTask) return
    const isoDay = format(day, 'yyyy-MM-dd')
    if (draggingTask.due_date === isoDay) {
      setDraggingTask(null)
      return
    }
    rescheduleMutation.mutate({ id: draggingTask.id, due_date: isoDay })
    setDraggingTask(null)
  }

  const openEditModal = (task: Task) => {
    setEditingTask(task)
    setModalOpen(true)
  }

  const handleSubmit = async (payload: TaskPayload) => {
    if (!editingTask) return
    await updateMutation.mutateAsync({ id: editingTask.id, payload })
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-surface-900 dark:text-surface-50">Calendário</h1>
          <p className="mt-1 text-sm text-surface-500 dark:text-surface-400">
            Arraste uma tarefa para outro dia para reagendá-la, ou clique para editar os detalhes.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="ghost" onClick={() => setCurrentMonth((month) => subMonths(month, 1))} aria-label="Mês anterior">
            <ChevronLeft className="size-4" />
          </Button>
          <span className="min-w-40 text-center text-sm font-medium capitalize text-surface-900 dark:text-surface-50">
            {format(currentMonth, 'MMMM \'de\' yyyy', { locale: ptBR })}
          </span>
          <Button variant="ghost" onClick={() => setCurrentMonth((month) => addMonths(month, 1))} aria-label="Próximo mês">
            <ChevronRight className="size-4" />
          </Button>
          <Button variant="secondary" onClick={() => setCurrentMonth(startOfMonth(new Date()))}>
            Hoje
          </Button>
        </div>
      </div>

      {feedback && <Alert variant="error">{feedback}</Alert>}

      {isLoading && <p className="text-sm text-surface-500 dark:text-surface-400">Carregando calendário…</p>}

      {isError && <Alert variant="error">Não foi possível carregar suas tarefas. Tente novamente.</Alert>}

      {!isLoading && !isError && (
        <Card className="overflow-hidden p-0">
          <div className="grid grid-cols-7 border-b border-surface-200 dark:border-surface-800">
            {WEEKDAY_LABELS.map((label) => (
              <div
                key={label}
                className="px-2 py-2 text-center text-xs font-semibold uppercase tracking-wide text-surface-500 dark:text-surface-400"
              >
                {label}
              </div>
            ))}
          </div>

          <div className="grid grid-cols-7">
            {days.map((day) => {
              const isoDay = format(day, 'yyyy-MM-dd')
              const dayTasks = tasksByDay.get(isoDay) ?? []
              const inCurrentMonth = isSameMonth(day, currentMonth)
              const isDragOver = dragOverDay === isoDay

              return (
                <div
                  key={isoDay}
                  onDragOver={(event) => {
                    event.preventDefault()
                    event.dataTransfer.dropEffect = 'move'
                    if (dragOverDay !== isoDay) setDragOverDay(isoDay)
                  }}
                  onDragLeave={() => setDragOverDay((current) => (current === isoDay ? null : current))}
                  onDrop={(event) => {
                    event.preventDefault()
                    handleDrop(day)
                  }}
                  className={`flex min-h-28 flex-col gap-1 border-b border-r border-surface-200 p-1.5 transition-colors last:border-r-0 dark:border-surface-800 ${
                    inCurrentMonth ? 'bg-white dark:bg-surface-900' : 'bg-surface-50 dark:bg-surface-900/40'
                  } ${isDragOver ? 'bg-brand-50 dark:bg-brand-900/20' : ''}`}
                >
                  <span
                    className={`self-start rounded-full px-1.5 text-xs font-medium ${
                      isToday(day)
                        ? 'bg-brand-600 text-white'
                        : inCurrentMonth
                          ? 'text-surface-600 dark:text-surface-300'
                          : 'text-surface-400 dark:text-surface-600'
                    }`}
                  >
                    {format(day, 'd')}
                  </span>

                  <div className="flex flex-col gap-1">
                    {dayTasks.map((task) => (
                      <CalendarTaskChip
                        key={task.id}
                        task={task}
                        onDragStart={setDraggingTask}
                        onClick={openEditModal}
                      />
                    ))}
                  </div>
                </div>
              )
            })}
          </div>
        </Card>
      )}

      <TaskFormModal
        open={modalOpen}
        task={editingTask}
        onClose={() => setModalOpen(false)}
        onSubmit={handleSubmit}
      />
    </div>
  )
}
