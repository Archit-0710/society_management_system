const configuredApiBaseUrl = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/$/, '')
const apiBaseUrl = import.meta.env.DEV ? '' : configuredApiBaseUrl
const tokenKey = 'society_maintenance_access_token'

export const getStoredToken = () => localStorage.getItem(tokenKey)
export const storeToken = (token) => localStorage.setItem(tokenKey, token)
export const clearStoredToken = () => localStorage.removeItem(tokenKey)

export async function apiRequest(path, options = {}) {
  const token = getStoredToken()
  const response = await fetch(`${apiBaseUrl}${path}`, {
    ...options,
    headers: { Accept: 'application/json', ...(token ? { Authorization: `Bearer ${token}` } : {}), ...options.headers },
  })

  if (response.status === 204) return null
  const payload = await response.json().catch(() => null)
  if (!response.ok) {
    if (response.status === 401 && token) window.dispatchEvent(new Event('auth:expired'))
    throw new Error(payload?.detail || 'Something went wrong. Please try again.')
  }
  return payload
}
