import { apiFetch } from './client'

export const listGoals = () => apiFetch('/goals')

export const createGoal = (payload) =>
  apiFetch('/goals', { method: 'POST', body: JSON.stringify(payload) })

export const updateGoal = (id, payload) =>
  apiFetch(`/goals/${id}`, { method: 'PUT', body: JSON.stringify(payload) })

export const contributeToGoal = (id, amount) =>
  apiFetch(`/goals/${id}/contribute`, { method: 'POST', body: JSON.stringify({ amount }) })

export const deleteGoal = (id) =>
  apiFetch(`/goals/${id}`, { method: 'DELETE' })
