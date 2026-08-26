import { LayoutDashboard, Receipt, Wallet, PiggyBank, Target, Repeat, Users, FileBarChart, MessageSquare, HandCoins, Trophy } from 'lucide-react'

// Single source of truth for navigation -- both Sidebar (desktop) and
// MobileMenu (mobile) render from this so they can never drift apart.
export const NAV_LINKS = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/transactions', label: 'Transactions', icon: Receipt },
  { to: '/income', label: 'Income', icon: Wallet },
  { to: '/budgets', label: 'Budgets', icon: PiggyBank },
  { to: '/goals', label: 'Goals', icon: Target },
  { to: '/recurring', label: 'Recurring', icon: Repeat },
  { to: '/splits', label: 'Splits', icon: Users },
  { to: '/reports', label: 'Reports', icon: FileBarChart },
  { to: '/assistant', label: 'AI Assistant', icon: MessageSquare },
  { to: '/afford', label: 'Can I Afford?', icon: HandCoins },
  { to: '/achievements', label: 'Achievements', icon: Trophy },
]
