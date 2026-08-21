import { toLabel, formatCurrency } from '../utils/constants'

const STATUS_STYLES = {
  normal: { bar: 'bg-emerald-500', text: 'text-emerald-600 dark:text-emerald-400', label: 'On track' },
  warning: { bar: 'bg-amber-500', text: 'text-amber-600 dark:text-amber-400', label: 'Warning' },
  critical: { bar: 'bg-orange-500', text: 'text-orange-600 dark:text-orange-400', label: 'Critical' },
  overspent: { bar: 'bg-red-500', text: 'text-red-600 dark:text-red-400', label: 'Overspent' },
}

export default function BudgetProgress({ budget, onEdit, onDelete }) {
  const style = STATUS_STYLES[budget.status]
  const widthPct = Math.min(budget.percentage_used, 100)

  return (
    <div className="rounded-xl border border-slate-100 p-4 dark:border-slate-800">
      <div className="mb-1 flex items-center justify-between">
        <span className="text-sm font-medium text-slate-900 dark:text-white">{toLabel(budget.category)}</span>
        <div className="flex items-center gap-3">
          <span className={`text-xs font-medium ${style.text}`}>{style.label}</span>
          {onEdit && (
            <button onClick={() => onEdit(budget)} className="text-xs text-slate-400 hover:text-slate-700 dark:hover:text-slate-200">
              Edit
            </button>
          )}
          {onDelete && (
            <button onClick={() => onDelete(budget)} className="text-xs text-slate-400 hover:text-red-600">
              Delete
            </button>
          )}
        </div>
      </div>

      <div className="mb-1.5 h-2 w-full overflow-hidden rounded-full bg-slate-100 dark:bg-slate-800">
        <div className={`h-full ${style.bar}`} style={{ width: `${widthPct}%` }} />
      </div>

      <div className="flex justify-between text-xs text-slate-500 dark:text-slate-400">
        <span>{formatCurrency(budget.spent)} spent of {formatCurrency(budget.amount)}</span>
        <span>{budget.percentage_used}%</span>
      </div>
    </div>
  )
}
