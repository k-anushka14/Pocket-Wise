import { useEffect, useState } from 'react'
import { Plus, Pencil, Trash2 } from 'lucide-react'
import Layout from '../components/Layout'
import Modal from '../components/Modal'
import Toast from '../components/Toast'
import EmptyState from '../components/EmptyState'
import ErrorState from '../components/ErrorState'
import LoadingState from '../components/LoadingState'
import { listIncome, createIncome, updateIncome, deleteIncome } from '../api/income'
import { INCOME_SOURCES, RECURRENCE_FREQUENCIES, formatCurrency, toLabel } from '../utils/constants'

const EMPTY_FORM = {
  amount: '',
  source: 'pocket_money',
  date: new Date().toISOString().slice(0, 10),
  is_recurring: false,
  frequency: '',
  notes: '',
}

export default function Income() {
  const [income, setIncome] = useState([])
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
      setIncome(await listIncome())
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const totalIncome = income.reduce((sum, i) => sum + Number(i.amount), 0)

  function openAddModal() {
    setEditingId(null)
    setForm(EMPTY_FORM)
    setModalOpen(true)
  }

  function openEditModal(entry) {
    setEditingId(entry.id)
    setForm({
      amount: entry.amount,
      source: entry.source,
      date: entry.date,
      is_recurring: entry.is_recurring,
      frequency: entry.frequency || '',
      notes: entry.notes || '',
    })
    setModalOpen(true)
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setSaving(true)
    try {
      const payload = {
        ...form,
        amount: Number(form.amount),
        frequency: form.is_recurring ? form.frequency || 'monthly' : null,
      }
      if (editingId) {
        await updateIncome(editingId, payload)
        setToast({ message: 'Income updated', variant: 'success' })
      } else {
        await createIncome(payload)
        setToast({ message: 'Income added', variant: 'success' })
      }
      setModalOpen(false)
      load()
    } catch (err) {
      setToast({ message: err.message, variant: 'error' })
    } finally {
      setSaving(false)
    }
  }

  async function handleDelete(entry) {
    if (!confirm(`Delete this ${toLabel(entry.source)} entry?`)) return
    try {
      await deleteIncome(entry.id)
      setToast({ message: 'Income deleted', variant: 'success' })
      load()
    } catch (err) {
      setToast({ message: err.message, variant: 'error' })
    }
  }

  return (
    <Layout>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-slate-900 dark:text-white">Income</h1>
          {!loading && !error && (
            <p className="text-sm text-slate-500 dark:text-slate-400">
              Total tracked: {formatCurrency(totalIncome)}
            </p>
          )}
        </div>
        <button
          onClick={openAddModal}
          className="flex items-center gap-1.5 rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800 dark:bg-white dark:text-slate-900"
        >
          <Plus size={16} /> Add income
        </button>
      </div>

      {loading && <LoadingState label="Loading income…" />}
      {!loading && error && <ErrorState message={error} onRetry={load} />}
      {!loading && !error && income.length === 0 && (
        <EmptyState
          title="No income logged yet"
          description="Add your pocket money, allowance, or stipend to see your available balance."
          action={
            <button
              onClick={openAddModal}
              className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white dark:bg-white dark:text-slate-900"
            >
              Add income
            </button>
          }
        />
      )}
      {!loading && !error && income.length > 0 && (
        <div className="overflow-x-auto rounded-2xl bg-white shadow-sm dark:bg-slate-900">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-200 text-left text-slate-500 dark:border-slate-800 dark:text-slate-400">
                <th className="px-4 py-3 font-medium">Date</th>
                <th className="px-4 py-3 font-medium">Source</th>
                <th className="px-4 py-3 font-medium">Recurring</th>
                <th className="px-4 py-3 text-right font-medium">Amount</th>
                <th className="px-4 py-3"></th>
              </tr>
            </thead>
            <tbody>
              {income.map((entry) => (
                <tr
                  key={entry.id}
                  className="border-b border-slate-100 last:border-0 hover:bg-slate-50 dark:border-slate-800 dark:hover:bg-slate-800/50"
                >
                  <td className="whitespace-nowrap px-4 py-3 text-slate-600 dark:text-slate-300">{entry.date}</td>
                  <td className="px-4 py-3 text-slate-900 dark:text-white">{toLabel(entry.source)}</td>
                  <td className="px-4 py-3 text-slate-600 dark:text-slate-300">
                    {entry.is_recurring ? toLabel(entry.frequency || '') : '—'}
                  </td>
                  <td className="whitespace-nowrap px-4 py-3 text-right font-medium text-slate-900 dark:text-white">
                    {formatCurrency(entry.amount)}
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex justify-end gap-2">
                      <button onClick={() => openEditModal(entry)} className="text-slate-400 hover:text-slate-700 dark:hover:text-slate-200" aria-label="Edit">
                        <Pencil size={15} />
                      </button>
                      <button onClick={() => handleDelete(entry)} className="text-slate-400 hover:text-red-600" aria-label="Delete">
                        <Trash2 size={15} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title={editingId ? 'Edit income' : 'Add income'}>
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
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300">Source</label>
              <select
                value={form.source}
                onChange={(e) => setForm((f) => ({ ...f, source: e.target.value }))}
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm dark:border-slate-700 dark:bg-slate-800 dark:text-white"
              >
                {INCOME_SOURCES.map((s) => <option key={s} value={s}>{toLabel(s)}</option>)}
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
          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="is_recurring"
              checked={form.is_recurring}
              onChange={(e) => setForm((f) => ({ ...f, is_recurring: e.target.checked }))}
              className="h-4 w-4 rounded border-slate-300"
            />
            <label htmlFor="is_recurring" className="text-sm text-slate-700 dark:text-slate-300">
              This is recurring
            </label>
          </div>
          {form.is_recurring && (
            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300">Frequency</label>
              <select
                value={form.frequency}
                onChange={(e) => setForm((f) => ({ ...f, frequency: e.target.value }))}
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm dark:border-slate-700 dark:bg-slate-800 dark:text-white"
              >
                <option value="">Select…</option>
                {RECURRENCE_FREQUENCIES.map((f) => <option key={f} value={f}>{toLabel(f)}</option>)}
              </select>
            </div>
          )}
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
            {saving ? 'Saving…' : editingId ? 'Save changes' : 'Add income'}
          </button>
        </form>
      </Modal>

      <Toast message={toast?.message} variant={toast?.variant} onDismiss={() => setToast(null)} />
    </Layout>
  )
}
