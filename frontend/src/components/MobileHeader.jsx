import { useState } from 'react'
import { Menu } from 'lucide-react'
import MobileMenu from './MobileMenu'

export default function MobileHeader() {
  const [open, setOpen] = useState(false)

  return (
    <>
      <header className="sticky top-0 z-40 flex h-14 items-center justify-between border-b border-slate-200 bg-white px-4 dark:border-slate-800 dark:bg-slate-900 md:hidden">
        <button onClick={() => setOpen(true)} aria-label="Open menu" className="text-slate-600 dark:text-slate-300">
          <Menu size={22} />
        </button>
        <span className="text-base font-semibold text-slate-900 dark:text-white">PocketWise</span>
        <span className="w-[22px]" /> {/* balances the hamburger for centered title */}
      </header>
      <MobileMenu open={open} onClose={() => setOpen(false)} />
    </>
  )
}
