import { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'

const destinationFor = (user) => user.role === 'ADMIN' ? '/admin' : '/resident'

export function LoginPage() {
  const [values, setValues] = useState({ email: '', password: '' })
  const [error, setError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const { login } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const submit = async (event) => {
    event.preventDefault(); setError(''); setIsSubmitting(true)
    try {
      const user = await login(values)
      const requestedPath = location.state?.from?.pathname
      const validDestination = requestedPath && (user.role === 'ADMIN' ? requestedPath.startsWith('/admin') : requestedPath.startsWith('/resident'))
      navigate(validDestination ? requestedPath : destinationFor(user), { replace: true })
    } catch (requestError) { setError(requestError.message) } finally { setIsSubmitting(false) }
  }
  return <div><h1 id="auth-title">Welcome back</h1><p className="muted">Sign in to manage your society maintenance requests.</p><form className="auth-form" onSubmit={submit}><label>Email<input type="email" value={values.email} onChange={(event) => setValues({ ...values, email: event.target.value })} autoComplete="email" required /></label><label>Password<input type="password" value={values.password} onChange={(event) => setValues({ ...values, password: event.target.value })} autoComplete="current-password" required /></label>{error && <p className="form-error" role="alert">{error}</p>}<button className="primary-button" type="submit" disabled={isSubmitting}>{isSubmitting ? 'Signing in...' : 'Sign in'}</button></form><p className="auth-footer">New resident? <Link to="/register">Create an account</Link><br /><Link to="/admin/login">Administrator sign in</Link></p></div>
}
