  import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Trophy } from 'lucide-react'
import { listAchievements } from '../api/achievements'

export default function AchievementsSummaryCard() {
  const [achievements, setAchievements] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    listAchievements().then(setAchievements).catch(() => {}).finally(() => setLoading(false))
  }, [])

  if (loading) return null

  const earned = achievements.filter((a) => a.earned)

  return (
    <Link
      to="/achievements"
      className="flex items-center justify-between rounded-2xl bg-white p-5 shadow-sm transition hover:shadow-md dark:bg-slate-900"
    >
      <div className="flex items-center gap-3">
        <Trophy size={20} className="text-amber-500" />
        <div>
          <p className="text-sm font-semibold text-slate-900 dark:text-white">Achievements</p>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            {earned.length} of {achievements.length} unlocked
          </p>
        </div>
      </div>
      <div className="flex gap-1 text-xl">
        {achievements.map((a) => (
          <span key={a.code} className={a.earned ? '' : 'opacity-25 grayscale'}>{a.icon}</span>
        ))}
      </div>
    </Link>
  )
}
