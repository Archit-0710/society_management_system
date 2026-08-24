import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

const dashboardFor = (user) => user.role === 'ADMIN' ? '/admin' : '/resident'

export function RequireAuth({ role }) {
  const { user, isLoading } = useAuth()
  const location = useLocation()
  if (isLoading) return <main className="route-loading">Loading your session...</main>
  if (!user) return <Navigate to="/login" replace state={{ from: location }} />
  if (role && user.role !== role) return <Navigate to={dashboardFor(user)} replace />
  return <Outlet />
}

export function PublicOnly() {
  const { user, isLoading } = useAuth()
  if (isLoading) return <main className="route-loading">Loading your session...</main>
  return user ? <Navigate to={dashboardFor(user)} replace /> : <Outlet />
}
