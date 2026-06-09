import { type ReactNode } from 'react'

import { clsx } from 'clsx'

type Tone = 'neutral' | 'brand' | 'success' | 'warning' | 'danger'

const TONE_CLASSES: Record<Tone, string> = {
  neutral: 'bg-surface-100 text-surface-600 dark:bg-surface-800 dark:text-surface-300',
  brand: 'bg-brand-50 text-brand-700 dark:bg-brand-900/30 dark:text-brand-300',
  success: 'bg-emerald-50 text-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-300',
  warning: 'bg-amber-50 text-amber-700 dark:bg-amber-950/40 dark:text-amber-300',
  danger: 'bg-red-50 text-red-700 dark:bg-red-950/40 dark:text-red-300',
}

export function Badge({ tone = 'neutral', children }: { tone?: Tone; children: ReactNode }) {
  return (
    <span className={clsx('inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-medium', TONE_CLASSES[tone])}>
      {children}
    </span>
  )
}
