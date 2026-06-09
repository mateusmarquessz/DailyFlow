import { useEffect, useState } from 'react'

import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'
import { z } from 'zod'

import { getHabitIcon, HABIT_ICON_OPTIONS } from '@/components/habits/habitIcons'
import { Alert } from '@/components/ui/Alert'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Modal } from '@/components/ui/Modal'
import { Select } from '@/components/ui/Select'
import { getErrorMessage } from '@/lib/errors'
import type { Habit, HabitPayload } from '@/types/habit'

const WEEKDAYS = [
  { value: 0, label: 'Seg' },
  { value: 1, label: 'Ter' },
  { value: 2, label: 'Qua' },
  { value: 3, label: 'Qui' },
  { value: 4, label: 'Sex' },
  { value: 5, label: 'Sáb' },
  { value: 6, label: 'Dom' },
]

const habitSchema = z.object({
  name: z.string().min(1, 'Informe um nome'),
  description: z.string().optional(),
  frequency: z.enum(['daily', 'weekly']),
  color: z.string(),
  icon: z.string(),
})

type HabitFormValues = z.infer<typeof habitSchema>

const DEFAULT_VALUES: HabitFormValues = {
  name: '',
  description: '',
  frequency: 'daily',
  color: '#6366F1',
  icon: 'check-circle',
}

function toFormValues(habit: Habit | null): HabitFormValues {
  if (!habit) return DEFAULT_VALUES
  return {
    name: habit.name,
    description: habit.description ?? '',
    frequency: habit.frequency,
    color: habit.color,
    icon: habit.icon,
  }
}

interface HabitFormModalProps {
  open: boolean
  habit: Habit | null
  onClose: () => void
  onSubmit: (payload: HabitPayload) => Promise<void>
}

export function HabitFormModal({ open, habit, onClose, onSubmit }: HabitFormModalProps) {
  const [targetDays, setTargetDays] = useState<number[]>([])
  const {
    register,
    handleSubmit,
    reset,
    watch,
    setValue,
    setError,
    formState: { errors, isSubmitting },
  } = useForm<HabitFormValues>({ resolver: zodResolver(habitSchema), defaultValues: DEFAULT_VALUES })

  const frequency = watch('frequency')
  const selectedIcon = watch('icon')

  useEffect(() => {
    if (open) {
      reset(toFormValues(habit))
      setTargetDays(habit?.target_days ?? [])
    }
  }, [open, habit, reset])

  const toggleDay = (day: number) => {
    setTargetDays((current) => (current.includes(day) ? current.filter((d) => d !== day) : [...current, day].sort()))
  }

  const submit = async (values: HabitFormValues) => {
    try {
      await onSubmit({
        name: values.name,
        description: values.description?.trim() ? values.description.trim() : null,
        frequency: values.frequency,
        target_days: values.frequency === 'weekly' && targetDays.length > 0 ? targetDays : null,
        color: values.color,
        icon: values.icon,
      })
      onClose()
    } catch (error) {
      setError('root', { message: getErrorMessage(error, 'Não foi possível salvar o hábito.') })
    }
  }

  return (
    <Modal open={open} onClose={onClose} title={habit ? 'Editar hábito' : 'Novo hábito'}>
      <form className="flex flex-col gap-4" onSubmit={handleSubmit(submit)} noValidate>
        {errors.root && <Alert variant="error">{errors.root.message}</Alert>}

        <Input label="Nome" error={errors.name?.message} {...register('name')} />

        <div className="flex flex-col gap-1.5">
          <label htmlFor="habit-description" className="text-sm font-medium text-surface-700 dark:text-surface-200">
            Descrição
          </label>
          <textarea
            id="habit-description"
            rows={2}
            className="rounded-lg border border-surface-200 bg-white px-3.5 py-2.5 text-sm text-surface-900 outline-none transition-colors placeholder:text-surface-400 focus:border-brand-500 focus:ring-2 focus:ring-brand-500/20 dark:border-surface-700 dark:bg-surface-800 dark:text-surface-50 dark:placeholder:text-surface-500"
            placeholder="Detalhes opcionais sobre o hábito"
            {...register('description')}
          />
        </div>

        <Select label="Frequência" {...register('frequency')}>
          <option value="daily">Todos os dias</option>
          <option value="weekly">Dias específicos da semana</option>
        </Select>

        {frequency === 'weekly' && (
          <div className="flex flex-col gap-1.5">
            <span className="text-sm font-medium text-surface-700 dark:text-surface-200">Dias da semana</span>
            <div className="flex flex-wrap gap-2">
              {WEEKDAYS.map(({ value, label }) => (
                <button
                  key={value}
                  type="button"
                  onClick={() => toggleDay(value)}
                  className={`rounded-full px-3 py-1.5 text-sm font-medium transition-colors ${
                    targetDays.includes(value)
                      ? 'bg-brand-600 text-white'
                      : 'bg-surface-100 text-surface-600 hover:bg-surface-200 dark:bg-surface-800 dark:text-surface-300 dark:hover:bg-surface-700'
                  }`}
                >
                  {label}
                </button>
              ))}
            </div>
            <p className="text-xs text-surface-400 dark:text-surface-500">
              Nenhum dia selecionado conta como todos os dias.
            </p>
          </div>
        )}

        <div className="grid grid-cols-2 gap-4">
          <div className="flex flex-col gap-1.5">
            <label htmlFor="habit-color" className="text-sm font-medium text-surface-700 dark:text-surface-200">
              Cor
            </label>
            <input
              id="habit-color"
              type="color"
              className="h-11 w-full cursor-pointer rounded-lg border border-surface-200 bg-white px-2 dark:border-surface-700 dark:bg-surface-800"
              {...register('color')}
            />
          </div>

          <div className="flex flex-col gap-1.5">
            <span className="text-sm font-medium text-surface-700 dark:text-surface-200">Ícone</span>
            <div className="flex flex-wrap gap-2">
              {HABIT_ICON_OPTIONS.map((name) => {
                const Icon = getHabitIcon(name)
                const active = selectedIcon === name
                return (
                  <button
                    key={name}
                    type="button"
                    aria-label={`Selecionar ícone ${name}`}
                    aria-pressed={active}
                    onClick={() => setValue('icon', name, { shouldDirty: true })}
                    className={`flex size-9 items-center justify-center rounded-lg border-2 transition-colors ${
                      active
                        ? 'border-brand-600 bg-brand-50 text-brand-600 dark:bg-brand-900/30 dark:text-brand-300'
                        : 'border-surface-200 text-surface-500 hover:border-surface-300 dark:border-surface-700 dark:text-surface-400'
                    }`}
                  >
                    <Icon className="size-4" />
                  </button>
                )
              })}
            </div>
            <input type="hidden" {...register('icon')} />
          </div>
        </div>

        <div className="mt-2 flex justify-end gap-3">
          <Button type="button" variant="ghost" onClick={onClose}>
            Cancelar
          </Button>
          <Button type="submit" isLoading={isSubmitting}>
            {habit ? 'Salvar alterações' : 'Criar hábito'}
          </Button>
        </div>
      </form>
    </Modal>
  )
}
