import { apiFetch } from './client'

export const categorizeExpense = (description) =>
  apiFetch('/ai/categorize-expense', {
    method: 'POST',
    body: JSON.stringify({ description }),
  })

export const askAssistant = (question) =>
  apiFetch('/ai/assistant', {
    method: 'POST',
    body: JSON.stringify({ question }),
  })
