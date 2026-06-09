import { useState } from 'react'

import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { z } from 'zod'

import { authApi } from '@/api/auth'
import { AuthLayout } from '@/components/auth/AuthLayout'
import { Alert } from '@/components/ui/Alert'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { getErrorMessage } from '@/lib/errors'

const schema = z
  .object({
    password: z.string().min(8, 'A senha deve ter ao menos 8 caracteres'),
    confirmPassword: z.string().min(1, 'Confirme sua senha'),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: 'As senhas não coincidem',
    path: ['confirmPassword'],
  })

type FormValues = z.infer<typeof schema>

export function ResetPasswordPage() {
  const [searchParams] = useSearchParams()
  const token = searchParams.get('token') ?? ''
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
      await authApi.resetPassword(token, values.password)
      navigate('/login', { replace: true, state: { resetSuccess: true } })
    } catch (error) {
      setFormError(getErrorMessage(error, 'Não foi possível redefinir sua senha. O link pode ter expirado.'))
    }
  }

  if (!token) {
    return (
      <AuthLayout title="Link inválido">
        <Alert variant="error">
          Este link de redefinição de senha está incompleto. Solicite um novo e-mail de recuperação.
        </Alert>
        <Link
          to="/forgot-password"
          className="mt-4 block text-center text-sm font-medium text-brand-600 hover:underline dark:text-brand-400"
        >
          Solicitar novo link
        </Link>
      </AuthLayout>
    )
  }

  return (
    <AuthLayout title="Defina uma nova senha" subtitle="Escolha uma senha forte para proteger sua conta">
      <form className="flex flex-col gap-4" onSubmit={handleSubmit(onSubmit)} noValidate>
        {formError && <Alert variant="error">{formError}</Alert>}
        <Input
          label="Nova senha"
          type="password"
          autoComplete="new-password"
          placeholder="Mínimo 8 caracteres"
          error={errors.password?.message}
          {...register('password')}
        />
        <Input
          label="Confirmar nova senha"
          type="password"
          autoComplete="new-password"
          placeholder="Repita a senha"
          error={errors.confirmPassword?.message}
          {...register('confirmPassword')}
        />
        <Button type="submit" isLoading={isSubmitting} className="mt-1 w-full">
          Redefinir senha
        </Button>
      </form>
    </AuthLayout>
  )
}
