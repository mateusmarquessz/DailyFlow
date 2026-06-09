import { type ReactNode, useEffect } from 'react'

import { X } from 'lucide-react'

import { Card } from '@/components/ui/Card'

interface ModalProps {
  open: boolean
  onClose: () => void
  title: string
  children: ReactNode
}

export function Modal({ open, onClose, title, children }: ModalProps) {
  useEffect(() => {
    if (!open) return
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') onClose()
    }
    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [open, onClose])

  if (!open) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <button
        type="button"
        aria-label="Fechar"
        className="absolute inset-0 bg-surface-950/40 backdrop-blur-sm"
        onClick={onClose}
      />
      <Card className="relative z-10 max-h-[90vh] w-full max-w-lg overflow-y-auto p-6">
        <div className="mb-5 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-surface-900 dark:text-surface-50">{title}</h2>
          <button
            type="button"
            onClick={onClose}
            aria-label="Fechar modal"
            className="rounded-lg p-1.5 text-surface-400 transition-colors hover:bg-surface-100 hover:text-surface-700 dark:hover:bg-surface-800 dark:hover:text-surface-200"
          >
            <X className="size-5" />
          </button>
        </div>
        {children}
      </Card>
    </div>
  )
}
