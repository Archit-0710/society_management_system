import { apiRequest } from './api'

export const getDashboard = () => apiRequest('/api/admin/dashboard')
