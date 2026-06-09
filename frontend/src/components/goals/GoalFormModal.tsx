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
import type { Goal, GoalPayload } from '@/types/goal'

const goalSchema = z.object({
  title: z.string().min(1, 'Informe um título'),
  description: z.string().optional(),
  type: z.enum(['weekly', 'monthly', 'yearly']),
  target_value: z
    .string()
    .min(1, 'Informe um valor alvo')
    .refine((value) => Number(value) > 0, 'Informe um valor maior que zero'),
  deadline: z.string().optional(),
})

type GoalFormValues = z.infer<typeof goalSchema>

const DEFAULT_VALUES: GoalFormValues = {
  title: '',
  description: '',
  type: 'monthly',
  target_value: '1',
  deadline: '',
}

function toFormValues(goal: Goal | null): GoalFormValues {
  if (!goal) return DEFAULT_VALUES
  return {
    title: goal.title,
    description: goal.description ?? '',
    type: goal.type,
    target_value: String(goal.target_value),
    deadline: goal.deadline ?? '',
  }
}

interface GoalFormModalProps {
  open: boolean
  goal: Goal | null
  onClose: () => void
  onSubmit: (payload: GoalPayload) => Promise<void>
}

export function GoalFormModal({ open, goal, onClose, onSubmit }: GoalFormModalProps) {
  const {
    register,
    handleSubmit,
    reset,
    setError,
    formState: { errors, isSubmitting },
  } = useForm<GoalFormValues>({ resolver: zodResolver(goalSchema), defaultValues: DEFAULT_VALUES })

  useEffect(() => {
    if (open) reset(toFormValues(goal))
  }, [open, goal, reset])

  const submit = async (values: GoalFormValues) => {
    try {
      await onSubmit({
        title: values.title,
        description: values.description?.trim() ? values.description.trim() : null,
        type: values.type,
        target_value: Number(values.target_value),
        deadline: values.deadline?.trim() ? values.deadline : null,
      })
      onClose()
    } catch (error) {
      setError('root', { message: getErrorMessage(error, 'Não foi possível salvar a meta.') })
    }
  }

  return (
    <Modal open={open} onClose={onClose} title={goal ? 'Editar meta' : 'Nova meta'}>
      <form className="flex flex-col gap-4" onSubmit={handleSubmit(submit)} noValidate>
        {errors.root && <Alert variant="error">{errors.root.message}</Alert>}

        <Input label="Título" error={errors.title?.message} {...register('title')} />

        <div className="flex flex-col gap-1.5">
          <label htmlFor="goal-description" className="text-sm font-medium text-surface-700 dark:text-surface-200">
            Descrição
          </label>
          <textarea
            id="goal-description"
            rows={2}
            className="rounded-lg border border-surface-200 bg-white px-3.5 py-2.5 text-sm text-surface-900 outline-none transition-colors placeholder:text-surface-400 focus:border-brand-500 focus:ring-2 focus:ring-brand-500/20 dark:border-surface-700 dark:bg-surface-800 dark:text-surface-50 dark:placeholder:text-surface-500"
            placeholder="Detalhes opcionais sobre a meta"
            {...register('description')}
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <Select label="Tipo" {...register('type')}>
            <option value="weekly">Semanal</option>
            <option value="monthly">Mensal</option>
            <option value="yearly">Anual</option>
          </Select>

          <Input
            label="Valor alvo"
            type="number"
            min={1}
            step="any"
            error={errors.target_value?.message}
            {...register('target_value')}
          />
        </div>

        <Input label="Prazo (opcional)" type="date" error={errors.deadline?.message} {...register('deadline')} />

        <div className="mt-2 flex justify-end gap-3">
          <Button type="button" variant="ghost" onClick={onClose}>
            Cancelar
          </Button>
          <Button type="submit" isLoading={isSubmitting}>
            {goal ? 'Salvar alterações' : 'Criar meta'}
          </Button>
        </div>
      </form>
    </Modal>
  )
}
