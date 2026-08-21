import { apiFetch } from './client'

export const listBudgets = (month) =>
  apiFetch(`/budgets${month ? `?month=${month}` : ''}`)

export const createBudget = (payload) =>
  apiFetch('/budgets', { method: 'POST', body: JSON.stringify(payload) })

export const updateBudget = (id, payload) =>
  apiFetch(`/budgets/${id}`, { method: 'PUT', body: JSON.stringify(payload) })

export const deleteBudget = (id) =>
  apiFetch(`/budgets/${id}`, { method: 'DELETE' })
