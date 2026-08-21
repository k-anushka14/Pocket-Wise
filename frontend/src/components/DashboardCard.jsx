import { formatCurrency } from '../utils/constants'

const ACCENTS = {
  slate: 'text-slate-900 dark:text-white',
  emerald: 'text-emerald-600 dark:text-emerald-400',
  red: 'text-red-600 dark:text-red-400',
  blue: 'text-blue-600 dark:text-blue-400',
}

export default function DashboardCard({ label, value, icon: Icon, accent = 'slate', isCurrency = true }) {
  return (
    <div className="rounded-2xl bg-white p-5 shadow-sm dark:bg-slate-900">
      <div className="mb-2 flex items-center justify-between">
        <span className="text-sm font-medium text-slate-500 dark:text-slate-400">{label}</span>
        {Icon && <Icon size={18} className="text-slate-400 dark:text-slate-500" />}
      </div>
      <p className={`text-2xl font-semibold ${ACCENTS[accent]}`}>
        {isCurrency ? formatCurrency(value) : value}
      </p>
    </div>
  )
}
