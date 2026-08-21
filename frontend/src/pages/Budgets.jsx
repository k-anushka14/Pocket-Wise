import { useEffect, useState } from 'react'
import { Plus } from 'lucide-react'
import Layout from '../components/Layout'
import Modal from '../components/Modal'
import Toast from '../components/Toast'
import EmptyState from '../components/EmptyState'
import ErrorState from '../components/ErrorState'
import LoadingState from '../components/LoadingState'
import BudgetProgress from '../components/BudgetProgress'
import { listBudgets, createBudget, updateBudget, deleteBudget } from '../api/budgets'
import { EXPENSE_CATEGORIES, toLabel } from '../utils/constants'

const EMPTY_FORM = { category: 'food', amount: '' }

export default function Budgets() {
  const [budgets, setBudgets] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [toast, setToast] = useState(null)

  const [modalOpen, setModalOpen] = useState(false)
  const [editingId, setEditingId] = useState(null)
  const [form, setForm] = useState(EMPTY_FORM)
  const [saving, setSaving] = useState(false)

  async function load() {
    setLoading(true)
    setError('')
    try {
      setBudgets(await listBudgets())
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  function openAddModal() {
    setEditingId(null)
    setForm(EMPTY_FORM)
    setModalOpen(true)
  }

  function openEditModal(budget) {
    setEditingId(budget.id)
    setForm({ category: budget.category, amount: budget.amount })
    setModalOpen(true)
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setSaving(true)
    try {
      if (editingId) {
        await updateBudget(editingId, { amount: Number(form.amount) })
        setToast({ message: 'Budget updated', variant: 'success' })
      } else {
        await createBudget({
          category: form.category,
          amount: Number(form.amount),
          month: new Date().toISOString().slice(0, 10),
        })
        setToast({ message: 'Budget created', variant: 'success' })
      }
      setModalOpen(false)
      load()
    } catch (err) {
      setToast({ message: err.message, variant: 'error' })
    } finally {
      setSaving(false)
    }
  }

  async function handleDelete(budget) {
    if (!confirm(`Delete the ${toLabel(budget.category)} budget?`)) return
    try {
      await deleteBudget(budget.id)
      setToast({ message: 'Budget deleted', variant: 'success' })
      load()
    } catch (err) {
      setToast({ message: err.message, variant: 'error' })
    }
  }

  const usedCategories = budgets.map((b) => b.category)
  const availableCategories = EXPENSE_CATEGORIES.filter((c) => !usedCategories.includes(c) || c === form.category)

  return (
    <Layout>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-slate-900 dark:text-white">Budgets</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400">This month's category budgets</p>
        </div>
        <button
          onClick={openAddModal}
          className="flex items-center gap-1.5 rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800 dark:bg-white dark:text-slate-900"
        >
          <Plus size={16} /> Add budget
        </button>
      </div>

      {loading && <LoadingState label="Loading budgets…" />}
      {!loading && error && <ErrorState message={error} onRetry={load} />}
      {!loading && !error && budgets.length === 0 && (
        <EmptyState
          title="No budgets set for this month"
          description="Set a spending limit per category to get warnings before you overspend."
          action={
            <button onClick={openAddModal} className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white dark:bg-white dark:text-slate-900">
              Add budget
            </button>
          }
        />
      )}
      {!loading && !error && budgets.length > 0 && (
        <div className="space-y-3">
          {budgets.map((b) => (
            <BudgetProgress key={b.id} budget={b} onEdit={openEditModal} onDelete={handleDelete} />
          ))}
        </div>
      )}

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title={editingId ? 'Edit budget' : 'Add budget'}>
        <form onSubmit={handleSubmit} className="space-y-3">
          <div>
            <label className="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300">Category</label>
            <select
              value={form.category}
              disabled={!!editingId}
              onChange={(e) => setForm((f) => ({ ...f, category: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm disabled:bg-slate-100 dark:border-slate-700 dark:bg-slate-800 dark:text-white dark:disabled:bg-slate-800/50"
            >
              {availableCategories.map((c) => <option key={c} value={c}>{toLabel(c)}</option>)}
            </select>
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300">Monthly limit (₹)</label>
            <input
              type="number" step="0.01" min="0.01" required
              value={form.amount}
              onChange={(e) => setForm((f) => ({ ...f, amount: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm dark:border-slate-700 dark:bg-slate-800 dark:text-white"
            />
          </div>
          <button
            type="submit"
            disabled={saving}
            className="w-full rounded-lg bg-slate-900 py-2 text-sm font-medium text-white hover:bg-slate-800 disabled:opacity-50 dark:bg-white dark:text-slate-900"
          >
            {saving ? 'Saving…' : editingId ? 'Save changes' : 'Add budget'}
          </button>
        </form>
      </Modal>

      <Toast message={toast?.message} variant={toast?.variant} onDismiss={() => setToast(null)} />
    </Layout>
  )
}
