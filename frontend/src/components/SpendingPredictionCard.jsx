import { useEffect, useState } from 'react'
import { getPredictions } from '../api/predictions'
import { formatCurrency, toLabel } from '../utils/constants'
import LoadingState from './LoadingState'

export default function SpendingPredictionCard() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    getPredictions()
      .then(setData)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="rounded-2xl bg-white p-5 shadow-sm dark:bg-slate-900">
      <h3 className="mb-4 text-sm font-semibold text-slate-900 dark:text-white">Spending Prediction</h3>

      {loading && <LoadingState label="Projecting…" />}
      {!loading && error && <p className="text-sm text-red-500">{error}</p>}

      {!loading && !error && data && (
        <div className="space-y-3">
          <p className="text-sm text-slate-600 dark:text-slate-300">
            📊 At your current rate, you're projected to spend{' '}
            <span className="font-semibold text-slate-900 dark:text-white">
              {formatCurrency(data.projected_month_total)}
            </span>{' '}
            this month.
          </p>

          {data.projected_overrun != null && Number(data.projected_overrun) > 0 && (
            <p className="text-sm text-amber-600 dark:text-amber-400">
              ⚠️ You may exceed your total budget by {formatCurrency(data.projected_overrun)}.
            </p>
          )}

          {data.category_predictions.length > 0 && (
            <div className="space-y-1.5 pt-2">
              {data.category_predictions.slice(0, 4).map((c) => (
                <div key={c.category} className="flex justify-between text-xs text-slate-500 dark:text-slate-400">
                  <span>{toLabel(c.category)}</span>
                  <span>{formatCurrency(c.current_spent)} → {formatCurrency(c.projected_spent)}</span>
                </div>
              ))}
            </div>
          )}

          <p className="pt-1 text-xs text-slate-400 dark:text-slate-500">
            {data.days_elapsed} days elapsed, {data.days_remaining} remaining this month.
          </p>
        </div>
      )}
    </div>
  )
}
