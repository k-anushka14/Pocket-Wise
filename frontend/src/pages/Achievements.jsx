import { useEffect, useState } from 'react'
import Layout from '../components/Layout'
import LoadingState from '../components/LoadingState'
import ErrorState from '../components/ErrorState'
import AchievementBadge from '../components/AchievementBadge'
import { listAchievements } from '../api/achievements'

export default function Achievements() {
  const [achievements, setAchievements] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  async function load() {
    setLoading(true)
    setError('')
    try {
      setAchievements(await listAchievements())
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const earnedCount = achievements.filter((a) => a.earned).length

  return (
    <Layout>
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-slate-900 dark:text-white">Achievements</h1>
        {!loading && !error && (
          <p className="text-sm text-slate-500 dark:text-slate-400">
            {earnedCount} of {achievements.length} unlocked
          </p>
        )}
      </div>

      {loading && <LoadingState label="Checking your progress…" />}
      {!loading && error && <ErrorState message={error} onRetry={load} />}

      {!loading && !error && (
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-5">
          {achievements.map((a) => (
            <AchievementBadge key={a.code} achievement={a} />
          ))}
        </div>
      )}
    </Layout>
  )
}
