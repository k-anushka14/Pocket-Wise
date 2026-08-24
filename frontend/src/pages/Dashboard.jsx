import { useEffect, useState } from 'react'
import { Wallet, TrendingDown, PiggyBank, Target } from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { getDashboard } from '../api/dashboard'
import Layout from '../components/Layout'
import LoadingState from '../components/LoadingState'
import ErrorState from '../components/ErrorState'
import DashboardCard from '../components/DashboardCard'
import SpendingChart from '../components/SpendingChart'
import CategoryChart from '../components/CategoryChart'
import BudgetProgress from '../components/BudgetProgress'
import InsightBanner from '../components/InsightBanner'
import NeedsWantsBar from '../components/NeedsWantsBar'
import HealthScoreCard from '../components/HealthScoreCard'
import SpendingPredictionCard from '../components/SpendingPredictionCard'
import AchievementsSummaryCard from '../components/AchievementsSummaryCard'
import { formatCurrency, toLabel } from '../utils/constants'

export default function Dashboard() {
  const { user } = useAuth()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  async function load() {
    setLoading(true)
    setError('')
    try {
      setData(await getDashboard())
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const greeting = new Date().getHours() < 12 ? 'Good morning' : new Date().getHours() < 18 ? 'Good afternoon' : 'Good evening'
  const firstName = user?.email?.split('@')[0]

  return (
    <Layout>
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-slate-900 dark:text-white">{greeting} 👋</h1>
        <p className="text-sm text-slate-500 dark:text-slate-400">Here's your financial overview, {firstName}.</p>
      </div>

      {loading && <LoadingState label="Crunching your numbers…" />}
      {!loading && error && <ErrorState message={error} onRetry={load} />}

      {!loading && !error && data && (
        <div className="space-y-6">
          {/* Smart insights / overspending alerts */}
          <InsightBanner insights={data.insights} />

          {/* Top cards */}
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <DashboardCard label="Balance" value={data.remaining_balance} icon={Wallet} accent="slate" />
            <DashboardCard label="Total Expenses" value={data.total_expenses} icon={TrendingDown} accent="red" />
            <DashboardCard label="Total Income" value={data.total_income} icon={PiggyBank} accent="emerald" />
            <DashboardCard label="Savings" value={data.total_savings} icon={Target} accent="blue" />
          </div>

          {/* Daily spending recommendation */}
          <div className="rounded-2xl bg-slate-900 p-5 text-white dark:bg-white dark:text-slate-900">
            <p className="text-sm opacity-80">
              You have {formatCurrency(data.daily_spending_limit.remaining_balance)} remaining.{' '}
              {data.daily_spending_limit.days_remaining} day{data.daily_spending_limit.days_remaining !== 1 ? 's' : ''} left this month.
            </p>
            <p className="mt-1 text-xl font-semibold">
              Recommended daily spending: {formatCurrency(data.daily_spending_limit.recommended_daily_spending)}
            </p>
          </div>

          {/* Charts */}
          <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
            <SpendingChart data={data.monthly_spending} />
            <CategoryChart data={data.spending_by_category} />
          </div>

          {/* Needs vs Wants */}
          <NeedsWantsBar needsVsWants={data.needs_vs_wants} />

          {/* Financial Health Score + No-spend days */}
          <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
            <div className="lg:col-span-2">
              <HealthScoreCard health={data.financial_health} />
            </div>
            <div className="rounded-2xl bg-white p-5 shadow-sm dark:bg-slate-900">
              <h3 className="mb-2 text-sm font-semibold text-slate-900 dark:text-white">No-spend days</h3>
              <p className="text-3xl font-bold text-slate-900 dark:text-white">🔥 {data.no_spend_days.count}</p>
              <p className="text-xs text-slate-500 dark:text-slate-400">this month so far</p>
              <p className="mt-2 text-xs text-slate-500 dark:text-slate-400">
                Longest streak: {data.no_spend_days.longest_streak} day{data.no_spend_days.longest_streak !== 1 ? 's' : ''}
              </p>
            </div>
          </div>

          {/* Spending Prediction */}
          <SpendingPredictionCard />

          {/* Achievements */}
          <AchievementsSummaryCard />

          {/* Budgets */}
          <div className="rounded-2xl bg-white p-5 shadow-sm dark:bg-slate-900">
            <h3 className="mb-4 text-sm font-semibold text-slate-900 dark:text-white">Budget status</h3>
            {data.budgets.length === 0 ? (
              <p className="text-sm text-slate-500 dark:text-slate-400">
                No budgets set for this month yet. Head to the Budgets page to create one.
              </p>
            ) : (
              <div className="space-y-3">
                {data.budgets.map((b) => (
                  <BudgetProgress key={b.id} budget={b} />
                ))}
              </div>
            )}
          </div>

          {/* Recent transactions */}
          <div className="rounded-2xl bg-white p-5 shadow-sm dark:bg-slate-900">
            <h3 className="mb-4 text-sm font-semibold text-slate-900 dark:text-white">Recent transactions</h3>
            {data.recent_transactions.length === 0 ? (
              <p className="text-sm text-slate-500 dark:text-slate-400">No transactions yet.</p>
            ) : (
              <div className="divide-y divide-slate-100 dark:divide-slate-800">
                {data.recent_transactions.map((t) => (
                  <div key={t.id} className="flex items-center justify-between py-2.5">
                    <div>
                      <p className="text-sm font-medium text-slate-900 dark:text-white">{t.description || toLabel(t.category)}</p>
                      <p className="text-xs text-slate-500 dark:text-slate-400">{toLabel(t.category)} · {t.date}</p>
                    </div>
                    <span className="text-sm font-medium text-slate-900 dark:text-white">{formatCurrency(t.amount)}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </Layout>
  )
}
