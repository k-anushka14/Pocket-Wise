import { apiFetch } from './client'

export function listTransactions(filters = {}) {
  const params = new URLSearchParams()
  Object.entries(filters).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      params.set(key, value)
    }
  })
  const query = params.toString()
  return apiFetch(`/transactions${query ? `?${query}` : ''}`)
}

export const createTransaction = (payload) =>
  apiFetch('/transactions', { method: 'POST', body: JSON.stringify(payload) })

export const updateTransaction = (id, payload) =>
  apiFetch(`/transactions/${id}`, { method: 'PUT', body: JSON.stringify(payload) })

export const deleteTransaction = (id) =>
  apiFetch(`/transactions/${id}`, { method: 'DELETE' })
