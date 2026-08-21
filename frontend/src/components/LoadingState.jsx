export default function LoadingState({ label = 'Loading…' }) {
  return (
    <div className="flex h-full min-h-[40vh] w-full items-center justify-center">
      <div className="flex items-center gap-3 text-slate-500 dark:text-slate-400">
        <span className="h-5 w-5 animate-spin rounded-full border-2 border-slate-300 border-t-slate-600 dark:border-slate-600 dark:border-t-slate-300" />
        <span className="text-sm">{label}</span>
      </div>
    </div>
  )
}
