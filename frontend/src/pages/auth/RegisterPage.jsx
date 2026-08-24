import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'

export function RegisterPage() {
  const [values, setValues] = useState({ name: '', email: '', password: '', phone: '', flat_no: '' })
  const [error, setError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const { register } = useAuth()
  const navigate = useNavigate()
  const update = (field) => (event) => setValues({ ...values, [field]: event.target.value })
  const submit = async (event) => {
    event.preventDefault(); setError(''); setIsSubmitting(true)
    try { await register({ ...values, phone: values.phone || null }); navigate('/resident', { replace: true }) } catch (requestError) { setError(requestError.message) } finally { setIsSubmitting(false) }
  }
  return <div><h1 id="auth-title">Create an account</h1><p className="muted">Register as a resident to submit and track maintenance requests.</p><form className="auth-form" onSubmit={submit}><label>Full name<input value={values.name} onChange={update('name')} autoComplete="name" maxLength="150" required /></label><label>Email<input type="email" value={values.email} onChange={update('email')} autoComplete="email" required /></label><label>Flat number<input value={values.flat_no} onChange={update('flat_no')} maxLength="20" required /></label><label>Phone <span className="optional">Optional</span><input type="tel" value={values.phone} onChange={update('phone')} autoComplete="tel" maxLength="20" /></label><label>Password<input type="password" value={values.password} onChange={update('password')} autoComplete="new-password" minLength="6" maxLength="72" required /></label>{error && <p className="form-error" role="alert">{error}</p>}<button className="primary-button" type="submit" disabled={isSubmitting}>{isSubmitting ? 'Creating account...' : 'Create account'}</button></form><p className="auth-footer">Already have an account? <Link to="/login">Sign in</Link></p></div>
}
