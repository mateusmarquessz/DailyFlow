import { type HTMLAttributes } from 'react'

import { clsx } from 'clsx'

export function Card({ className, ...rest }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={clsx(
        'rounded-2xl border border-surface-200 bg-white shadow-sm',
        'dark:border-surface-800 dark:bg-surface-900',
        className,
      )}
      {...rest}
    />
  )
}
