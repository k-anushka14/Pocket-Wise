import { useEffect, useState } from 'react'
import { Plus, Trash2, CheckCircle2 } from 'lucide-react'
import Layout from '../components/Layout'
import Modal from '../components/Modal'
import Toast from '../components/Toast'
import EmptyState from '../components/EmptyState'
import ErrorState from '../components/ErrorState'
import LoadingState from '../components/LoadingState'
import {
  listRecurringExpenses, createRecurringExpense, deleteRecurringExpense, markRecurringPaid,
} from '../api/recurring'
import { EXPENSE_CATEGORIES, PAYMENT_METHODS, RECURRENCE_FREQUENCIES, formatCurrency, toLabel } from '../utils/constants'

const EMPTY_FORM = {
  name: '', amount: '', category: 'subscriptions', frequency: 'monthly',
  next_due_date: new Date().toISOString().slice(0, 10),
}

function DueBadge({ expense }) {
  if (expense.is_overdue) {
    return <span className="rounded-full bg-red-100 px-2 py-0.5 text-xs font-medium text-red-700 dark:bg-red-950 dark:text-red-300">Overdue</span>
  }
  if (expense.is_due_soon) {
    return <span className="rounded-full bg-amber-100 px-2 py-0.5 text-xs font-medium text-amber-700 dark:bg-amber-950 dark:text-amber-300">Due in {expense.days_until_due}d</span>
  }
  return <span className="text-xs text-slate-500 dark:text-slate-400">Due in {expense.days_until_due}d</span>
}

export default function RecurringExpenses() {
  const [expenses, setExpenses] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [toast, setToast] = useState(null)

  const [modalOpen, setModalOpen] = useState(false)
  const [form, setForm] = useState(EMPTY_FORM)
  const [saving, setSaving] = useState(false)
  const [payMethod, setPayMethod] = useState('upi')

  async function load() {
    setLoading(true)
    setError('')
    try {
      setExpenses(await listRecurringExpenses())
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  async function handleSubmit(e) {
    e.preventDefault()
    setSaving(true)
    try {
      await createRecurringExpense({ ...form, amount: Number(form.amount) })
      setToast({ message: 'Recurring expense added', variant: 'success' })
      setModalOpen(false)
      setForm(EMPTY_FORM)
      load()
    } catch (err) {
      setToast({ message: err.message, variant: 'error' })
    } finally {
      setSaving(false)
    }
  }

  async function handleDelete(expense) {
    if (!confirm(`Delete "${expense.name}"?`)) return
    try {
      await deleteRecurringExpense(expense.id)
      setToast({ message: 'Deleted', variant: 'success' })
      load()
    } catch (err) {
      setToast({ message: err.message, variant: 'error' })
    }
  }

  async function handleMarkPaid(expense) {
    try {
      await markRecurringPaid(expense.id, payMethod)
      setToast({ message: `Logged this cycle's ${expense.name} payment`, variant: 'success' })
      load()
    } catch (err) {
      setToast({ message: err.message, variant: 'error' })
    }
  }

  return (
    <Layout>
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-semibold text-slate-900 dark:text-white">Recurring Expenses</h1>
        <button
          onClick={() => setModalOpen(true)}
          className="flex items-center gap-1.5 rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800 dark:bg-white dark:text-slate-900"
        >
          <Plus size={16} /> Add recurring
        </button>
      </div>

      <div className="mb-4 flex items-center gap-2 text-sm">
        <span className="text-slate-500 dark:text-slate-400">Pay via</span>
        <select
          value={payMethod}
          onChange={(e) => setPayMethod(e.target.value)}
          className="rounded-lg border border-slate-300 px-2 py-1 text-sm dark:border-slate-700 dark:bg-slate-900 dark:text-white"
        >
          {PAYMENT_METHODS.map((p) => <option key={p} value={p}>{toLabel(p)}</option>)}
        </select>
        <span className="text-slate-400 dark:text-slate-500">— used when you mark one paid below</span>
      </div>

      {loading && <LoadingState label="Loading recurring expenses…" />}
      {!loading && error && <ErrorState message={error} onRetry={load} />}
      {!loading && !error && expenses.length === 0 && (
        <EmptyState
          title="No recurring expenses set up"
          description="Add subscriptions or hostel fees so PocketWise can remind you before they're due."
          action={
            <button onClick={() => setModalOpen(true)} className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white dark:bg-white dark:text-slate-900">
              Add recurring
            </button>
          }
        />
      )}
      {!loading && !error && expenses.length > 0 && (
        <div className="space-y-2">
          {expenses.map((e) => (
            <div key={e.id} className="flex items-center justify-between rounded-xl bg-white p-4 shadow-sm dark:bg-slate-900">
              <div>
                <p className="font-medium text-slate-900 dark:text-white">{e.name}</p>
                <p className="text-xs text-slate-500 dark:text-slate-400">
                  {toLabel(e.category)} · {toLabel(e.frequency)} · {formatCurrency(e.amount)}
                </p>
              </div>
              <div className="flex items-center gap-3">
                <DueBadge expense={e} />
                <button onClick={() => handleMarkPaid(e)} className="flex items-center gap-1 text-sm text-emerald-600 hover:underline dark:text-emerald-400">
                  <CheckCircle2 size={15} /> Mark paid
                </button>
                <button onClick={() => handleDelete(e)} className="text-slate-400 hover:text-red-600" aria-label="Delete">
                  <Trash2 size={15} />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title="Add recurring expense">
        <form onSubmit={handleSubmit} className="space-y-3">
          <div>
            <label className="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300">Name</label>
            <input
              required
              value={form.name}
              onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm dark:border-slate-700 dark:bg-slate-800 dark:text-white"
              placeholder="Spotify, WiFi, hostel fees…"
            />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300">Amount (₹)</label>
            <input
              type="number" step="0.01" min="0.01" required
              value={form.amount}
              onChange={(e) => setForm((f) => ({ ...f, amount: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm dark:border-slate-700 dark:bg-slate-800 dark:text-white"
            />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300">Category</label>
              <select
                value={form.category}
                onChange={(e) => setForm((f) => ({ ...f, category: e.target.value }))}
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm dark:border-slate-700 dark:bg-slate-800 dark:text-white"
              >
                {EXPENSE_CATEGORIES.map((c) => <option key={c} value={c}>{toLabel(c)}</option>)}
              </select>
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300">Frequency</label>
              <select
                value={form.frequency}
                onChange={(e) => setForm((f) => ({ ...f, frequency: e.target.value }))}
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm dark:border-slate-700 dark:bg-slate-800 dark:text-white"
              >
                {RECURRENCE_FREQUENCIES.map((f) => <option key={f} value={f}>{toLabel(f)}</option>)}
              </select>
            </div>
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300">Next due date</label>
            <input
              type="date" required
              value={form.next_due_date}
              onChange={(e) => setForm((f) => ({ ...f, next_due_date: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm dark:border-slate-700 dark:bg-slate-800 dark:text-white"
            />
          </div>
          <button
            type="submit"
            disabled={saving}
            className="w-full rounded-lg bg-slate-900 py-2 text-sm font-medium text-white hover:bg-slate-800 disabled:opacity-50 dark:bg-white dark:text-slate-900"
          >
            {saving ? 'Saving…' : 'Add recurring expense'}
          </button>
        </form>
      </Modal>

      <Toast message={toast?.message} variant={toast?.variant} onDismiss={() => setToast(null)} />
    </Layout>
  )
}
