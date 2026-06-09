import { type InputHTMLAttributes, forwardRef } from 'react'

import { clsx } from 'clsx'

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string
  error?: string
}

export const Input = forwardRef<HTMLInputElement, InputProps>(function Input(
  { label, error, id, className, ...rest },
  ref,
) {
  const inputId = id ?? rest.name

  return (
    <div className="flex flex-col gap-1.5">
      {label && (
        <label htmlFor={inputId} className="text-sm font-medium text-surface-700 dark:text-surface-200">
          {label}
        </label>
      )}
      <input
        ref={ref}
        id={inputId}
        className={clsx(
          'h-11 rounded-lg border bg-white px-3.5 text-sm text-surface-900 outline-none transition-colors',
          'placeholder:text-surface-400 focus:border-brand-500 focus:ring-2 focus:ring-brand-500/20',
          'dark:bg-surface-800 dark:text-surface-50 dark:placeholder:text-surface-500',
          error ? 'border-red-400 focus:border-red-500 focus:ring-red-500/20' : 'border-surface-200 dark:border-surface-700',
          className,
        )}
        {...rest}
      />
      {error && <p className="text-xs text-red-500">{error}</p>}
    </div>
  )
})
