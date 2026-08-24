import { apiFetch } from './client'

export const listAchievements = () => apiFetch('/achievements')
