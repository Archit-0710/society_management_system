import { apiRequest } from './api'

export const getNotices = () => apiRequest('/api/notices')
export const getNotice = (id) => apiRequest(`/api/notices/${id}`)
export const createNotice = (payload) => apiRequest('/api/admin/notices', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) })
export const updateNotice = (id, payload) => apiRequest(`/api/admin/notices/${id}`, { method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) })
export const deleteNotice = (id) => apiRequest(`/api/admin/notices/${id}`, { method: 'DELETE' })
