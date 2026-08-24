import { apiFetch } from './client'

export const checkAffordability = (payload) =>
  apiFetch('/ai/affordability-check', { method: 'POST', body: JSON.stringify(payload) })
