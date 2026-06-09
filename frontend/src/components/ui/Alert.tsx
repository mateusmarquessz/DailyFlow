import { type ReactNode } from 'react'

import { clsx } from 'clsx'

type Variant = 'error' | 'success' | 'info'

const VARIANT_CLASSES: Record<Variant, string> = {
  error: 'bg-red-50 text-red-700 border-red-200 dark:bg-red-950/40 dark:text-red-300 dark:border-red-900',
  success:
    'bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-300 dark:border-emerald-900',
  info: 'bg-brand-50 text-brand-700 border-brand-200 dark:bg-brand-950/40 dark:text-brand-300 dark:border-brand-900',
}

export function Alert({ variant = 'info', children }: { variant?: Variant; children: ReactNode }) {
  return (
    <div role="alert" className={clsx('rounded-lg border px-4 py-3 text-sm', VARIANT_CLASSES[variant])}>
      {children}
    </div>
  )
}
