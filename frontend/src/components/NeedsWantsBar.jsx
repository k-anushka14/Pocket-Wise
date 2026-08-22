import { formatCurrency } from '../utils/constants'

export default function NeedsWantsBar({ needsVsWants }) {
  const { needs, wants, wants_percentage } = needsVsWants
  const total = Number(needs) + Number(wants)
  const needsPct = total > 0 ? (Number(needs) / total) * 100 : 0

  return (
    <div className="rounded-2xl bg-white p-5 shadow-sm dark:bg-slate-900">
      <h3 className="mb-4 text-sm font-semibold text-slate-900 dark:text-white">Needs vs Wants</h3>
      <div className="mb-2 flex h-3 w-full overflow-hidden rounded-full bg-slate-100 dark:bg-slate-800">
        <div className="h-full bg-blue-500" style={{ width: `${needsPct}%` }} />
        <div className="h-full bg-amber-500" style={{ width: `${100 - needsPct}%` }} />
      </div>
      <div className="flex justify-between text-sm">
        <span className="flex items-center gap-1.5 text-slate-600 dark:text-slate-300">
          <span className="h-2 w-2 rounded-full bg-blue-500" /> Needs: {formatCurrency(needs)}
        </span>
        <span className="flex items-center gap-1.5 text-slate-600 dark:text-slate-300">
          <span className="h-2 w-2 rounded-full bg-amber-500" /> Wants: {formatCurrency(wants)}
        </span>
      </div>
      <p className="mt-3 text-xs text-slate-500 dark:text-slate-400">
        {wants_percentage}% of this month's spending was on wants.
      </p>
    </div>
  )
}
