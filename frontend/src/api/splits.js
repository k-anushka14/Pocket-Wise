import { apiFetch } from './client'

export const listSplitExpenses = () => apiFetch('/split-expenses')

export const createSplitExpense = (payload) =>
  apiFetch('/split-expenses', { method: 'POST', body: JSON.stringify(payload) })

export const markParticipantPaid = (splitId, participantId) =>
  apiFetch(`/split-expenses/${splitId}/participants/${participantId}/mark-paid`, { method: 'PUT' })

export const deleteSplitExpense = (id) =>
  apiFetch(`/split-expenses/${id}`, { method: 'DELETE' })
