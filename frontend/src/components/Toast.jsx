import { useEffect } from 'react'
import { AnimatePresence, motion } from 'framer-motion'

const VARIANT_STYLES = {
  success: 'bg-emerald-600',
  error: 'bg-red-600',
}

const DURATION_MS = 3000

export default function Toast({ message, variant = 'success', onDismiss }) {
  useEffect(() => {
    if (!message) return
    const timer = setTimeout(onDismiss, DURATION_MS)
    return () => clearTimeout(timer)
  }, [message, onDismiss])

  return (
    <AnimatePresence>
      {message && (
        <motion.div
          className={`fixed bottom-6 left-1/2 z-50 w-[min(90vw,320px)] -translate-x-1/2 overflow-hidden rounded-xl text-white shadow-lg ${VARIANT_STYLES[variant]}`}
          initial={{ opacity: 0, y: 24, scale: 0.95 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: 12, scale: 0.97 }}
          transition={{ duration: 0.25, ease: [0.16, 1, 0.3, 1] }}
        >
          <div className="px-4 py-3 text-sm">{message}</div>
          <motion.div
            className="h-0.5 bg-white/50"
            initial={{ width: '100%' }}
            animate={{ width: '0%' }}
            transition={{ duration: DURATION_MS / 1000, ease: 'linear' }}
          />
        </motion.div>
      )}
    </AnimatePresence>
  )
}
