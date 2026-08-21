import { apiFetch } from './client'

export const listIncome = () => apiFetch('/income')

export const createIncome = (payload) =>
  apiFetch('/income', { method: 'POST', body: JSON.stringify(payload) })

export const updateIncome = (id, payload) =>
  apiFetch(`/income/${id}`, { method: 'PUT', body: JSON.stringify(payload) })

export const deleteIncome = (id) =>
  apiFetch(`/income/${id}`, { method: 'DELETE' })
