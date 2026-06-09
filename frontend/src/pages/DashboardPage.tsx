import { useQuery } from '@tanstack/react-query'
import { format, parseISO } from 'date-fns'
import { ptBR } from 'date-fns/locale'
import { CheckCircle2, Flame, ListChecks, Target } from 'lucide-react'
import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

import { dashboardApi } from '@/api/dashboard'
import { Alert } from '@/components/ui/Alert'
import { Card } from '@/components/ui/Card'
import { useAuth } from '@/context/AuthContext'
import { useTheme } from '@/context/ThemeContext'

export function DashboardPage() {
  const { user } = useAuth()
  const { theme } = useTheme()
  const firstName = user?.name?.split(' ')[0] ?? ''

  const { data: stats, isLoading, isError } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: () => dashboardApi.stats(),
  })

  const statCards = [
    {
      label: 'Tarefas de hoje',
      value: stats ? `${stats.tasks_completed_today}/${stats.tasks_due_today}` : '—',
      icon: ListChecks,
      hint: 'Concluídas / com vencimento hoje',
    },
    {
      label: 'Hábitos concluídos',
      value: stats ? `${stats.habits_completed_today}/${stats.habits_total}` : '—',
      icon: CheckCircle2,
      hint: 'Check-ins de hoje',
    },
    {
      label: 'Sequência atual',
      value: stats ? String(stats.best_current_streak) : '—',
      icon: Flame,
      hint: stats?.best_current_streak ? 'Dias seguidos no seu melhor hábito' : 'Comece um hábito para criar uma sequência',
    },
    {
      label: 'Metas em andamento',
      value: stats ? String(stats.goals_in_progress) : '—',
      icon: Target,
      hint: 'Em breve: metas semanais, mensais e anuais',
    },
  ]

  const chartData = (stats?.weekly_completions ?? []).map((entry) => ({
    ...entry,
    label: format(parseISO(entry.date), 'EEE dd/MM', { locale: ptBR }),
  }))

  const axisColor = theme === 'dark' ? '#94a3b8' : '#64748b'
  const gridColor = theme === 'dark' ? '#1e293b' : '#e2e8f0'

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-semibold text-surface-900 dark:text-surface-50">Olá, {firstName} 👋</h1>
        <p className="mt-1 text-sm text-surface-500 dark:text-surface-400">
          Aqui está um resumo da sua rotina de hoje e da sua semana.
        </p>
      </div>

      {isError && <Alert variant="error">Não foi possível carregar suas estatísticas. Tente novamente.</Alert>}

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {statCards.map(({ label, value, icon: Icon, hint }) => (
          <Card key={label} className="p-5">
            <div className="flex items-center justify-between">
              <p className="text-sm font-medium text-surface-500 dark:text-surface-400">{label}</p>
              <div className="flex size-9 items-center justify-center rounded-lg bg-brand-50 text-brand-600 dark:bg-brand-900/30 dark:text-brand-300">
                <Icon className="size-[18px]" />
              </div>
            </div>
            <p className="mt-3 text-3xl font-semibold text-surface-900 dark:text-surface-50">
              {isLoading ? '…' : value}
            </p>
            <p className="mt-1 text-xs text-surface-400 dark:text-surface-500">{hint}</p>
          </Card>
        ))}
      </div>

      <Card className="p-6">
        <h2 className="text-base font-semibold text-surface-900 dark:text-surface-50">Sua semana</h2>
        <p className="mt-1 text-sm text-surface-500 dark:text-surface-400">
          Tarefas concluídas e hábitos registrados nos últimos 7 dias.
        </p>
        <div className="mt-4 h-72 w-full">
          {isLoading ? (
            <div className="flex h-full items-center justify-center text-sm text-surface-400 dark:text-surface-500">
              Carregando gráfico…
            </div>
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} barGap={6}>
                <CartesianGrid strokeDasharray="3 3" stroke={gridColor} vertical={false} />
                <XAxis dataKey="label" stroke={axisColor} fontSize={12} tickLine={false} axisLine={false} />
                <YAxis stroke={axisColor} fontSize={12} tickLine={false} axisLine={false} allowDecimals={false} width={28} />
                <Tooltip
                  cursor={{ fill: gridColor, opacity: 0.4 }}
                  contentStyle={{
                    borderRadius: 12,
                    border: 'none',
                    backgroundColor: theme === 'dark' ? '#1e293b' : '#ffffff',
                    color: theme === 'dark' ? '#f8fafc' : '#0f172a',
                    fontSize: 13,
                  }}
                />
                <Legend wrapperStyle={{ fontSize: 13 }} />
                <Bar dataKey="tasks_completed" name="Tarefas concluídas" fill="#6366f1" radius={[6, 6, 0, 0]} />
                <Bar dataKey="habits_completed" name="Hábitos registrados" fill="#22c55e" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>
      </Card>

      <Card className="p-6">
        <h2 className="text-base font-semibold text-surface-900 dark:text-surface-50">Próximos passos</h2>
        <ul className="mt-4 flex flex-col gap-3 text-sm text-surface-600 dark:text-surface-300">
          <li className="flex items-start gap-2">
            <span className="mt-1 size-1.5 shrink-0 rounded-full bg-brand-500" />
            Crie tarefas com prioridade, data e recorrência na seção <strong>Tarefas</strong>.
          </li>
          <li className="flex items-start gap-2">
            <span className="mt-1 size-1.5 shrink-0 rounded-full bg-brand-500" />
            Cadastre hábitos diários e acompanhe sua sequência (streak) em <strong>Hábitos</strong>.
          </li>
          <li className="flex items-start gap-2">
            <span className="mt-1 size-1.5 shrink-0 rounded-full bg-brand-500" />
            Conecte sua conta ao bot do Telegram em <strong>Configurações</strong> para receber lembretes automáticos.
          </li>
        </ul>
      </Card>
    </div>
  )
}
