import { Link, NavLink, Outlet, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

const links = [['/resident', 'Overview', true], ['/resident/complaints', 'My complaints'], ['/resident/complaints/new', 'New complaint'], ['/resident/notices', 'Notice board']]

export function ResidentLayout() {
  return <Shell title="Resident portal" links={links} />
}

export function Shell({ title, links }) {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const handleLogout = () => { logout(); navigate('/login', { replace: true }) }
  return <div className="application-shell"><aside className="sidebar"><Link className="brand" to="/">SocietyCare</Link><p className="sidebar-title">{title}</p><nav aria-label={`${title} navigation`}>{links.map(([to, label, end]) => <NavLink key={to} to={to} end={end} className="nav-link">{label}</NavLink>)}</nav><div className="account-menu"><span>{user.name}</span><button type="button" className="logout-button" onClick={handleLogout}>Log out</button></div></aside><main className="page-content"><Outlet /></main></div>
}
