import { useEffect, useState } from 'react'
import { Plus, Trash2, Check, X } from 'lucide-react'
import Layout from '../components/Layout'
import Modal from '../components/Modal'
import Toast from '../components/Toast'
import EmptyState from '../components/EmptyState'
import ErrorState from '../components/ErrorState'
import LoadingState from '../components/LoadingState'
import { listSplitExpenses, createSplitExpense, markParticipantPaid, deleteSplitExpense } from '../api/splits'
import { formatCurrency } from '../utils/constants'

const EMPTY_FORM = {
  description: '', total_amount: '', date: new Date().toISOString().slice(0, 10),
  participants: [{ person_name: '', amount_owed: '', direction: 'owed_to_me' }],
}

export default function SplitExpenses() {
  const [splits, setSplits] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [toast, setToast] = useState(null)

  const [modalOpen, setModalOpen] = useState(false)
  const [form, setForm] = useState(EMPTY_FORM)
  const [saving, setSaving] = useState(false)

  async function load() {
    setLoading(true)
    setError('')
    try {
      setSplits(await listSplitExpenses())
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  function updateParticipant(index, field, value) {
    setForm((f) => {
      const participants = [...f.participants]
      participants[index] = { ...participants[index], [field]: value }
      return { ...f, participants }
    })
  }

  function addParticipantRow() {
    setForm((f) => ({
      ...f,
      participants: [...f.participants, { person_name: '', amount_owed: '', direction: 'owed_to_me' }],
    }))
  }

  function removeParticipantRow(index) {
    setForm((f) => ({ ...f, participants: f.participants.filter((_, i) => i !== index) }))
  }

  function splitEvenly() {
    // Participant rows represent everyone EXCEPT you -- the total bill is
    // split across you + those rows, so the divisor is n + 1, not n.
    // (This is what was wrong before: with 1 other person on the form,
    // it divided by 1 and handed back the full amount instead of half.)
    const n = form.participants.length
    if (!form.total_amount || n === 0) return
    const totalPeople = n + 1
    const share = (Number(form.total_amount) / totalPeople).toFixed(2)
    setForm((f) => ({
      ...f,
      participants: f.participants.map((p) => ({ ...p, amount_owed: share })),
    }))
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setSaving(true)
    try {
      await createSplitExpense({
        description: form.description,
        total_amount: Number(form.total_amount),
        date: form.date,
        participants: form.participants.map((p) => ({
          person_name: p.person_name,
          amount_owed: Number(p.amount_owed),
          direction: p.direction,
        })),
      })
      setToast({ message: 'Split expense added', variant: 'success' })
      setModalOpen(false)
      setForm(EMPTY_FORM)
      load()
    } catch (err) {
      setToast({ message: err.message, variant: 'error' })
    } finally {
      setSaving(false)
    }
  }

  async function handleMarkPaid(split, participant) {
    try {
      await markParticipantPaid(split.id, participant.id)
      load()
    } catch (err) {
      setToast({ message: err.message, variant: 'error' })
    }
  }

  async function handleDelete(split) {
    if (!confirm(`Delete "${split.description}"?`)) return
    try {
      await deleteSplitExpense(split.id)
      setToast({ message: 'Deleted', variant: 'success' })
      load()
    } catch (err) {
      setToast({ message: err.message, variant: 'error' })
    }
  }

  return (
    <Layout>
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-semibold text-slate-900 dark:text-white">Split Expenses</h1>
        <button
          onClick={() => setModalOpen(true)}
          className="flex items-center gap-1.5 rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800 dark:bg-white dark:text-slate-900"
        >
          <Plus size={16} /> Split an expense
        </button>
      </div>

      {loading && <LoadingState label="Loading splits…" />}
      {!loading && error && <ErrorState message={error} onRetry={load} />}
      {!loading && !error && splits.length === 0 && (
        <EmptyState
          title="No split expenses yet"
          description="Split a group expense like a meal or a cab, and track who's paid you back."
          action={
            <button onClick={() => setModalOpen(true)} className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white dark:bg-white dark:text-slate-900">
              Split an expense
            </button>
          }
        />
      )}
      {!loading && !error && splits.length > 0 && (
        <div className="space-y-3">
          {splits.map((split) => (
            <div key={split.id} className="rounded-2xl bg-white p-5 shadow-sm dark:bg-slate-900">
              <div className="mb-3 flex items-start justify-between">
                <div>
                  <p className="font-medium text-slate-900 dark:text-white">{split.description}</p>
                  <p className="text-xs text-slate-500 dark:text-slate-400">
                    {formatCurrency(split.total_amount)} total · {split.date}
                  </p>
                </div>
                <button onClick={() => handleDelete(split)} className="text-slate-400 hover:text-red-600" aria-label="Delete">
                  <Trash2 size={15} />
                </button>
              </div>
              <div className="space-y-1.5">
                {split.participants.map((p) => (
                  <div key={p.id} className="flex items-center justify-between rounded-lg bg-slate-50 px-3 py-2 text-sm dark:bg-slate-800/60">
                    <span className="text-slate-700 dark:text-slate-300">
                      {p.person_name}{' '}
                      <span className="text-xs text-slate-400 dark:text-slate-500">
                        ({p.direction === 'owed_to_me' ? 'owes you' : 'you owe'})
                      </span>
                    </span>
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-slate-900 dark:text-white">{formatCurrency(p.amount_owed)}</span>
                      {p.status === 'paid' ? (
                        <span className="flex items-center gap-1 text-xs font-medium text-emerald-600 dark:text-emerald-400">
                          <Check size={13} /> Paid
                        </span>
                      ) : (
                        <button
                          onClick={() => handleMarkPaid(split, p)}
                          className="rounded-full bg-slate-200 px-2 py-0.5 text-xs font-medium text-slate-600 hover:bg-slate-300 dark:bg-slate-700 dark:text-slate-300"
                        >
                          Mark paid
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title="Split an expense">
        <form onSubmit={handleSubmit} className="space-y-3">
          <div>
            <label className="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300">Description</label>
            <input
              required
              value={form.description}
              onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm dark:border-slate-700 dark:bg-slate-800 dark:text-white"
              placeholder="Pizza, cab ride…"
            />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300">Total amount (₹)</label>
              <input
                type="number" step="0.01" min="0.01" required
                value={form.total_amount}
                onChange={(e) => setForm((f) => ({ ...f, total_amount: e.target.value }))}
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm dark:border-slate-700 dark:bg-slate-800 dark:text-white"
              />
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

          <div>
            <div className="mb-1 flex items-center justify-between">
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300">
                Participants (everyone except you)
              </label>
              <button type="button" onClick={splitEvenly} className="text-xs text-blue-600 hover:underline dark:text-blue-400">
                Split evenly ({form.participants.length + 1} people)
              </button>
            </div>
            <div className="space-y-2">
              {form.participants.map((p, i) => (
                <div key={i} className="flex items-center gap-2">
                  <input
                    required
                    placeholder="Name"
                    value={p.person_name}
                    onChange={(e) => updateParticipant(i, 'person_name', e.target.value)}
                    className="w-1/3 rounded-lg border border-slate-300 px-2 py-1.5 text-sm dark:border-slate-700 dark:bg-slate-800 dark:text-white"
                  />
                  <input
                    type="number" step="0.01" min="0.01" required
                    placeholder="Amount"
                    value={p.amount_owed}
                    onChange={(e) => updateParticipant(i, 'amount_owed', e.target.value)}
                    className="w-1/4 rounded-lg border border-slate-300 px-2 py-1.5 text-sm dark:border-slate-700 dark:bg-slate-800 dark:text-white"
                  />
                  <select
                    value={p.direction}
                    onChange={(e) => updateParticipant(i, 'direction', e.target.value)}
                    className="flex-1 rounded-lg border border-slate-300 px-2 py-1.5 text-sm dark:border-slate-700 dark:bg-slate-800 dark:text-white"
                  >
                    <option value="owed_to_me">Owes me</option>
                    <option value="i_owe">I owe</option>
                  </select>
                  {form.participants.length > 1 && (
                    <button type="button" onClick={() => removeParticipantRow(i)} className="text-slate-400 hover:text-red-600">
                      <X size={16} />
                    </button>
                  )}
                </div>
              ))}
            </div>
            <button type="button" onClick={addParticipantRow} className="mt-2 text-xs text-slate-500 hover:text-slate-700 dark:hover:text-slate-300">
              + Add another person
            </button>
          </div>

          <button
            type="submit"
            disabled={saving}
            className="w-full rounded-lg bg-slate-900 py-2 text-sm font-medium text-white hover:bg-slate-800 disabled:opacity-50 dark:bg-white dark:text-slate-900"
          >
            {saving ? 'Saving…' : 'Save split'}
          </button>
        </form>
      </Modal>

      <Toast message={toast?.message} variant={toast?.variant} onDismiss={() => setToast(null)} />
    </Layout>
  )
}
