import { useState } from 'react'

import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'
import { z } from 'zod'

import { authApi } from '@/api/auth'
import { Alert } from '@/components/ui/Alert'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { Input } from '@/components/ui/Input'
import { useAuth } from '@/context/AuthContext'
import { getErrorMessage } from '@/lib/errors'

const profileSchema = z.object({
  name: z.string().min(1, 'Informe seu nome'),
})

const passwordSchema = z
  .object({
    current_password: z.string().min(1, 'Informe sua senha atual'),
    new_password: z.string().min(8, 'A nova senha deve ter ao menos 8 caracteres'),
    confirm_password: z.string().min(1, 'Confirme a nova senha'),
  })
  .refine((data) => data.new_password === data.confirm_password, {
    message: 'As senhas não coincidem',
    path: ['confirm_password'],
  })

type ProfileFormValues = z.infer<typeof profileSchema>
type PasswordFormValues = z.infer<typeof passwordSchema>

export function ProfilePage() {
  const { user, setUser } = useAuth()
  const [profileStatus, setProfileStatus] = useState<{ kind: 'success' | 'error'; message: string } | null>(null)
  const [passwordStatus, setPasswordStatus] = useState<{ kind: 'success' | 'error'; message: string } | null>(null)

  const profileForm = useForm<ProfileFormValues>({
    resolver: zodResolver(profileSchema),
    values: { name: user?.name ?? '' },
  })

  const passwordForm = useForm<PasswordFormValues>({ resolver: zodResolver(passwordSchema) })

  const onSubmitProfile = async (values: ProfileFormValues) => {
    setProfileStatus(null)
    try {
      const updated = await authApi.updateProfile({ name: values.name })
      setUser(updated)
      setProfileStatus({ kind: 'success', message: 'Perfil atualizado com sucesso.' })
    } catch (error) {
      setProfileStatus({ kind: 'error', message: getErrorMessage(error) })
    }
  }

  const onSubmitPassword = async (values: PasswordFormValues) => {
    setPasswordStatus(null)
    try {
      await authApi.changePassword({ current_password: values.current_password, new_password: values.new_password })
      setPasswordStatus({ kind: 'success', message: 'Senha alterada com sucesso.' })
      passwordForm.reset()
    } catch (error) {
      setPasswordStatus({ kind: 'error', message: getErrorMessage(error, 'Não foi possível alterar a senha.') })
    }
  }

  return (
    <div className="mx-auto flex max-w-2xl flex-col gap-6">
      <div>
        <h1 className="text-2xl font-semibold text-surface-900 dark:text-surface-50">Meu perfil</h1>
        <p className="mt-1 text-sm text-surface-500 dark:text-surface-400">
          Gerencie suas informações pessoais e segurança da conta.
        </p>
      </div>

      <Card className="p-6">
        <h2 className="mb-4 text-base font-semibold text-surface-900 dark:text-surface-50">Informações pessoais</h2>
        <form className="flex flex-col gap-4" onSubmit={profileForm.handleSubmit(onSubmitProfile)} noValidate>
          {profileStatus && <Alert variant={profileStatus.kind === 'success' ? 'success' : 'error'}>{profileStatus.message}</Alert>}
          <Input label="Nome" error={profileForm.formState.errors.name?.message} {...profileForm.register('name')} />
          <Input label="E-mail" value={user?.email ?? ''} disabled />
          <div>
            <Button type="submit" isLoading={profileForm.formState.isSubmitting}>
              Salvar alterações
            </Button>
          </div>
        </form>
      </Card>

      <Card className="p-6">
        <h2 className="mb-4 text-base font-semibold text-surface-900 dark:text-surface-50">Alterar senha</h2>
        <form className="flex flex-col gap-4" onSubmit={passwordForm.handleSubmit(onSubmitPassword)} noValidate>
          {passwordStatus && <Alert variant={passwordStatus.kind === 'success' ? 'success' : 'error'}>{passwordStatus.message}</Alert>}
          <Input
            label="Senha atual"
            type="password"
            autoComplete="current-password"
            error={passwordForm.formState.errors.current_password?.message}
            {...passwordForm.register('current_password')}
          />
          <Input
            label="Nova senha"
            type="password"
            autoComplete="new-password"
            error={passwordForm.formState.errors.new_password?.message}
            {...passwordForm.register('new_password')}
          />
          <Input
            label="Confirmar nova senha"
            type="password"
            autoComplete="new-password"
            error={passwordForm.formState.errors.confirm_password?.message}
            {...passwordForm.register('confirm_password')}
          />
          <div>
            <Button type="submit" variant="secondary" isLoading={passwordForm.formState.isSubmitting}>
              Alterar senha
            </Button>
          </div>
        </form>
      </Card>
    </div>
  )
}
