import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { authApi } from '@/api/auth'
import { AuthProvider } from '@/context/AuthContext'
import { LoginPage } from '@/pages/auth/LoginPage'

vi.mock('@/api/auth', () => ({
  authApi: {
    me: vi.fn().mockRejectedValue(new Error('not authenticated')),
    login: vi.fn(),
    register: vi.fn(),
    logout: vi.fn(),
  },
}))

function renderLoginPage() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={['/login']}>
        <AuthProvider>
          <LoginPage />
        </AuthProvider>
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

describe('LoginPage', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  it('shows validation errors when submitting empty form', async () => {
    renderLoginPage()
    const user = userEvent.setup()

    await user.click(await screen.findByRole('button', { name: /entrar/i }))

    expect(await screen.findByText('Informe seu e-mail')).toBeInTheDocument()
    expect(await screen.findByText('Informe sua senha')).toBeInTheDocument()
    expect(authApi.login).not.toHaveBeenCalled()
  })

  it('submits credentials and stores tokens on success', async () => {
    vi.mocked(authApi.login).mockResolvedValue({
      access_token: 'access-123',
      refresh_token: 'refresh-456',
      token_type: 'bearer',
      user: {
        id: 1,
        email: 'mateus@example.com',
        name: 'Mateus',
        avatar_url: null,
        theme_preference: 'light',
        created_at: '2026-01-01T00:00:00Z',
      },
    })

    renderLoginPage()
    const user = userEvent.setup()

    await user.type(screen.getByLabelText('E-mail'), 'mateus@example.com')
    await user.type(screen.getByLabelText('Senha'), 'StrongPass123')
    await user.click(screen.getByRole('button', { name: /entrar/i }))

    await waitFor(() => {
      expect(authApi.login).toHaveBeenCalledWith({ email: 'mateus@example.com', password: 'StrongPass123' })
    })
    expect(localStorage.getItem('dailyflow.access_token')).toBe('access-123')
    expect(localStorage.getItem('dailyflow.refresh_token')).toBe('refresh-456')
  })

  it('shows an error message when credentials are rejected', async () => {
    vi.mocked(authApi.login).mockRejectedValue({
      isAxiosError: true,
      response: { data: { detail: 'E-mail ou senha inválidos.' } },
    })

    renderLoginPage()
    const user = userEvent.setup()

    await user.type(screen.getByLabelText('E-mail'), 'mateus@example.com')
    await user.type(screen.getByLabelText('Senha'), 'WrongPass123')
    await user.click(screen.getByRole('button', { name: /entrar/i }))

    expect(await screen.findByRole('alert')).toHaveTextContent('E-mail ou senha inválidos.')
  })
})
