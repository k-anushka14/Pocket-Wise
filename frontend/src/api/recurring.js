import { apiFetch } from './client'

export const listRecurringExpenses = () => apiFetch('/recurring-expenses')

export const createRecurringExpense = (payload) =>
  apiFetch('/recurring-expenses', { method: 'POST', body: JSON.stringify(payload) })

export const updateRecurringExpense = (id, payload) =>
  apiFetch(`/recurring-expenses/${id}`, { method: 'PUT', body: JSON.stringify(payload) })

export const markRecurringPaid = (id, paymentMethod) =>
  apiFetch(`/recurring-expenses/${id}/mark-paid`, {
    method: 'POST',
    body: JSON.stringify({ payment_method: paymentMethod }),
  })

export const deleteRecurringExpense = (id) =>
  apiFetch(`/recurring-expenses/${id}`, { method: 'DELETE' })
