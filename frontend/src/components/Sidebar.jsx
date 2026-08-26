import { NavLink } from 'react-router-dom'
import { NAV_LINKS } from '../utils/navLinks'
import ThemeToggle from './ThemeToggle'

export default function Sidebar() {
  return (
    <aside className="hidden w-56 shrink-0 flex-col border-r border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-slate-900 md:flex">
      <div className="mb-6 px-2 text-lg font-semibold text-slate-900 dark:text-white">PocketWise</div>
      <nav className="flex-1 space-y-1 overflow-y-auto">
        {NAV_LINKS.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium transition ${
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
    </aside>
  )
}
