import { apiRequest } from './api'

export const getCategories = () => apiRequest('/api/categories')
export const createCategory = (payload) => apiRequest('/api/admin/categories', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) })
export const updateCategory = (id, payload) => apiRequest(`/api/admin/categories/${id}`, { method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) })
