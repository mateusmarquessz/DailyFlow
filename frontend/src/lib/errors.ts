import { isAxiosError } from 'axios'

export function getErrorMessage(error: unknown, fallback = 'Algo deu errado. Tente novamente.'): string {
  if (isAxiosError(error)) {
    const detail = error.response?.data?.detail
    if (typeof detail === 'string') return detail
  }
  if (error instanceof Error && error.message) return error.message
  return fallback
}
