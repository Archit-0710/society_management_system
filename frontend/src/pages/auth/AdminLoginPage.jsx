import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'

export function AdminLoginPage() {
  const [values, setValues] = useState({ email: '', password: '' })
  const [error, setError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const { login, logout } = useAuth()
  const navigate = useNavigate()

  const submit = async (event) => {
    event.preventDefault()
    setError('')
    setIsSubmitting(true)
    try {
      const user = await login(values)
      if (user.role !== 'ADMIN') {
        logout()
        setError('This account does not have administrator access.')
        return
      }
      navigate('/admin', { replace: true })
    } catch (requestError) {
      setError(requestError.message)
    } finally {
      setIsSubmitting(false)
    }
  }

  return <div><h1 id="auth-title">Administrator sign in</h1><p className="muted">Use an administrator account to manage maintenance operations.</p><form className="auth-form" onSubmit={submit}><label>Email<input type="email" value={values.email} onChange={(event) => setValues({ ...values, email: event.target.value })} autoComplete="email" required /></label><label>Password<input type="password" value={values.password} onChange={(event) => setValues({ ...values, password: event.target.value })} autoComplete="current-password" required /></label>{error && <p className="form-error" role="alert">{error}</p>}<button className="primary-button" type="submit" disabled={isSubmitting}>{isSubmitting ? 'Signing in...' : 'Sign in as administrator'}</button></form><p className="auth-footer"><Link to="/login">Resident sign in</Link></p></div>
}
