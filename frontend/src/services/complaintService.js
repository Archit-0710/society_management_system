import { apiRequest } from './api'

const queryString = (params) => {
  const query = new URLSearchParams(Object.entries(params).filter(([, value]) => value !== '' && value !== null && value !== undefined && value !== false))
  return query.size ? `?${query}` : ''
}

export const getMyComplaints = (params = {}) => apiRequest(`/api/complaints/my${queryString(params)}`)
export const getAdminComplaints = (params = {}) => apiRequest(`/api/admin/complaints${queryString(params)}`)
export const getComplaint = (id) => apiRequest(`/api/complaints/${id}`)
export const createComplaint = (formData) => apiRequest('/api/complaints', { method: 'POST', body: formData })
export const updateComplaintStatus = (id, payload) => apiRequest(`/api/admin/complaints/${id}/status`, { method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) })
export const updateComplaintPriority = (id, payload) => apiRequest(`/api/admin/complaints/${id}/priority`, { method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) })
