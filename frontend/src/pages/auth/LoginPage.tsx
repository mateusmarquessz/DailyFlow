import { useState } from 'react'

import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { z } from 'zod'

import { AuthLayout } from '@/components/auth/AuthLayout'
import { Alert } from '@/components/ui/Alert'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { useAuth } from '@/context/AuthContext'
import { getErrorMessage } from '@/lib/errors'

const schema = z.object({
  email: z.string().min(1, 'Informe seu e-mail').email('E-mail inválido'),
  password: z.string().min(1, 'Informe sua senha'),
})

type FormValues = z.infer<typeof schema>

export function LoginPage() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [formError, setFormError] = useState<string | null>(null)

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({ resolver: zodResolver(schema) })

  const onSubmit = async (values: FormValues) => {
    setFormError(null)
    try {
      await login(values)
      const redirectTo = (location.state as { from?: string } | null)?.from ?? '/dashboard'
      navigate(redirectTo, { replace: true })
    } catch (error) {
      setFormError(getErrorMessage(error, 'Não foi possível entrar. Verifique suas credenciais.'))
    }
  }

  return (
    <AuthLayout title="Bem-vindo de volta" subtitle="Entre para continuar organizando sua rotina">
      <form className="flex flex-col gap-4" onSubmit={handleSubmit(onSubmit)} noValidate>
        {formError && <Alert variant="error">{formError}</Alert>}
        <Input
          label="E-mail"
          type="email"
          autoComplete="email"
          placeholder="voce@exemplo.com"
          error={errors.email?.message}
          {...register('email')}
        />
        <Input
          label="Senha"
          type="password"
          autoComplete="current-password"
          placeholder="••••••••"
          error={errors.password?.message}
          {...register('password')}
        />
        <div className="flex justify-end">
          <Link to="/forgot-password" className="text-sm font-medium text-brand-600 hover:underline dark:text-brand-400">
            Esqueceu a senha?
          </Link>
        </div>
        <Button type="submit" isLoading={isSubmitting} className="mt-1 w-full">
          Entrar
        </Button>
      </form>
      <p className="mt-6 text-center text-sm text-surface-500 dark:text-surface-400">
        Ainda não tem conta?{' '}
        <Link to="/register" className="font-medium text-brand-600 hover:underline dark:text-brand-400">
          Cadastre-se
        </Link>
      </p>
    </AuthLayout>
  )
}
