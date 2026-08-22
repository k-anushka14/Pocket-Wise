import { useEffect, useState } from 'react'
import Layout from '../components/Layout'
import LoadingState from '../components/LoadingState'
import ErrorState from '../components/ErrorState'
import HealthScoreCard from '../components/HealthScoreCard'
import InsightBanner from '../components/InsightBanner'
import { getMonthlyReport } from '../api/reports'
import { formatCurrency, toLabel } from '../utils/constants'

export default function Reports() {
  const [report, setReport] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  async function load() {
    setLoading(true)
    setError('')
    try {
      setReport(await getMonthlyReport())
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  return (
    <Layout>
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-slate-900 dark:text-white">Monthly Report</h1>
        {report && <p className="text-sm text-slate-500 dark:text-slate-400">{report.month_label}</p>}
      </div>

      {loading && <LoadingState label="Building your report…" />}
      {!loading && error && <ErrorState message={error} onRetry={load} />}

      {!loading && !error && report && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            <div className="rounded-2xl bg-white p-5 shadow-sm dark:bg-slate-900">
              <p className="text-sm text-slate-500 dark:text-slate-400">Income</p>
              <p className="text-xl font-semibold text-emerald-600 dark:text-emerald-400">{formatCurrency(report.income)}</p>
            </div>
            <div className="rounded-2xl bg-white p-5 shadow-sm dark:bg-slate-900">
              <p className="text-sm text-slate-500 dark:text-slate-400">Expenses</p>
              <p className="text-xl font-semibold text-red-600 dark:text-red-400">{formatCurrency(report.expenses)}</p>
            </div>
            <div className="rounded-2xl bg-white p-5 shadow-sm dark:bg-slate-900">
              <p className="text-sm text-slate-500 dark:text-slate-400">Savings ({report.savings_rate_pct}%)</p>
              <p className="text-xl font-semibold text-slate-900 dark:text-white">{formatCurrency(report.savings)}</p>
            </div>
          </div>

          <HealthScoreCard health={report.financial_health} />

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div className="rounded-2xl bg-white p-5 shadow-sm dark:bg-slate-900">
              <p className="text-sm text-slate-500 dark:text-slate-400">Top category</p>
              <p className="text-lg font-medium text-slate-900 dark:text-white">
                {report.top_category ? toLabel(report.top_category) : '—'}
              </p>
            </div>
            <div className="rounded-2xl bg-white p-5 shadow-sm dark:bg-slate-900">
              <p className="text-sm text-slate-500 dark:text-slate-400">Largest expense</p>
              {report.largest_expense ? (
                <p className="text-lg font-medium text-slate-900 dark:text-white">
                  {report.largest_expense.description || toLabel(report.largest_expense.category)}{' '}
                  <span className="text-sm text-slate-500 dark:text-slate-400">
                    ({formatCurrency(report.largest_expense.amount)})
                  </span>
                </p>
              ) : (
                <p className="text-lg font-medium text-slate-900 dark:text-white">—</p>
              )}
            </div>
          </div>

          <div className="rounded-2xl bg-white p-5 shadow-sm dark:bg-slate-900">
            <p className="mb-2 text-sm font-semibold text-slate-900 dark:text-white">Needs vs Wants</p>
            <p className="text-sm text-slate-600 dark:text-slate-300">
              Needs: {formatCurrency(report.needs)} · Wants: {formatCurrency(report.wants)}
            </p>
          </div>

          {report.insights.length > 0 && (
            <div>
              <p className="mb-2 text-sm font-semibold text-slate-900 dark:text-white">Insights this month</p>
              <InsightBanner insights={report.insights} />
            </div>
          )}
        </div>
      )}
    </Layout>
  )
}
