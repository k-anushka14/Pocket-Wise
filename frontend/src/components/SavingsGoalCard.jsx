import { Pencil, Trash2, PlusCircle } from 'lucide-react'
import { formatCurrency } from '../utils/constants'

const PRIORITY_STYLES = {
  high: 'bg-red-100 text-red-700 dark:bg-red-950 dark:text-red-300',
  medium: 'bg-amber-100 text-amber-700 dark:bg-amber-950 dark:text-amber-300',
  low: 'bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-300',
}

export default function SavingsGoalCard({ goal, onEdit, onDelete, onContribute }) {
  const barColor = goal.is_completed ? 'bg-emerald-500' : goal.is_overdue ? 'bg-red-500' : 'bg-blue-500'

  return (
    <div className="rounded-2xl bg-white p-5 shadow-sm dark:bg-slate-900">
      <div className="mb-2 flex items-start justify-between">
        <div>
          <h3 className="font-medium text-slate-900 dark:text-white">{goal.name}</h3>
          {goal.deadline && (
            <p className="text-xs text-slate-500 dark:text-slate-400">Target date: {goal.deadline}</p>
          )}
        </div>
        <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${PRIORITY_STYLES[goal.priority]}`}>
          {goal.priority}
        </span>
      </div>

      <div className="mb-1.5 h-2 w-full overflow-hidden rounded-full bg-slate-100 dark:bg-slate-800">
        <div className={`h-full ${barColor}`} style={{ width: `${goal.progress_percentage}%` }} />
      </div>
      <div className="mb-3 flex justify-between text-xs text-slate-500 dark:text-slate-400">
        <span>{formatCurrency(goal.current_amount)} of {formatCurrency(goal.target_amount)}</span>
        <span>{goal.progress_percentage}%</span>
      </div>

      {goal.is_completed && (
        <p className="mb-3 text-sm font-medium text-emerald-600 dark:text-emerald-400">🎯 Goal reached!</p>
      )}
      {!goal.is_completed && goal.is_overdue && (
        <p className="mb-3 text-sm font-medium text-red-600 dark:text-red-400">Deadline passed</p>
      )}
      {!goal.is_completed && !goal.is_overdue && goal.amount_per_week != null && (
        <p className="mb-3 text-sm text-slate-600 dark:text-slate-300">
          Save {formatCurrency(goal.amount_per_week)}/week to reach this on time.
        </p>
      )}

      <div className="flex items-center gap-3 text-sm">
        <button onClick={() => onContribute(goal)} className="flex items-center gap-1 text-blue-600 hover:underline dark:text-blue-400">
          <PlusCircle size={14} /> Add funds
        </button>
        <button onClick={() => onEdit(goal)} className="flex items-center gap-1 text-slate-500 hover:text-slate-700 dark:hover:text-slate-200">
          <Pencil size={14} /> Edit
        </button>
        <button onClick={() => onDelete(goal)} className="flex items-center gap-1 text-slate-500 hover:text-red-600">
          <Trash2 size={14} /> Delete
        </button>
      </div>
    </div>
  )
}
