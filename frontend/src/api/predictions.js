import { apiFetch } from './client'

export const getPredictions = () => apiFetch('/predictions')
