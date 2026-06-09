import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from 'react'

import { useAuth } from '@/context/AuthContext'
import { authApi } from '@/api/auth'
import type { ThemePreference } from '@/types/auth'

const STORAGE_KEY = 'dailyflow.theme'

interface ThemeContextValue {
  theme: ThemePreference
  toggleTheme: () => void
  setTheme: (theme: ThemePreference) => void
}

const ThemeContext = createContext<ThemeContextValue | null>(null)

function getInitialTheme(): ThemePreference {
  const stored = localStorage.getItem(STORAGE_KEY)
  if (stored === 'light' || stored === 'dark') return stored
  return window.matchMedia?.('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setThemeState] = useState<ThemePreference>(getInitialTheme)
  const { user, isAuthenticated, setUser } = useAuth()

  useEffect(() => {
    const root = document.documentElement
    root.classList.toggle('dark', theme === 'dark')
    localStorage.setItem(STORAGE_KEY, theme)
  }, [theme])

  // Once we know who the user is, respect their saved preference.
  useEffect(() => {
    if (user?.theme_preference && user.theme_preference !== theme) {
      setThemeState(user.theme_preference)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user?.id])

  const persistTheme = (next: ThemePreference) => {
    setThemeState(next)
    if (isAuthenticated) {
      authApi
        .updateProfile({ theme_preference: next })
        .then((updated) => setUser(updated))
        .catch(() => undefined)
    }
  }

  const value = useMemo<ThemeContextValue>(
    () => ({
      theme,
      toggleTheme: () => persistTheme(theme === 'light' ? 'dark' : 'light'),
      setTheme: persistTheme,
    }),
    [theme, isAuthenticated],
  )

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>
}

export function useTheme(): ThemeContextValue {
  const context = useContext(ThemeContext)
  if (!context) {
    throw new Error('useTheme deve ser usado dentro de um ThemeProvider')
  }
  return context
}
