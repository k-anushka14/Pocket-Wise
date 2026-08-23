import { useEffect, useState, useCallback } from 'react'
import { Plus, Sparkles } from 'lucide-react'
import Layout from '../components/Layout'
import Modal from '../components/Modal'
import Toast from '../components/Toast'
import EmptyState from '../components/EmptyState'
import ErrorState from '../components/ErrorState'
import LoadingState from '../components/LoadingState'
import TransactionTable from '../components/TransactionTable'
import {
  listTransactions,
  createTransaction,
  updateTransaction,
  deleteTransaction,
} from '../api/transactions'
import { categorizeExpense } from '../api/ai'
import { EXPENSE_CATEGORIES, PAYMENT_METHODS, EXPENSE_TYPES, toLabel } from '../utils/constants'

const EMPTY_FORM = {
  amount: '',
  category: 'food',
  description: '',
  date: new Date().toISOString().slice(0, 10),
  payment_method: 'upi',
  type: 'want',
  notes: '',
}

export default function Transactions() {
  const [transactions, setTransactions] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [toast, setToast] = useState(null)

  const [filters, setFilters] = useState({
    search: '',
    category: '',
    payment_method: '',
    type: '',
    sort_by: 'date',
    sort_dir: 'desc',
  })

  const [modalOpen, setModalOpen] = useState(false)
  const [editingId, setEditingId] = useState(null)
  const [form, setForm] = useState(EMPTY_FORM)
  const [saving, setSaving] = useState(false)
  const [categorizing, setCategorizing] = useState(false)

  // Auto-categorize using AI after the user pauses typing (debounced 800ms)
  const tryAICategorize = useCallback(async (description) => {
    if (!description || description.length < 8 || editingId) return
    setCategorizing(true)
    try {
      const result = await categorizeExpense(description)
      if (result.ai_available && result.confidence === 'high') {
        setForm((f) => ({
          ...f,
          category: result.category,
          type: result.type,
          ...(result.amount && !f.amount ? { amount: result.amount } : {}),
        }))
      }
    } catch {
      // Silently ignore -- AI unavailability shouldn't break the form
    } finally {
      setCategorizing(false)
    }
  }, [editingId])

  async function load() {
    setLoading(true)
    setError('')
    try {
      const data = await listTransactions(filters)
      setTransactions(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filters])

  function openAddModal() {
    setEditingId(null)
    setForm(EMPTY_FORM)
    setModalOpen(true)
  }

  function openEditModal(txn) {
    setEditingId(txn.id)
    setForm({
      amount: txn.amount,
      category: txn.category,
      description: txn.description || '',
      date: txn.date,
      payment_method: txn.payment_method,
      type: txn.type,
      notes: txn.notes || '',
    })
    setModalOpen(true)
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setSaving(true)
    try {
      const payload = { ...form, amount: Number(form.amount) }
      if (editingId) {
        await updateTransaction(editingId, payload)
        setToast({ message: 'Transaction updated', variant: 'success' })
      } else {
        await createTransaction(payload)
        setToast({ message: 'Transaction added', variant: 'success' })
      }
      setModalOpen(false)
      load()
    } catch (err) {
      setToast({ message: err.message, variant: 'error' })
    } finally {
      setSaving(false)
    }
  }

  async function handleDelete(txn) {
    if (!confirm(`Delete "${txn.description || toLabel(txn.category)}"?`)) return
    try {
      await deleteTransaction(txn.id)
      setToast({ message: 'Transaction deleted', variant: 'success' })
      load()
    } catch (err) {
      setToast({ message: err.message, variant: 'error' })
    }
  }

  return (
    <Layout>
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-semibold text-slate-900 dark:text-white">Transactions</h1>
        <button
          onClick={openAddModal}
          className="flex items-center gap-1.5 rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800 dark:bg-white dark:text-slate-900"
        >
          <Plus size={16} /> Add expense
        </button>
      </div>

      {/* Filters */}
      <div className="mb-4 flex flex-wrap gap-2">
        <input
          placeholder="Search description/notes…"
          value={filters.search}
          onChange={(e) => setFilters((f) => ({ ...f, search: e.target.value }))}
          className="rounded-lg border border-slate-300 px-3 py-1.5 text-sm dark:border-slate-700 dark:bg-slate-900 dark:text-white"
        />
        <select
          value={filters.category}
          onChange={(e) => setFilters((f) => ({ ...f, category: e.target.value }))}
          className="rounded-lg border border-slate-300 px-3 py-1.5 text-sm dark:border-slate-700 dark:bg-slate-900 dark:text-white"
        >
          <option value="">All categories</option>
          {EXPENSE_CATEGORIES.map((c) => (
            <option key={c} value={c}>{toLabel(c)}</option>
          ))}
        </select>
        <select
          value={filters.payment_method}
          onChange={(e) => setFilters((f) => ({ ...f, payment_method: e.target.value }))}
          className="rounded-lg border border-slate-300 px-3 py-1.5 text-sm dark:border-slate-700 dark:bg-slate-900 dark:text-white"
        >
          <option value="">All payment methods</option>
          {PAYMENT_METHODS.map((p) => (
            <option key={p} value={p}>{toLabel(p)}</option>
          ))}
        </select>
        <select
          value={filters.type}
          onChange={(e) => setFilters((f) => ({ ...f, type: e.target.value }))}
          className="rounded-lg border border-slate-300 px-3 py-1.5 text-sm dark:border-slate-700 dark:bg-slate-900 dark:text-white"
        >
          <option value="">Need or Want</option>
          {EXPENSE_TYPES.map((t) => (
            <option key={t} value={t}>{toLabel(t)}</option>
          ))}
        </select>
        <select
          value={`${filters.sort_by}:${filters.sort_dir}`}
          onChange={(e) => {
            const [sort_by, sort_dir] = e.target.value.split(':')
            setFilters((f) => ({ ...f, sort_by, sort_dir }))
          }}
          className="rounded-lg border border-slate-300 px-3 py-1.5 text-sm dark:border-slate-700 dark:bg-slate-900 dark:text-white"
        >
          <option value="date:desc">Newest first</option>
          <option value="date:asc">Oldest first</option>
          <option value="amount:desc">Amount: high to low</option>
          <option value="amount:asc">Amount: low to high</option>
        </select>
      </div>

      {loading && <LoadingState label="Loading transactions…" />}
      {!loading && error && <ErrorState message={error} onRetry={load} />}
      {!loading && !error && transactions.length === 0 && (
        <EmptyState
          title="No transactions yet"
          description="Add your first expense to start tracking where your money goes."
          action={
            <button
              onClick={openAddModal}
              className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white dark:bg-white dark:text-slate-900"
            >
              Add expense
            </button>
          }
        />
      )}
      {!loading && !error && transactions.length > 0 && (
        <TransactionTable transactions={transactions} onEdit={openEditModal} onDelete={handleDelete} />
      )}

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title={editingId ? 'Edit expense' : 'Add expense'}>
        <form onSubmit={handleSubmit} className="space-y-3">
          <div>
            <label className="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300">Amount (₹)</label>
            <input
              type="number" step="0.01" min="0.01" required
              value={form.amount}
              onChange={(e) => setForm((f) => ({ ...f, amount: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm dark:border-slate-700 dark:bg-slate-800 dark:text-white"
            />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300">
              Description
              {categorizing && <span className="ml-2 text-xs text-slate-400">✨ AI categorizing…</span>}
            </label>
            <input
              value={form.description}
              onChange={(e) => {
                const val = e.target.value
                setForm((f) => ({ ...f, description: val }))
                clearTimeout(window._catTimer)
                window._catTimer = setTimeout(() => tryAICategorize(val), 800)
              }}
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm dark:border-slate-700 dark:bg-slate-800 dark:text-white"
              placeholder="e.g. Bought DBMS textbook for ₹650"
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
              <label className="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300">Date</label>
              <input
                type="date" required
                value={form.date}
                onChange={(e) => setForm((f) => ({ ...f, date: e.target.value }))}
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm dark:border-slate-700 dark:bg-slate-800 dark:text-white"
              />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300">Payment method</label>
              <select
                value={form.payment_method}
                onChange={(e) => setForm((f) => ({ ...f, payment_method: e.target.value }))}
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm dark:border-slate-700 dark:bg-slate-800 dark:text-white"
              >
                {PAYMENT_METHODS.map((p) => <option key={p} value={p}>{toLabel(p)}</option>)}
              </select>
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300">Need or Want</label>
              <select
                value={form.type}
                onChange={(e) => setForm((f) => ({ ...f, type: e.target.value }))}
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm dark:border-slate-700 dark:bg-slate-800 dark:text-white"
              >
                {EXPENSE_TYPES.map((t) => <option key={t} value={t}>{toLabel(t)}</option>)}
              </select>
            </div>
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300">Notes</label>
            <textarea
              value={form.notes}
              onChange={(e) => setForm((f) => ({ ...f, notes: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm dark:border-slate-700 dark:bg-slate-800 dark:text-white"
              rows={2}
            />
          </div>
          <button
            type="submit"
            disabled={saving}
            className="w-full rounded-lg bg-slate-900 py-2 text-sm font-medium text-white hover:bg-slate-800 disabled:opacity-50 dark:bg-white dark:text-slate-900"
          >
            {saving ? 'Saving…' : editingId ? 'Save changes' : 'Add expense'}
          </button>
        </form>
      </Modal>

      <Toast message={toast?.message} variant={toast?.variant} onDismiss={() => setToast(null)} />
    </Layout>
  )
}
