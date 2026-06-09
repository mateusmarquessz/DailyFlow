import { useState } from 'react'

import {
  LayoutDashboard,
  ListChecks,
  Repeat,
  Calendar,
  Target,
  BarChart3,
  Trophy,
  Settings,
  Menu,
  X,
  Sun,
  Moon,
  LogOut,
} from 'lucide-react'
import { NavLink, Outlet, useNavigate } from 'react-router-dom'

import { useAuth } from '@/context/AuthContext'
import { useTheme } from '@/context/ThemeContext'
import { clsx } from 'clsx'

const NAV_ITEMS = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/tasks', label: 'Tarefas', icon: ListChecks },
  { to: '/habits', label: 'Hábitos', icon: Repeat },
  { to: '/calendar', label: 'Calendário', icon: Calendar },
  { to: '/goals', label: 'Metas', icon: Target },
  { to: '/reports', label: 'Relatórios', icon: BarChart3 },
  { to: '/achievements', label: 'Conquistas', icon: Trophy },
  { to: '/settings', label: 'Configurações', icon: Settings },
]

export function AppLayout() {
  const { user, logout } = useAuth()
  const { theme, toggleTheme } = useTheme()
  const navigate = useNavigate()
  const [isSidebarOpen, setSidebarOpen] = useState(false)

  const handleLogout = async () => {
    await logout()
    navigate('/login', { replace: true })
  }

  return (
    <div className="flex min-h-svh bg-surface-50 dark:bg-surface-950">
      {isSidebarOpen && (
        <button
          aria-label="Fechar menu"
          className="fixed inset-0 z-30 bg-black/40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      <aside
        className={clsx(
          'fixed inset-y-0 left-0 z-40 flex w-64 shrink-0 flex-col border-r border-surface-200 bg-white p-4 transition-transform',
          'dark:border-surface-800 dark:bg-surface-900',
          'lg:static lg:translate-x-0',
          isSidebarOpen ? 'translate-x-0' : '-translate-x-full',
        )}
      >
        <div className="mb-6 flex items-center justify-between px-2">
          <div className="flex items-center gap-2">
            <div className="flex size-9 items-center justify-center rounded-xl bg-brand-600 text-sm font-bold text-white">
              DF
            </div>
            <span className="text-lg font-semibold text-surface-900 dark:text-surface-50">DailyFlow</span>
          </div>
          <button
            aria-label="Fechar menu"
            className="rounded-md p-1.5 text-surface-500 hover:bg-surface-100 dark:hover:bg-surface-800 lg:hidden"
            onClick={() => setSidebarOpen(false)}
          >
            <X className="size-5" />
          </button>
        </div>

        <nav className="flex flex-1 flex-col gap-1">
          {NAV_ITEMS.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              onClick={() => setSidebarOpen(false)}
              className={({ isActive }) =>
                clsx(
                  'flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors',
                  isActive
                    ? 'bg-brand-50 text-brand-700 dark:bg-brand-900/30 dark:text-brand-300'
                    : 'text-surface-600 hover:bg-surface-100 dark:text-surface-300 dark:hover:bg-surface-800',
                )
              }
            >
              <Icon className="size-[18px]" />
              {label}
            </NavLink>
          ))}
        </nav>

        <div className="mt-4 flex items-center gap-3 rounded-lg border border-surface-200 p-3 dark:border-surface-800">
          <div className="flex size-9 items-center justify-center rounded-full bg-brand-100 text-sm font-semibold text-brand-700 dark:bg-brand-900/40 dark:text-brand-300">
            {user?.name?.charAt(0).toUpperCase() ?? '?'}
          </div>
          <div className="min-w-0 flex-1">
            <p className="truncate text-sm font-medium text-surface-900 dark:text-surface-100">{user?.name}</p>
            <p className="truncate text-xs text-surface-500 dark:text-surface-400">{user?.email}</p>
          </div>
          <button
            aria-label="Sair"
            title="Sair"
            onClick={handleLogout}
            className="rounded-md p-1.5 text-surface-400 hover:bg-surface-100 hover:text-red-600 dark:hover:bg-surface-800"
          >
            <LogOut className="size-[18px]" />
          </button>
        </div>
      </aside>

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="flex h-16 items-center justify-between border-b border-surface-200 bg-white px-4 dark:border-surface-800 dark:bg-surface-900 lg:px-6">
          <button
            aria-label="Abrir menu"
            className="rounded-md p-2 text-surface-500 hover:bg-surface-100 dark:hover:bg-surface-800 lg:hidden"
            onClick={() => setSidebarOpen(true)}
          >
            <Menu className="size-5" />
          </button>
          <div className="hidden lg:block" />
          <button
            aria-label="Alternar tema"
            title="Alternar tema claro/escuro"
            onClick={toggleTheme}
            className="rounded-lg border border-surface-200 p-2 text-surface-600 transition-colors hover:bg-surface-100 dark:border-surface-700 dark:text-surface-300 dark:hover:bg-surface-800"
          >
            {theme === 'dark' ? <Sun className="size-[18px]" /> : <Moon className="size-[18px]" />}
          </button>
        </header>

        <main className="flex-1 overflow-y-auto p-4 lg:p-8">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
