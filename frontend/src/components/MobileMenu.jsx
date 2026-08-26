import { NavLink } from 'react-router-dom'
import { X } from 'lucide-react'
import { NAV_LINKS } from '../utils/navLinks'
import ThemeToggle from './ThemeToggle'

export default function MobileMenu({ open, onClose }) {
  if (!open) return null

  return (
    <div className="fixed inset-0 z-50 md:hidden">
      <div className="absolute inset-0 bg-black/40" onClick={onClose} />
      <div className="absolute inset-y-0 left-0 flex w-72 flex-col bg-white p-4 shadow-xl dark:bg-slate-900">
        <div className="mb-6 flex items-center justify-between px-2">
          <span className="text-lg font-semibold text-slate-900 dark:text-white">PocketWise</span>
          <button onClick={onClose} aria-label="Close menu" className="text-slate-400 hover:text-slate-700 dark:hover:text-slate-200">
            <X size={20} />
          </button>
        </div>
        <nav className="flex-1 space-y-1 overflow-y-auto">
          {NAV_LINKS.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              onClick={onClose}
              className={({ isActive }) =>
                `flex items-center gap-2 rounded-lg px-3 py-2.5 text-sm font-medium transition ${
                  isActive
                    ? 'bg-slate-900 text-white dark:bg-white dark:text-slate-900'
                    : 'text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800'
                }`
              }
            >
              <Icon size={16} />
              {label}
            </NavLink>
          ))}
        </nav>
        <div className="mt-2 border-t border-slate-100 pt-2 dark:border-slate-800">
          <ThemeToggle />
        </div>
      </div>
    </div>
  )
}
