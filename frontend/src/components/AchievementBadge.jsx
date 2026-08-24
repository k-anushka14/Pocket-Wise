export default function AchievementBadge({ achievement }) {
  const { name, description, icon, earned, earned_at } = achievement

  return (
    <div
      className={`rounded-2xl border p-5 text-center transition ${
        earned
          ? 'border-amber-200 bg-amber-50 dark:border-amber-900 dark:bg-amber-950'
          : 'border-slate-200 bg-slate-50 opacity-60 grayscale dark:border-slate-800 dark:bg-slate-900'
      }`}
    >
      <div className="mb-2 text-4xl">{icon}</div>
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
    </div>
  )
}
