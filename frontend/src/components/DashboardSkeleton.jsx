function Block({ className = '' }) {
  return <div className={`animate-pulse rounded-2xl bg-slate-100 dark:bg-slate-800 ${className}`} />
}

export default function DashboardSkeleton() {
  return (
    <div className="space-y-6">
      <Block className="h-16" />

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Block className="h-24" />
        <Block className="h-24" />
        <Block className="h-24" />
        <Block className="h-24" />
      </div>

      <Block className="h-20" />

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Block className="h-64" />
        <Block className="h-64" />
      </div>

      <Block className="h-40" />
      <Block className="h-32" />
    </div>
  )
}
