import { describe, it, expect } from 'vitest'
import { toLabel, formatCurrency } from './constants'

describe('toLabel', () => {
  it('converts snake_case to Title Case', () => {
    expect(toLabel('personal_care')).toBe('Personal Care')
  })

  it('handles single words', () => {
    expect(toLabel('food')).toBe('Food')
  })
})

describe('formatCurrency', () => {
  it('formats a number as INR with no decimals', () => {
    expect(formatCurrency(1500)).toBe('₹1,500')
  })

  it('formats zero correctly', () => {
    expect(formatCurrency(0)).toBe('₹0')
  })

  it('formats large numbers with Indian-style comma grouping', () => {
    expect(formatCurrency(150000)).toBe('₹1,50,000')
  })
})
