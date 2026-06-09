import { type SelectHTMLAttributes, forwardRef } from 'react'

import { clsx } from 'clsx'

interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  label?: string
  error?: string
}

export const Select = forwardRef<HTMLSelectElement, SelectProps>(function Select(
  { label, error, id, className, children, ...rest },
  ref,
) {
  const selectId = id ?? rest.name

  return (
    <div className="flex flex-col gap-1.5">
      {label && (
        <label htmlFor={selectId} className="text-sm font-medium text-surface-700 dark:text-surface-200">
          {label}
        </label>
      )}
      <select
        ref={ref}
        id={selectId}
        className={clsx(
          'h-11 rounded-lg border bg-white px-3.5 text-sm text-surface-900 outline-none transition-colors',
          'focus:border-brand-500 focus:ring-2 focus:ring-brand-500/20',
          'dark:bg-surface-800 dark:text-surface-50',
          error ? 'border-red-400 focus:border-red-500 focus:ring-red-500/20' : 'border-surface-200 dark:border-surface-700',
          className,
        )}
        {...rest}
      >
        {children}
      </select>
      {error && <p className="text-xs text-red-500">{error}</p>}
    </div>
  )
})
