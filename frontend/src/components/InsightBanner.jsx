const SEVERITY_STYLES = {
  critical: 'bg-red-50 border-red-200 text-red-700 dark:bg-red-950 dark:border-red-900 dark:text-red-300',
  warning: 'bg-amber-50 border-amber-200 text-amber-700 dark:bg-amber-950 dark:border-amber-900 dark:text-amber-300',
  info: 'bg-blue-50 border-blue-200 text-blue-700 dark:bg-blue-950 dark:border-blue-900 dark:text-blue-300',
}

export default function InsightBanner({ insights }) {
  if (!insights || insights.length === 0) return null

  return (
    <div className="space-y-2">
      {insights.map((insight, i) => (
        <div key={i} className={`rounded-xl border px-4 py-2.5 text-sm ${SEVERITY_STYLES[insight.severity] || SEVERITY_STYLES.info}`}>
          {insight.message}
        </div>
      ))}
    </div>
  )
}
