import { describe, it, expect } from 'vitest'
import { calculateEvenSplit } from './split'

describe('calculateEvenSplit', () => {
  it('divides by group size INCLUDING yourself, not just other participants', () => {
    // Regression test for the real bug: splitting ₹800 with 1 other
    // person used to return 800 (divided by 1) instead of 400 (divided by 2).
    expect(calculateEvenSplit(800, 1)).toBe(400)
  })

  it('splits a pizza between 3 other people (4 total) correctly', () => {
    expect(calculateEvenSplit(800, 3)).toBe(200)
  })

  it('rounds to 2 decimal places', () => {
    expect(calculateEvenSplit(100, 2)).toBe(33.33)
  })

  it('returns 0 when there are no other participants', () => {
    expect(calculateEvenSplit(500, 0)).toBe(0)
  })

  it('returns 0 when total amount is falsy', () => {
    expect(calculateEvenSplit(0, 2)).toBe(0)
    expect(calculateEvenSplit(null, 2)).toBe(0)
  })
})
