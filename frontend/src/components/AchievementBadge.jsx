import { motion } from 'framer-motion'

export default function AchievementBadge({ achievement }) {
  const { name, description, icon, earned, earned_at } = achievement

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      whileHover={earned ? { y: -3 } : {}}
      transition={{ duration: 0.25 }}
      className={`relative overflow-hidden rounded-2xl border p-5 text-center transition ${
        earned
          ? 'border-amber-200 bg-amber-50 dark:border-amber-900 dark:bg-amber-950'
          : 'border-slate-200 bg-slate-50 opacity-60 grayscale dark:border-slate-800 dark:bg-slate-900'
      }`}
    >
      {earned && (
        <motion.div
          className="pointer-events-none absolute inset-0"
          initial={{ boxShadow: '0 0 0 0 rgba(245, 158, 11, 0.5)' }}
          animate={{ boxShadow: '0 0 0 12px rgba(245, 158, 11, 0)' }}
          transition={{ duration: 1, ease: 'easeOut' }}
        />
      )}
      <motion.div
        className="mb-2 text-4xl"
        initial={earned ? { scale: 0, rotate: -20 } : false}
        animate={earned ? { scale: 1, rotate: 0 } : {}}
        transition={{ type: 'spring', stiffness: 260, damping: 14 }}
      >
        {icon}
      </motion.div>
      <p className="font-semibold text-slate-900 dark:text-white">{name}</p>
      <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">{description}</p>
      {earned && earned_at && (
        <p className="mt-2 text-xs font-medium text-amber-600 dark:text-amber-400">
          Earned {new Date(earned_at).toLocaleDateString()}
        </p>
      )}
      {!earned && (
        <p className="mt-2 text-xs text-slate-400 dark:text-slate-500">Locked</p>
      )}
    </motion.div>
  )
}
