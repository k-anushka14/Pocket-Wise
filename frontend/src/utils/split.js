/**
 * Pure math for splitting a bill evenly. Extracted so it's independently
 * testable -- this exact calculation (dividing by group size INCLUDING
 * yourself, not just the number of other participants) was the source of
 * a real bug: with 1 other participant on the form, the old code divided
 * by 1 instead of 2 and handed back the full amount instead of a half share.
 */
export function calculateEvenSplit(totalAmount, otherParticipantsCount) {
  if (!totalAmount || otherParticipantsCount <= 0) return 0
  const totalPeople = otherParticipantsCount + 1 // + yourself
  return Number((totalAmount / totalPeople).toFixed(2))
}
