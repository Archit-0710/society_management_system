import { apiRequest, clearStoredToken, storeToken } from './api'

async function createSession(path, payload) {
  const token = await apiRequest(path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  storeToken(token.access_token)
  return getCurrentUser()
}

export const login = (credentials) => createSession('/api/auth/login', credentials)
export const register = (details) => createSession('/api/auth/register', details)
export const getCurrentUser = () => apiRequest('/api/auth/me')
export const clearSession = clearStoredToken
