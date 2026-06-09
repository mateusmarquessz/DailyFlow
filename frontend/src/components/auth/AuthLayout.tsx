import { type ReactNode } from 'react'

import { Card } from '@/components/ui/Card'

export function AuthLayout({
  title,
  subtitle,
  children,
}: {
  title: string
  subtitle?: string
  children: ReactNode
}) {
  return (
    <div className="flex min-h-svh items-center justify-center bg-surface-50 px-4 py-10 dark:bg-surface-950">
      <div className="w-full max-w-md">
        <div className="mb-8 text-center">
          <div className="mx-auto mb-4 flex size-12 items-center justify-center rounded-2xl bg-brand-600 text-xl font-bold text-white">
            DF
          </div>
          <h1 className="text-2xl font-semibold text-surface-900 dark:text-surface-50">{title}</h1>
          {subtitle && <p className="mt-1 text-sm text-surface-500 dark:text-surface-400">{subtitle}</p>}
        </div>
        <Card className="p-6 sm:p-8">{children}</Card>
      </div>
    </div>
  )
}
