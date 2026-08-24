import { Link, Outlet } from 'react-router-dom'

export function AuthLayout() {
  return <main className="auth-layout"><section className="auth-panel" aria-labelledby="auth-title"><Link className="brand" to="/login">SocietyCare</Link><p className="eyebrow">Society Maintenance Tracker</p><Outlet /></section></main>
}
