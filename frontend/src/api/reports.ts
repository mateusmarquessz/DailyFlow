import { apiClient } from '@/api/client'
import type { ReportExportFormat, ReportPeriod, ReportSummary } from '@/types/report'

interface ReportQuery {
  period: ReportPeriod
  reference_date?: string
}

function extractFilename(contentDisposition: string | undefined, fallback: string): string {
  const match = contentDisposition?.match(/filename="?([^"]+)"?/)
  return match?.[1] ?? fallback
}

export const reportsApi = {
  summary: (query: ReportQuery) =>
    apiClient.get<ReportSummary>('/reports/summary', { params: query }).then((res) => res.data),

  export: async (query: ReportQuery & { format: ReportExportFormat }) => {
    const response = await apiClient.get<Blob>('/reports/export', { params: query, responseType: 'blob' })
    const extension = query.format === 'pdf' ? 'pdf' : 'xlsx'
    return {
      blob: response.data,
      filename: extractFilename(response.headers['content-disposition'], `dailyflow-relatorio.${extension}`),
    }
  },
}
