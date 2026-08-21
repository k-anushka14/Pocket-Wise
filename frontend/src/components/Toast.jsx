import { useEffect } from 'react'

const VARIANT_STYLES = {
  success: 'bg-emerald-600',
  error: 'bg-red-600',
}

export default function Toast({ message, variant = 'success', onDismiss }) {
  useEffect(() => {
    if (!message) return
    const timer = setTimeout(onDismiss, 3000)
    return () => clearTimeout(timer)
  }, [message, onDismiss])

  if (!message) return null

  return (
    <div
      className={`fixed bottom-6 left-1/2 z-50 -translate-x-1/2 rounded-lg px-4 py-2 text-sm text-white shadow-lg ${VARIANT_STYLES[variant]}`}
    >
      {message}
    </div>
  )
}
