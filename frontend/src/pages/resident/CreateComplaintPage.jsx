import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ErrorMessage, LoadingSpinner } from '../../components/common/Feedback'
import { PageHeader } from '../../components/common/PageTools'
import { getCategories } from '../../services/categoryService'
import { createComplaint } from '../../services/complaintService'

const validTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
export function CreateComplaintPage() {
  const [categories, setCategories] = useState(null), [values, setValues] = useState({ category_id: '', description: '' }), [photo, setPhoto] = useState(null), [preview, setPreview] = useState(''), [error, setError] = useState(''), [saving, setSaving] = useState(false)
  const navigate = useNavigate()
  useEffect(() => { getCategories().then(setCategories).catch((err) => setError(err.message)) }, [])
  const choosePhoto = (event) => { const file = event.target.files?.[0]; setError(''); if (!file) return; if (!validTypes.includes(file.type) || file.size > 5 * 1024 * 1024) { setPhoto(null); setPreview(''); setError('Use a JPEG, PNG, GIF, or WEBP image up to 5 MB.'); return }; setPhoto(file); setPreview(URL.createObjectURL(file)) }
  const submit = async (event) => { event.preventDefault(); setError(''); setSaving(true); try { const formData = new FormData(); formData.append('category_id', values.category_id); formData.append('description', values.description); if (photo) formData.append('photo', photo); const complaint = await createComplaint(formData); navigate(`/resident/complaints/${complaint.id}`) } catch (err) { setError(err.message) } finally { setSaving(false) } }
  if (error && !categories) return <ErrorMessage message={error} />
  if (!categories) return <LoadingSpinner label="Loading categories..." />
  return <><PageHeader title="New complaint" description="Describe the maintenance issue and add a photo if it helps." /><form className="panel-form" onSubmit={submit}><label>Category<select value={values.category_id} onChange={(event) => setValues({ ...values, category_id: event.target.value })} required><option value="">Choose a category</option>{categories.map((category) => <option value={category.id} key={category.id}>{category.name}</option>)}</select></label><label>Description<textarea value={values.description} onChange={(event) => setValues({ ...values, description: event.target.value })} minLength="10" maxLength="2000" required /></label><label>Photo <span className="optional">Optional, maximum 5 MB</span><input type="file" accept="image/jpeg,image/png,image/gif,image/webp" onChange={choosePhoto} /></label>{preview && <img className="photo-preview" src={preview} alt="Complaint upload preview" />}{error && <p className="form-error" role="alert">{error}</p>}<button className="primary-button compact" disabled={saving}>{saving ? 'Submitting...' : 'Submit complaint'}</button></form></>
}
