import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { ComplaintList } from '../../components/complaints/ComplaintList'
import { EmptyState, ErrorMessage, LoadingSpinner } from '../../components/common/Feedback'
import { PageHeader, Pagination } from '../../components/common/PageTools'
import { getCategories } from '../../services/categoryService'
import { getMyComplaints } from '../../services/complaintService'

export function MyComplaintsPage() {
  const [result, setResult] = useState(null), [categories, setCategories] = useState([]), [filters, setFilters] = useState({ status: '', category_id: '', page: 1, limit: 10 }), [error, setError] = useState('')
  const load = async () => { setError(''); try { const [complaints, categoryData] = await Promise.all([getMyComplaints(filters), getCategories()]); setResult(complaints); setCategories(categoryData) } catch (err) { setError(err.message) } }
  useEffect(() => { load() }, [filters])
  const setFilter = (key, value) => setFilters({ ...filters, [key]: value, page: 1 })
  return <><PageHeader title="My complaints" description="Follow the status of every maintenance request." action={<Link className="primary-button compact" to="/resident/complaints/new">New complaint</Link>} /><div className="filter-bar"><label>Status<select value={filters.status} onChange={(event) => setFilter('status', event.target.value)}><option value="">All statuses</option><option>OPEN</option><option>IN_PROGRESS</option><option>RESOLVED</option></select></label><label>Category<select value={filters.category_id} onChange={(event) => setFilter('category_id', event.target.value)}><option value="">All categories</option>{categories.map((category) => <option value={category.id} key={category.id}>{category.name}</option>)}</select></label></div>{error ? <ErrorMessage message={error} onRetry={load} /> : !result ? <LoadingSpinner /> : result.complaints.length ? <><ComplaintList complaints={result.complaints} /><Pagination {...result} onChange={(page) => setFilters({ ...filters, page })} /></> : <EmptyState title="No complaints yet" message="Create a complaint to request maintenance." />}</>
}
