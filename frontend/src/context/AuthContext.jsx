import { createContext, useContext, useEffect, useState } from 'react'
import { clearSession, getCurrentUser, login as loginRequest, register as registerRequest } from '../services/authService'
import { getStoredToken } from '../services/api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    let active = true
    const restoreSession = async () => {
      if (!getStoredToken()) {
        if (active) setIsLoading(false)
        return
      }
      try {
        const currentUser = await getCurrentUser()
        if (active) setUser(currentUser)
      } catch {
        clearSession()
      } finally {
        if (active) setIsLoading(false)
      }
    }
    const expireSession = () => {
      clearSession()
      setUser(null)
    }
    restoreSession()
    window.addEventListener('auth:expired', expireSession)
    return () => {
      active = false
      window.removeEventListener('auth:expired', expireSession)
    }
  }, [])

  const login = async (credentials) => {
    const currentUser = await loginRequest(credentials)
    setUser(currentUser)
    return currentUser
  }
  const register = async (details) => {
    const currentUser = await registerRequest(details)
    setUser(currentUser)
    return currentUser
  }
  const logout = () => {
    clearSession()
    setUser(null)
  }

  return <AuthContext.Provider value={{ user, isLoading, login, register, logout }}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) throw new Error('useAuth must be used within AuthProvider')
  return context
}
