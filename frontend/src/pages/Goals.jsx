import { useEffect, useState } from 'react'
import { Plus } from 'lucide-react'
import Layout from '../components/Layout'
import Modal from '../components/Modal'
import Toast from '../components/Toast'
import EmptyState from '../components/EmptyState'
import ErrorState from '../components/ErrorState'
import LoadingState from '../components/LoadingState'
import SavingsGoalCard from '../components/SavingsGoalCard'
import { listGoals, createGoal, updateGoal, deleteGoal, contributeToGoal } from '../api/goals'

const EMPTY_FORM = { name: '', target_amount: '', deadline: '', priority: 'medium' }

export default function Goals() {
  const [goals, setGoals] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [toast, setToast] = useState(null)

  const [modalOpen, setModalOpen] = useState(false)
  const [editingId, setEditingId] = useState(null)
  const [form, setForm] = useState(EMPTY_FORM)
  const [saving, setSaving] = useState(false)

  const [contributeGoal, setContributeGoal] = useState(null)
  const [contributeAmount, setContributeAmount] = useState('')

  async function load() {
    setLoading(true)
    setError('')
    try {
      setGoals(await listGoals())
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

  function openEditModal(goal) {
    setEditingId(goal.id)
    setForm({
      name: goal.name,
      target_amount: goal.target_amount,
      deadline: goal.deadline || '',
      priority: goal.priority,
    })
    setModalOpen(true)
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setSaving(true)
    try {
      if (editingId) {
        await updateGoal(editingId, {
          name: form.name,
          target_amount: Number(form.target_amount),
          deadline: form.deadline || null,
          priority: form.priority,
        })
        setToast({ message: 'Goal updated', variant: 'success' })
      } else {
        await createGoal({
          name: form.name,
          target_amount: Number(form.target_amount),
          current_amount: 0,
          deadline: form.deadline || null,
          priority: form.priority,
        })
        setToast({ message: 'Goal created', variant: 'success' })
      }
      setModalOpen(false)
      load()
    } catch (err) {
      setToast({ message: err.message, variant: 'error' })
    } finally {
      setSaving(false)
    }
  }

  async function handleDelete(goal) {
    if (!confirm(`Delete "${goal.name}"?`)) return
    try {
      await deleteGoal(goal.id)
      setToast({ message: 'Goal deleted', variant: 'success' })
      load()
    } catch (err) {
      setToast({ message: err.message, variant: 'error' })
    }
  }

  async function handleContributeSubmit(e) {
    e.preventDefault()
    try {
      await contributeToGoal(contributeGoal.id, Number(contributeAmount))
      setToast({ message: 'Funds added', variant: 'success' })
      setContributeGoal(null)
      setContributeAmount('')
      load()
    } catch (err) {
      setToast({ message: err.message, variant: 'error' })
    }
  }

  return (
    <Layout>
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-semibold text-slate-900 dark:text-white">Savings Goals</h1>
        <button
          onClick={openAddModal}
          className="flex items-center gap-1.5 rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800 dark:bg-white dark:text-slate-900"
        >
          <Plus size={16} /> New goal
        </button>
      </div>

      {loading && <LoadingState label="Loading goals…" />}
      {!loading && error && <ErrorState message={error} onRetry={load} />}
      {!loading && !error && goals.length === 0 && (
        <EmptyState
          title="No savings goals yet"
          description="Set a target — a trip, a laptop, an emergency fund — and track your progress."
          action={
            <button onClick={openAddModal} className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white dark:bg-white dark:text-slate-900">
              New goal
            </button>
          }
        />
      )}
      {!loading && !error && goals.length > 0 && (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {goals.map((g) => (
            <SavingsGoalCard
              key={g.id}
              goal={g}
              onEdit={openEditModal}
              onDelete={handleDelete}
              onContribute={setContributeGoal}
            />
          ))}
        </div>
      )}

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title={editingId ? 'Edit goal' : 'New goal'}>
        <form onSubmit={handleSubmit} className="space-y-3">
          <div>
            <label className="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300">Goal name</label>
            <input
              required
              value={form.name}
              onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm dark:border-slate-700 dark:bg-slate-800 dark:text-white"
              placeholder="Goa trip, new laptop…"
            />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300">Target amount (₹)</label>
            <input
              type="number" step="0.01" min="0.01" required
              value={form.target_amount}
              onChange={(e) => setForm((f) => ({ ...f, target_amount: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm dark:border-slate-700 dark:bg-slate-800 dark:text-white"
            />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300">Deadline (optional)</label>
              <input
                type="date"
                value={form.deadline}
                onChange={(e) => setForm((f) => ({ ...f, deadline: e.target.value }))}
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm dark:border-slate-700 dark:bg-slate-800 dark:text-white"
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300">Priority</label>
              <select
                value={form.priority}
                onChange={(e) => setForm((f) => ({ ...f, priority: e.target.value }))}
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm dark:border-slate-700 dark:bg-slate-800 dark:text-white"
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
              </select>
            </div>
          </div>
          <button
            type="submit"
            disabled={saving}
            className="w-full rounded-lg bg-slate-900 py-2 text-sm font-medium text-white hover:bg-slate-800 disabled:opacity-50 dark:bg-white dark:text-slate-900"
          >
            {saving ? 'Saving…' : editingId ? 'Save changes' : 'Create goal'}
          </button>
        </form>
      </Modal>

      <Modal open={!!contributeGoal} onClose={() => setContributeGoal(null)} title={`Add funds to ${contributeGoal?.name || ''}`}>
        <form onSubmit={handleContributeSubmit} className="space-y-3">
          <div>
            <label className="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300">Amount (₹)</label>
            <input
              type="number" step="0.01" min="0.01" required
              value={contributeAmount}
              onChange={(e) => setContributeAmount(e.target.value)}
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm dark:border-slate-700 dark:bg-slate-800 dark:text-white"
              autoFocus
            />
          </div>
          <button
            type="submit"
            className="w-full rounded-lg bg-slate-900 py-2 text-sm font-medium text-white hover:bg-slate-800 dark:bg-white dark:text-slate-900"
          >
            Add funds
          </button>
        </form>
      </Modal>

      <Toast message={toast?.message} variant={toast?.variant} onDismiss={() => setToast(null)} />
    </Layout>
  )
}
