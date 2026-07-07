import React from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth.jsx'

export default function Navbar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  function handleLogout() {
    logout()
    navigate('/')
  }

  return (
    <header className="sticky top-0 z-20 bg-paper/90 dark:bg-ink/90 backdrop-blur border-b border-slate-150 dark:border-inkline">
      <nav className="max-w-6xl mx-auto flex items-center justify-between px-6 py-4">
        <Link to="/" className="font-display font-700 text-lg tracking-tight">
          Resume<span className="mark-highlight">Mark</span>
        </Link>

        <div className="flex items-center gap-6 font-body text-sm">
          {user ? (
            <>
              <Link to="/dashboard" className="hover:opacity-70">Dashboard</Link>
              <span className="text-ink/50 dark:text-paper/50">{user.full_name}</span>
              <button
                onClick={handleLogout}
                className="px-3 py-1.5 rounded-card border border-slate-150 dark:border-inkline hover:bg-flag/10"
              >
                Log out
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="hover:opacity-70">Log in</Link>
              <Link
                to="/register"
                className="px-3 py-1.5 rounded-card bg-ink text-paper dark:bg-highlight dark:text-ink font-medium"
              >
                Get started
              </Link>
            </>
          )}
        </div>
      </nav>
    </header>
  )
}
