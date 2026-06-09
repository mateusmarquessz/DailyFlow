import { useState } from 'react'

import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'
import { Link } from 'react-router-dom'
import { z } from 'zod'

import { authApi } from '@/api/auth'
import { AuthLayout } from '@/components/auth/AuthLayout'
import { Alert } from '@/components/ui/Alert'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { getErrorMessage } from '@/lib/errors'

const schema = z.object({
  email: z.string().min(1, 'Informe seu e-mail').email('E-mail inválido'),
})

type FormValues = z.infer<typeof schema>

export function ForgotPasswordPage() {
  const [status, setStatus] = useState<{ kind: 'success' | 'error'; message: string } | null>(null)

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({ resolver: zodResolver(schema) })

  const onSubmit = async (values: FormValues) => {
    setStatus(null)
    try {
      const response = await authApi.forgotPassword(values.email)
      setStatus({ kind: 'success', message: response.message })
    } catch (error) {
      setStatus({ kind: 'error', message: getErrorMessage(error) })
    }
  }

  return (
    <AuthLayout
      title="Esqueceu sua senha?"
      subtitle="Informe seu e-mail e enviaremos instruções para redefini-la"
    >
      <form className="flex flex-col gap-4" onSubmit={handleSubmit(onSubmit)} noValidate>
        {status && <Alert variant={status.kind === 'success' ? 'success' : 'error'}>{status.message}</Alert>}
        <Input
          label="E-mail"
          type="email"
          autoComplete="email"
          placeholder="voce@exemplo.com"
          error={errors.email?.message}
          {...register('email')}
        />
        <Button type="submit" isLoading={isSubmitting} className="mt-1 w-full">
          Enviar instruções
        </Button>
      </form>
      <p className="mt-6 text-center text-sm text-surface-500 dark:text-surface-400">
        Lembrou sua senha?{' '}
        <Link to="/login" className="font-medium text-brand-600 hover:underline dark:text-brand-400">
          Voltar para o login
        </Link>
      </p>
    </AuthLayout>
  )
}
