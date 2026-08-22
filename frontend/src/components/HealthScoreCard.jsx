function scoreColor(score) {
  if (score >= 75) return { ring: 'stroke-emerald-500', text: 'text-emerald-600 dark:text-emerald-400', label: 'Strong' }
  if (score >= 50) return { ring: 'stroke-amber-500', text: 'text-amber-600 dark:text-amber-400', label: 'Fair' }
  return { ring: 'stroke-red-500', text: 'text-red-600 dark:text-red-400', label: 'Needs attention' }
}

export default function HealthScoreCard({ health }) {
  const { score, strengths, weaknesses } = health
  const colors = scoreColor(score)
  const circumference = 2 * Math.PI * 40
  const offset = circumference - (score / 100) * circumference

  return (
    <div className="rounded-2xl bg-white p-5 shadow-sm dark:bg-slate-900">
      <h3 className="mb-4 text-sm font-semibold text-slate-900 dark:text-white">Financial Health</h3>
      <div className="flex flex-col items-center gap-4 sm:flex-row sm:items-start">
        <div className="relative flex h-28 w-28 shrink-0 items-center justify-center">
          <svg viewBox="0 0 100 100" className="h-28 w-28 -rotate-90">
            <circle cx="50" cy="50" r="40" strokeWidth="8" fill="none" className="stroke-slate-100 dark:stroke-slate-800" />
            <circle
              cx="50" cy="50" r="40" strokeWidth="8" fill="none"
              strokeLinecap="round"
              strokeDasharray={circumference}
              strokeDashoffset={offset}
              className={colors.ring}
            />
          </svg>
          <div className="absolute flex flex-col items-center">
            <span className={`text-2xl font-bold ${colors.text}`}>{score}</span>
            <span className="text-xs text-slate-400 dark:text-slate-500">/100</span>
          </div>
        </div>

        <div className="flex-1 space-y-2">
          <p className={`text-sm font-medium ${colors.text}`}>{colors.label}</p>
          {strengths.slice(0, 2).map((s, i) => (
            <p key={`s-${i}`} className="text-xs text-slate-600 dark:text-slate-300">✅ {s}</p>
          ))}
          {weaknesses.slice(0, 2).map((w, i) => (
            <p key={`w-${i}`} className="text-xs text-slate-600 dark:text-slate-300">⚠️ {w}</p>
          ))}
        </div>
      </div>
    </div>
  )
}
