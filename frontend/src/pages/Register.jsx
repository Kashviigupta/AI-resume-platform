import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { useAuth } from '../hooks/useAuth.jsx'

export default function Register() {
  const { register } = useAuth()
  const navigate = useNavigate()
  const [fullName, setFullName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [submitting, setSubmitting] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    setSubmitting(true)
    try {
      await register(fullName, email, password)
      toast.success('Account created!')
      navigate('/dashboard')
    } catch (err) {
      let msg
      if (err.response) {
        // Backend responded with an error (e.g. 400 email already taken)
        msg = err.response.data?.detail || 'Registration failed.'
      } else if (err.request) {
        // Request went out but no response came back — backend is down,
        // wrong VITE_API_URL, or the request was blocked by CORS.
        msg = 'Could not reach the server. Is the backend running, and does its FRONTEND_ORIGIN match the URL this page is open at?'
      } else {
        msg = err.message || 'Registration failed.'
      }
      toast.error(msg)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-6">
      <div className="w-full max-w-sm card p-8">
        <h1 className="font-display font-700 text-2xl mb-1">Create your account</h1>
        <p className="text-sm text-ink/60 dark:text-paper/60 mb-6">
          Already have one?{' '}
          <Link to="/login" className="underline hover:text-highlight">
            Log in
          </Link>
        </p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Full name</label>
            <input
              type="text"
              required
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              className="w-full px-3 py-2 rounded-card border border-slate-150 dark:border-inkline bg-transparent focus:outline-none focus:ring-2 focus:ring-highlight"
              placeholder="Kashvi Gupta"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Email</label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-3 py-2 rounded-card border border-slate-150 dark:border-inkline bg-transparent focus:outline-none focus:ring-2 focus:ring-highlight"
              placeholder="you@example.com"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Password</label>
            <input
              type="password"
              required
              minLength={8}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-3 py-2 rounded-card border border-slate-150 dark:border-inkline bg-transparent focus:outline-none focus:ring-2 focus:ring-highlight"
              placeholder="At least 8 characters"
            />
          </div>
          <button
            type="submit"
            disabled={submitting}
            className="w-full py-2.5 rounded-card bg-ink text-paper dark:bg-highlight dark:text-ink font-medium disabled:opacity-50"
          >
            {submitting ? 'Creating account…' : 'Create account'}
          </button>
        </form>
      </div>
    </div>
  )
}
