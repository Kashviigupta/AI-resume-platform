import React, { createContext, useContext, useEffect, useState } from 'react'
import { loginUser, registerUser, fetchCurrentUser } from '../services/authService'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true) // true while we check for an existing session

  // On first load, if a token is already in localStorage, try to restore the
  // session by fetching the current user. This is what makes login "persistent"
  // across page refreshes instead of logging the user out every reload.
  useEffect(() => {
    const token = localStorage.getItem('access_token')
    if (!token) {
      setLoading(false)
      return
    }
    fetchCurrentUser()
      .then((data) => setUser(data))
      .catch(() => {
        localStorage.removeItem('access_token')
        localStorage.removeItem('user')
      })
      .finally(() => setLoading(false))
  }, [])

  async function login(email, password) {
    const data = await loginUser({ email, password })
    localStorage.setItem('access_token', data.access_token)
    const me = await fetchCurrentUser()
    localStorage.setItem('user', JSON.stringify(me))
    setUser(me)
    return me
  }

  async function register(fullName, email, password) {
    await registerUser({ fullName, email, password })
    // Auto-login right after successful registration
    return login(email, password)
  }

  function logout() {
    localStorage.removeItem('access_token')
    localStorage.removeItem('user')
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside an <AuthProvider>')
  return ctx
}
