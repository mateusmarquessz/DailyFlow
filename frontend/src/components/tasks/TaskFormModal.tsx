import { useEffect } from 'react'

import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'
import { z } from 'zod'

import { Alert } from '@/components/ui/Alert'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Modal } from '@/components/ui/Modal'
import { Select } from '@/components/ui/Select'
import { getErrorMessage } from '@/lib/errors'
import type { Task, TaskPayload } from '@/types/task'

const taskSchema = z.object({
  title: z.string().min(1, 'Informe um título'),
  description: z.string().optional(),
  priority: z.enum(['low', 'medium', 'high']),
  due_date: z.string().optional(),
  due_time: z.string().optional(),
  recurrence: z.enum(['none', 'daily', 'weekly', 'monthly']),
})

type TaskFormValues = z.infer<typeof taskSchema>

const DEFAULT_VALUES: TaskFormValues = {
  title: '',
  description: '',
  priority: 'medium',
  due_date: '',
  due_time: '',
  recurrence: 'none',
}

function toFormValues(task: Task | null): TaskFormValues {
  if (!task) return DEFAULT_VALUES
  return {
    title: task.title,
    description: task.description ?? '',
    priority: task.priority,
    due_date: task.due_date ?? '',
    due_time: task.due_time?.slice(0, 5) ?? '',
    recurrence: task.recurrence,
  }
}

interface TaskFormModalProps {
  open: boolean
  task: Task | null
  onClose: () => void
  onSubmit: (payload: TaskPayload) => Promise<void>
}

export function TaskFormModal({ open, task, onClose, onSubmit }: TaskFormModalProps) {
  const {
    register,
    handleSubmit,
    reset,
    setError,
    formState: { errors, isSubmitting },
  } = useForm<TaskFormValues>({ resolver: zodResolver(taskSchema), defaultValues: DEFAULT_VALUES })

  useEffect(() => {
    if (open) reset(toFormValues(task))
  }, [open, task, reset])

  const submit = async (values: TaskFormValues) => {
    try {
      await onSubmit({
        title: values.title,
        description: values.description?.trim() ? values.description.trim() : null,
        priority: values.priority,
        due_date: values.due_date || null,
        due_time: values.due_time || null,
        recurrence: values.recurrence,
      })
      onClose()
    } catch (error) {
      setError('root', { message: getErrorMessage(error, 'Não foi possível salvar a tarefa.') })
    }
  }

  return (
    <Modal open={open} onClose={onClose} title={task ? 'Editar tarefa' : 'Nova tarefa'}>
      <form className="flex flex-col gap-4" onSubmit={handleSubmit(submit)} noValidate>
        {errors.root && <Alert variant="error">{errors.root.message}</Alert>}

        <Input label="Título" error={errors.title?.message} {...register('title')} />

        <div className="flex flex-col gap-1.5">
          <label htmlFor="description" className="text-sm font-medium text-surface-700 dark:text-surface-200">
            Descrição
          </label>
          <textarea
            id="description"
            rows={3}
            className="rounded-lg border border-surface-200 bg-white px-3.5 py-2.5 text-sm text-surface-900 outline-none transition-colors placeholder:text-surface-400 focus:border-brand-500 focus:ring-2 focus:ring-brand-500/20 dark:border-surface-700 dark:bg-surface-800 dark:text-surface-50 dark:placeholder:text-surface-500"
            placeholder="Detalhes opcionais sobre a tarefa"
            {...register('description')}
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <Select label="Prioridade" {...register('priority')}>
            <option value="low">Baixa</option>
            <option value="medium">Média</option>
            <option value="high">Alta</option>
          </Select>
          <Select label="Recorrência" {...register('recurrence')}>
            <option value="none">Não repete</option>
            <option value="daily">Diariamente</option>
            <option value="weekly">Semanalmente</option>
            <option value="monthly">Mensalmente</option>
          </Select>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <Input label="Data de vencimento" type="date" {...register('due_date')} />
          <Input label="Horário" type="time" {...register('due_time')} />
        </div>

        <div className="mt-2 flex justify-end gap-3">
          <Button type="button" variant="ghost" onClick={onClose}>
            Cancelar
          </Button>
          <Button type="submit" isLoading={isSubmitting}>
            {task ? 'Salvar alterações' : 'Criar tarefa'}
          </Button>
        </div>
      </form>
    </Modal>
  )
}
