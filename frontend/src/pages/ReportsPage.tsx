import { useState } from 'react'

import { useQuery } from '@tanstack/react-query'
import { format, parseISO } from 'date-fns'
import { ptBR } from 'date-fns/locale'
import { CheckCircle2, FileSpreadsheet, FileText, ListChecks, Repeat, Target } from 'lucide-react'
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

import { reportsApi } from '@/api/reports'
import { Alert } from '@/components/ui/Alert'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { useTheme } from '@/context/ThemeContext'
import { getErrorMessage } from '@/lib/errors'
import type { ReportExportFormat, ReportPeriod } from '@/types/report'

const PERIODS: { value: ReportPeriod; label: string }[] = [
  { value: 'daily', label: 'Diário' },
  { value: 'weekly', label: 'Semanal' },
  { value: 'monthly', label: 'Mensal' },
]

function downloadBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  link.remove()
  URL.revokeObjectURL(url)
}

export function ReportsPage() {
  const { theme } = useTheme()
  const [period, setPeriod] = useState<ReportPeriod>('weekly')
  const [exportingFormat, setExportingFormat] = useState<ReportExportFormat | null>(null)
  const [exportError, setExportError] = useState<string | null>(null)

  const { data: summary, isLoading, isError } = useQuery({
    queryKey: ['reports-summary', period],
    queryFn: () => reportsApi.summary({ period }),
  })

  const handleExport = async (exportFormat: ReportExportFormat) => {
    setExportError(null)
    setExportingFormat(exportFormat)
    try {
      const { blob, filename } = await reportsApi.export({ period, format: exportFormat })
      downloadBlob(blob, filename)
    } catch (error) {
      setExportError(getErrorMessage(error, 'Não foi possível exportar o relatório.'))
    } finally {
      setExportingFormat(null)
    }
  }

  const statCards = [
    {
      label: 'Tarefas concluídas',
      value: summary ? `${summary.tasks_completed}/${summary.tasks_due}` : '—',
      icon: ListChecks,
      hint: summary ? `${summary.task_completion_rate.toFixed(0)}% de conclusão no período` : 'Concluídas / com vencimento',
    },
    {
      label: 'Check-ins de hábitos',
      value: summary ? String(summary.habit_checkins) : '—',
      icon: CheckCircle2,
      hint: summary
        ? `${summary.habit_completion_rate.toFixed(0)}% do esperado · ${summary.habits_active} ativo(s)`
        : 'Registros no período',
    },
    {
      label: 'Melhor sequência',
      value: summary ? String(summary.best_streak) : '—',
      icon: Repeat,
      hint: 'Dias seguidos no seu melhor hábito',
    },
    {
      label: 'Metas concluídas',
      value: summary ? String(summary.goals_completed) : '—',
      icon: Target,
      hint: 'Concluídas dentro do período selecionado',
    },
  ]

  const chartData = (summary?.daily_breakdown ?? []).map((entry) => ({
    ...entry,
    label: format(parseISO(entry.date), period === 'monthly' ? 'dd/MM' : 'EEE dd/MM', { locale: ptBR }),
  }))

  const axisColor = theme === 'dark' ? '#94a3b8' : '#64748b'
  const gridColor = theme === 'dark' ? '#1e293b' : '#e2e8f0'

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-surface-900 dark:text-surface-50">Relatórios</h1>
          <p className="mt-1 text-sm text-surface-500 dark:text-surface-400">
            Acompanhe sua produtividade ao longo do tempo e exporte um resumo em PDF ou Excel.
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Button variant="secondary" onClick={() => handleExport('pdf')} isLoading={exportingFormat === 'pdf'}>
            <FileText className="size-4" />
            Exportar PDF
          </Button>
          <Button variant="secondary" onClick={() => handleExport('excel')} isLoading={exportingFormat === 'excel'}>
            <FileSpreadsheet className="size-4" />
            Exportar Excel
          </Button>
        </div>
      </div>

      {isError && <Alert variant="error">Não foi possível carregar o relatório. Tente novamente.</Alert>}
      {exportError && <Alert variant="error">{exportError}</Alert>}

      <div className="flex flex-wrap gap-2">
        {PERIODS.map(({ value, label }) => (
          <button
            key={value}
            type="button"
            onClick={() => setPeriod(value)}
            className={`rounded-full px-4 py-1.5 text-sm font-medium transition-colors ${
              period === value
                ? 'bg-brand-600 text-white'
                : 'bg-surface-100 text-surface-600 hover:bg-surface-200 dark:bg-surface-800 dark:text-surface-300 dark:hover:bg-surface-700'
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      {summary && (
        <p className="text-sm text-surface-500 dark:text-surface-400">
          Período de {format(parseISO(summary.start_date), 'dd/MM/yyyy')} a{' '}
          {format(parseISO(summary.end_date), 'dd/MM/yyyy')}
        </p>
      )}

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
        <h2 className="text-base font-semibold text-surface-900 dark:text-surface-50">Detalhamento diário</h2>
        <p className="mt-1 text-sm text-surface-500 dark:text-surface-400">
          Tarefas concluídas e hábitos registrados em cada dia do período selecionado.
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
    </div>
  )
}
