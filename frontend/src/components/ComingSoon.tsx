import type { LucideIcon } from 'lucide-react'

import { Card } from '@/components/ui/Card'

export function ComingSoon({ icon: Icon, title, description }: { icon: LucideIcon; title: string; description: string }) {
  return (
    <div>
      <h1 className="text-2xl font-semibold text-surface-900 dark:text-surface-50">{title}</h1>
      <Card className="mt-6 flex flex-col items-center justify-center gap-3 px-6 py-16 text-center">
        <div className="flex size-14 items-center justify-center rounded-2xl bg-brand-50 text-brand-600 dark:bg-brand-900/30 dark:text-brand-300">
          <Icon className="size-7" />
        </div>
        <h2 className="text-lg font-semibold text-surface-900 dark:text-surface-50">Em construção</h2>
        <p className="max-w-md text-sm text-surface-500 dark:text-surface-400">{description}</p>
      </Card>
    </div>
  )
}
