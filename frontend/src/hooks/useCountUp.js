import { useEffect, useState } from 'react'

export function useCountUp(target, duration = 800) {
  const [value, setValue] = useState(0)

  useEffect(() => {
    const startTime = performance.now()
    const startValue = 0

    const animate = (currentTime) => {
      const elapsed = currentTime - startTime
      const progress = Math.min(elapsed / duration, 1)

      // Ease-out animation
      const easedProgress = 1 - Math.pow(1 - progress, 3)

      setValue(startValue + (target - startValue) * easedProgress)

      if (progress < 1) {
        requestAnimationFrame(animate)
      }
    }

    requestAnimationFrame(animate)
  }, [target, duration])

  return value
}