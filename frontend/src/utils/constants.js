// Kept in sync with backend/app/schemas/enums.py -- if you add a category
// or payment method on the backend, add it here too.

export const EXPENSE_CATEGORIES = [
  'food', 'cafe', 'transport', 'education', 'shopping', 'entertainment',
  'hostel', 'recharge', 'subscriptions', 'personal_care', 'health',
  'gifts', 'groceries', 'other',
]

export const PAYMENT_METHODS = [
  'upi', 'cash', 'debit_card', 'credit_card', 'bank_transfer', 'other',
]

export const EXPENSE_TYPES = ['need', 'want']

export const INCOME_SOURCES = [
  'pocket_money', 'weekly_allowance', 'scholarship', 'internship_stipend',
  'freelance', 'gift', 'other',
]

export const RECURRENCE_FREQUENCIES = ['weekly', 'monthly', 'yearly']

export function toLabel(value) {
  return value
    .split('_')
    .map((w) => w[0].toUpperCase() + w.slice(1))
    .join(' ')
}

export function formatCurrency(amount) {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(amount)
}
