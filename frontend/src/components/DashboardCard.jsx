import { motion } from 'framer-motion'
import { formatCurrency } from '../utils/constants'
import { useCountUp } from '../hooks/useCountUp'

const ACCENTS = {
  slate: {
    text: 'text-slate-900 dark:text-white',
    iconBg: 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-200',
  },
  emerald: {
    text: 'text-emerald-600 dark:text-emerald-400',
    iconBg: 'bg-emerald-100 text-emerald-600 dark:bg-emerald-950 dark:text-emerald-400',
  },
  red: {
    text: 'text-red-600 dark:text-red-400',
    iconBg: 'bg-red-100 text-red-600 dark:bg-red-950 dark:text-red-400',
  },
  blue: {
    text: 'text-blue-600 dark:text-blue-400',
    iconBg: 'bg-blue-100 text-blue-600 dark:bg-blue-950 dark:text-blue-400',
  },
}

export default function DashboardCard({ label, value, icon: Icon, accent = 'slate', isCurrency = true }) {
  const numericValue = isCurrency ? Number(value) || 0 : 0
  const animated = useCountUp(numericValue)
  const colors = ACCENTS[accent]

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -3, boxShadow: '0 12px 24px -8px rgba(15, 23, 42, 0.15)' }}
      transition={{ duration: 0.25 }}
      className="rounded-2xl bg-white p-5 shadow-sm dark:bg-slate-900"
    >
      <div className="mb-3 flex items-center justify-between">
        <span className="text-sm font-medium text-slate-500 dark:text-slate-400">{label}</span>
        {Icon && (
          <span className={`flex h-9 w-9 items-center justify-center rounded-xl ${colors.iconBg}`}>
            <Icon size={17} />
          </span>
        )}
      </div>
      <p className={`text-2xl font-semibold tabular-nums ${colors.text}`}>
        {isCurrency ? formatCurrency(animated) : value}
      </p>
    </motion.div>
  )
}
