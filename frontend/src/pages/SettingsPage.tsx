import { useState } from 'react'

import { zodResolver } from '@hookform/resolvers/zod'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Moon, Send, Sun } from 'lucide-react'
import { useForm } from 'react-hook-form'
import { z } from 'zod'

import { telegramApi } from '@/api/telegram'
import { Alert } from '@/components/ui/Alert'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { Input } from '@/components/ui/Input'
import { useTheme } from '@/context/ThemeContext'
import { getErrorMessage } from '@/lib/errors'
import { clsx } from 'clsx'

const linkSchema = z.object({
  code: z.string().min(4, 'Informe o código enviado pelo bot').max(12),
})

type LinkFormValues = z.infer<typeof linkSchema>

function formatDateTime(value: string) {
  return new Date(value).toLocaleString('pt-BR', { dateStyle: 'short', timeStyle: 'short' })
}

export function SettingsPage() {
  const { theme, setTheme } = useTheme()
  const queryClient = useQueryClient()
  const [feedback, setFeedback] = useState<{ kind: 'success' | 'error'; message: string } | null>(null)

  const { data: status, isLoading } = useQuery({
    queryKey: ['telegram-status'],
    queryFn: () => telegramApi.status(),
  })

  const linkForm = useForm<LinkFormValues>({ resolver: zodResolver(linkSchema) })

  const invalidateStatus = () => queryClient.invalidateQueries({ queryKey: ['telegram-status'] })

  const linkMutation = useMutation({
    mutationFn: (values: LinkFormValues) => telegramApi.link(values.code.trim().toUpperCase()),
    onSuccess: () => {
      setFeedback({ kind: 'success', message: 'Conta do Telegram conectada com sucesso!' })
      linkForm.reset()
      invalidateStatus()
    },
    onError: (error) =>
      setFeedback({ kind: 'error', message: getErrorMessage(error, 'Não foi possível conectar com esse código.') }),
  })

  const unlinkMutation = useMutation({
    mutationFn: () => telegramApi.unlink(),
    onSuccess: () => {
      setFeedback({ kind: 'success', message: 'Conta do Telegram desconectada.' })
      invalidateStatus()
    },
    onError: (error) =>
      setFeedback({ kind: 'error', message: getErrorMessage(error, 'Não foi possível desconectar a conta.') }),
  })

  const onSubmitLink = (values: LinkFormValues) => {
    setFeedback(null)
    linkMutation.mutate(values)
  }

  const onUnlink = () => {
    setFeedback(null)
    unlinkMutation.mutate()
  }

  return (
    <div className="mx-auto flex max-w-2xl flex-col gap-6">
      <div>
        <h1 className="text-2xl font-semibold text-surface-900 dark:text-surface-50">Configurações</h1>
        <p className="mt-1 text-sm text-surface-500 dark:text-surface-400">
          Personalize sua experiência e conecte integrações.
        </p>
      </div>

      <Card className="p-6">
        <h2 className="mb-1 text-base font-semibold text-surface-900 dark:text-surface-50">Aparência</h2>
        <p className="mb-4 text-sm text-surface-500 dark:text-surface-400">Escolha entre tema claro ou escuro.</p>
        <div className="flex gap-3">
          <button
            onClick={() => setTheme('light')}
            className={clsx(
              'flex flex-1 items-center justify-center gap-2 rounded-lg border px-4 py-3 text-sm font-medium transition-colors',
              theme === 'light'
                ? 'border-brand-500 bg-brand-50 text-brand-700 dark:bg-brand-900/30 dark:text-brand-300'
                : 'border-surface-200 text-surface-600 hover:bg-surface-50 dark:border-surface-700 dark:text-surface-300 dark:hover:bg-surface-800',
            )}
          >
            <Sun className="size-[18px]" /> Claro
          </button>
          <button
            onClick={() => setTheme('dark')}
            className={clsx(
              'flex flex-1 items-center justify-center gap-2 rounded-lg border px-4 py-3 text-sm font-medium transition-colors',
              theme === 'dark'
                ? 'border-brand-500 bg-brand-50 text-brand-700 dark:bg-brand-900/30 dark:text-brand-300'
                : 'border-surface-200 text-surface-600 hover:bg-surface-50 dark:border-surface-700 dark:text-surface-300 dark:hover:bg-surface-800',
            )}
          >
            <Moon className="size-[18px]" /> Escuro
          </button>
        </div>
      </Card>

      <Card className="p-6">
        <div className="flex items-start gap-4">
          <div className="flex size-11 shrink-0 items-center justify-center rounded-xl bg-sky-50 text-sky-600 dark:bg-sky-900/30 dark:text-sky-300">
            <Send className="size-5" />
          </div>
          <div className="flex-1">
            <h2 className="text-base font-semibold text-surface-900 dark:text-surface-50">Bot do Telegram</h2>
            <p className="mt-1 text-sm text-surface-500 dark:text-surface-400">
              Receba lembretes automáticos de tarefas, hábitos e metas diretamente no Telegram — incluindo o resumo
              matinal e noturno de produtividade.
            </p>

            {feedback && (
              <div className="mt-4">
                <Alert variant={feedback.kind === 'success' ? 'success' : 'error'}>{feedback.message}</Alert>
              </div>
            )}

            {!isLoading && status?.is_linked && (
              <div className="mt-4 flex flex-col gap-3">
                <Alert variant="success">
                  Conectado{status.linked_at ? ` desde ${formatDateTime(status.linked_at)}` : ''}. Você já recebe
                  lembretes pelo Telegram.
                </Alert>
                <div>
                  <Button variant="danger" size="sm" isLoading={unlinkMutation.isPending} onClick={onUnlink}>
                    Desconectar conta do Telegram
                  </Button>
                </div>
              </div>
            )}

            {!isLoading && status && !status.is_linked && (
              <>
                <ol className="mt-4 list-inside list-decimal space-y-1.5 text-sm text-surface-600 dark:text-surface-300">
                  <li>
                    Abra o Telegram e procure{' '}
                    {status.bot_username ? (
                      <a
                        href={`https://t.me/${status.bot_username}`}
                        target="_blank"
                        rel="noreferrer"
                        className="font-medium text-brand-600 hover:underline dark:text-brand-400"
                      >
                        @{status.bot_username}
                      </a>
                    ) : (
                      'pelo nosso bot'
                    )}
                    .
                  </li>
                  <li>
                    Envie <code className="rounded bg-surface-100 px-1.5 py-0.5 text-xs dark:bg-surface-800">/start</code> — o
                    bot responderá com um código de vinculação.
                  </li>
                  <li>Cole o código abaixo para conectar sua conta.</li>
                </ol>
                <form className="mt-4 flex items-end gap-3" onSubmit={linkForm.handleSubmit(onSubmitLink)} noValidate>
                  <div className="flex-1">
                    <Input
                      label="Código de vinculação"
                      placeholder="Ex: AB12CD"
                      autoCapitalize="characters"
                      error={linkForm.formState.errors.code?.message}
                      {...linkForm.register('code')}
                    />
                  </div>
                  <Button type="submit" isLoading={linkMutation.isPending}>
                    Conectar
                  </Button>
                </form>
              </>
            )}
          </div>
        </div>
      </Card>
    </div>
  )
}
