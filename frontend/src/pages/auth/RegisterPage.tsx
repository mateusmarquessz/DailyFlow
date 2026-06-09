import { useState } from 'react'

import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'
import { Link, useNavigate } from 'react-router-dom'
import { z } from 'zod'

import { AuthLayout } from '@/components/auth/AuthLayout'
import { Alert } from '@/components/ui/Alert'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { useAuth } from '@/context/AuthContext'
import { getErrorMessage } from '@/lib/errors'

const schema = z
  .object({
    name: z.string().min(1, 'Informe seu nome'),
    email: z.string().min(1, 'Informe seu e-mail').email('E-mail inválido'),
    password: z.string().min(8, 'A senha deve ter ao menos 8 caracteres'),
    confirmPassword: z.string().min(1, 'Confirme sua senha'),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: 'As senhas não coincidem',
    path: ['confirmPassword'],
  })

type FormValues = z.infer<typeof schema>

export function RegisterPage() {
  const { register: registerUser } = useAuth()
  const navigate = useNavigate()
  const [formError, setFormError] = useState<string | null>(null)

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({ resolver: zodResolver(schema) })

  const onSubmit = async (values: FormValues) => {
    setFormError(null)
    try {
      await registerUser({ name: values.name, email: values.email, password: values.password })
      navigate('/dashboard', { replace: true })
    } catch (error) {
      setFormError(getErrorMessage(error, 'Não foi possível criar sua conta.'))
    }
  }

  return (
    <AuthLayout title="Crie sua conta" subtitle="Organize tarefas, hábitos e metas em um só lugar">
      <form className="flex flex-col gap-4" onSubmit={handleSubmit(onSubmit)} noValidate>
        {formError && <Alert variant="error">{formError}</Alert>}
        <Input label="Nome" autoComplete="name" placeholder="Seu nome" error={errors.name?.message} {...register('name')} />
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
          autoComplete="new-password"
          placeholder="Mínimo 8 caracteres"
          error={errors.password?.message}
          {...register('password')}
        />
        <Input
          label="Confirmar senha"
          type="password"
          autoComplete="new-password"
          placeholder="Repita a senha"
          error={errors.confirmPassword?.message}
          {...register('confirmPassword')}
        />
        <Button type="submit" isLoading={isSubmitting} className="mt-1 w-full">
          Criar conta
        </Button>
      </form>
      <p className="mt-6 text-center text-sm text-surface-500 dark:text-surface-400">
        Já tem uma conta?{' '}
        <Link to="/login" className="font-medium text-brand-600 hover:underline dark:text-brand-400">
          Entrar
        </Link>
      </p>
    </AuthLayout>
  )
}
