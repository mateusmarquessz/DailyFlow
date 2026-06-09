import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from 'react'

import { authApi } from '@/api/auth'
import { tokenStorage } from '@/api/client'
import type { LoginPayload, RegisterPayload, User } from '@/types/auth'

interface AuthContextValue {
  user: User | null
  isLoading: boolean
  isAuthenticated: boolean
  login: (payload: LoginPayload) => Promise<User>
  register: (payload: RegisterPayload) => Promise<User>
  logout: () => Promise<void>
  setUser: (user: User) => void
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const bootstrap = async () => {
      if (!tokenStorage.getAccessToken()) {
        setIsLoading(false)
        return
      }
      try {
        const me = await authApi.me()
        setUser(me)
      } catch {
        tokenStorage.clear()
      } finally {
        setIsLoading(false)
      }
    }
    void bootstrap()
  }, [])

  const login = async (payload: LoginPayload) => {
    const response = await authApi.login(payload)
    tokenStorage.setTokens(response.access_token, response.refresh_token)
    setUser(response.user)
    return response.user
  }

  const register = async (payload: RegisterPayload) => {
    const response = await authApi.register(payload)
    tokenStorage.setTokens(response.access_token, response.refresh_token)
    setUser(response.user)
    return response.user
  }

  const logout = async () => {
    const refreshToken = tokenStorage.getRefreshToken()
    tokenStorage.clear()
    setUser(null)
    if (refreshToken) {
      try {
        await authApi.logout(refreshToken)
      } catch {
        // best-effort: token is already cleared client-side
      }
    }
  }

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      isLoading,
      isAuthenticated: Boolean(user),
      login,
      register,
      logout,
      setUser,
    }),
    [user, isLoading],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth deve ser usado dentro de um AuthProvider')
  }
  return context
}
