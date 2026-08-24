import { apiRequest } from './api'

export const getNotifications = (params = {}) => {
  const query = new URLSearchParams(Object.entries(params).filter(([, value]) => value))
  return apiRequest(`/api/admin/notifications${query.size ? `?${query}` : ''}`)
}
