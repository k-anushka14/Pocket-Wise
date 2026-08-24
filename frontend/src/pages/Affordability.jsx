import { useState } from 'react'
import Layout from '../components/Layout'
import { checkAffordability } from '../api/affordability'
import { EXPENSE_CATEGORIES, formatCurrency, toLabel } from '../utils/constants'

const VERDICT_STYLES = {
  yes: { bg: 'bg-emerald-50 dark:bg-emerald-950', border: 'border-emerald-200 dark:border-emerald-900', text: 'text-emerald-700 dark:text-emerald-300', emoji: '🟢', label: 'You can afford this' },
  risky: { bg: 'bg-amber-50 dark:bg-amber-950', border: 'border-amber-200 dark:border-amber-900', text: 'text-amber-700 dark:text-amber-300', emoji: '🟡', label: 'You can afford this, with caveats' },
  no: { bg: 'bg-red-50 dark:bg-red-950', border: 'border-red-200 dark:border-red-900', text: 'text-red-700 dark:text-red-300', emoji: '🔴', label: "You can't afford this right now" },
}

export default function Affordability() {
  const [itemName, setItemName] = useState('')
  const [amount, setAmount] = useState('')
  const [category, setCategory] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function handleSubmit(e) {
    e.preventDefault()
    setLoading(true)
    setError('')
    setResult(null)
    try {
      const res = await checkAffordability({
        item_name: itemName,
        amount: Number(amount),
        category: category || undefined,
      })
      setResult(res)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const style = result ? VERDICT_STYLES[result.verdict] : null

  return (
    <Layout>
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-slate-900 dark:text-white">Can I Afford This?</h1>
        <p className="text-sm text-slate-500 dark:text-slate-400">
          Check a purchase against your balance, upcoming bills, budgets, and goals.
        </p>
      </div>

      <div className="max-w-lg space-y-4">
        <form onSubmit={handleSubmit} className="rounded-2xl bg-white p-5 shadow-sm dark:bg-slate-900">
          <div className="mb-3">
            <label className="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300">What do you want to buy?</label>
            <input
              required
              value={itemName}
              onChange={(e) => setItemName(e.target.value)}
              placeholder="New shoes"
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm dark:border-slate-700 dark:bg-slate-800 dark:text-white"
            />
          </div>
          <div className="mb-3 grid grid-cols-2 gap-3">
            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300">Amount (₹)</label>
              <input
                type="number" step="0.01" min="0.01" required
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm dark:border-slate-700 dark:bg-slate-800 dark:text-white"
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300">Category (optional)</label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm dark:border-slate-700 dark:bg-slate-800 dark:text-white"
              >
                <option value="">None</option>
                {EXPENSE_CATEGORIES.map((c) => <option key={c} value={c}>{toLabel(c)}</option>)}
              </select>
            </div>
          </div>
          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-lg bg-slate-900 py-2 text-sm font-medium text-white hover:bg-slate-800 disabled:opacity-50 dark:bg-white dark:text-slate-900"
          >
            {loading ? 'Checking…' : 'Check affordability'}
          </button>
        </form>

        {error && <p className="text-sm text-red-500">{error}</p>}

        {result && (
          <div className={`rounded-2xl border p-5 ${style.bg} ${style.border}`}>
            <p className={`mb-1 text-lg font-semibold ${style.text}`}>
              {style.emoji} {style.label}
            </p>
            <div className="mb-3 grid grid-cols-2 gap-3 text-sm">
              <div>
                <p className="text-slate-500 dark:text-slate-400">Current balance</p>
                <p className="font-medium text-slate-900 dark:text-white">{formatCurrency(result.current_balance)}</p>
              </div>
              <div>
                <p className="text-slate-500 dark:text-slate-400">After this purchase</p>
                <p className="font-medium text-slate-900 dark:text-white">{formatCurrency(result.after_purchase_balance)}</p>
              </div>
            </div>
            <ul className="space-y-1.5">
              {result.explanation.map((line, i) => (
                <li key={i} className={`text-sm ${style.text}`}>• {line}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </Layout>
  )
}
