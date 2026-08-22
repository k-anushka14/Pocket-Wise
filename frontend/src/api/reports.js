import { apiFetch } from './client'

export const getMonthlyReport = (month) =>
  apiFetch(`/reports/monthly${month ? `?month=${month}` : ''}`)
