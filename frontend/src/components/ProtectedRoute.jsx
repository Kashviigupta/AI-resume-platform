import React from 'react'
import { Navigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth.jsx'

// Wrap any page that requires login: <ProtectedRoute><Dashboard /></ProtectedRoute>
export default function ProtectedRoute({ children }) {
  const { user, loading } = useAuth()

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center font-mono text-sm text-ink/60 dark:text-paper/60">
        Checking session…
      </div>
    )
  }

  if (!user) {
    return <Navigate to="/login" replace />
  }

  return children
}
