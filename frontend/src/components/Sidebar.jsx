import React from 'react'
import { NavLink } from 'react-router-dom'

const links = [
  { to: '/dashboard', label: 'Overview', end: true },
  { to: '/dashboard/upload', label: 'Upload Resume' },
  { to: '/dashboard/jd-match', label: 'Job Match' },
  { to: '/dashboard/ai-tools', label: 'AI Tools' },
  { to: '/dashboard/history', label: 'History' },
  { to: '/dashboard/settings', label: 'Settings' },
]

export default function Sidebar() {
  return (
    <aside className="w-56 shrink-0 border-r border-slate-150 dark:border-inkline min-h-[calc(100vh-65px)] py-6 px-3 hidden md:block">
      <nav className="flex flex-col gap-1">
        {links.map((link) => (
          <NavLink
            key={link.to}
            to={link.to}
            end={link.end}
            className={({ isActive }) =>
              `px-3 py-2 rounded-card text-sm font-medium transition-colors ${
                isActive
                  ? 'bg-highlight/20 text-ink dark:text-paper'
                  : 'text-ink/60 dark:text-paper/60 hover:bg-slate-150/50 dark:hover:bg-inkline'
              }`
            }
          >
            {link.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  )
}
