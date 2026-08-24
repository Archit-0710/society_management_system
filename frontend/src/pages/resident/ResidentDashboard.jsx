import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { ComplaintList } from '../../components/complaints/ComplaintList'
import { ErrorMessage, LoadingSpinner } from '../../components/common/Feedback'
import { PageHeader } from '../../components/common/PageTools'
import { NoticeList } from '../../components/notices/NoticeList'
import { getMyComplaints } from '../../services/complaintService'
import { getNotices } from '../../services/noticeService'

export function ResidentDashboard() {
  const [data, setData] = useState(null); const [error, setError] = useState('')
  const load = async () => { setError(''); try { const [complaints, notices] = await Promise.all([getMyComplaints({ limit: 100 }), getNotices()]); setData({ complaints: complaints.complaints, notices: notices.slice(0, 3) }) } catch (err) { setError(err.message) } }
  useEffect(() => { load() }, [])
  if (error) return <ErrorMessage message={error} onRetry={load} />
  if (!data) return <LoadingSpinner label="Loading your overview..." />
  const counts = ['OPEN', 'IN_PROGRESS', 'RESOLVED'].map((status) => [status.replace('_', ' '), data.complaints.filter((item) => item.status === status).length])
  return <><PageHeader title="Resident overview" description="Track your maintenance requests and society notices." action={<Link className="primary-button compact" to="/resident/complaints/new">New complaint</Link>} /><div className="stat-grid">{[['Total', data.complaints.length], ...counts].map(([label, value]) => <article className="stat-card" key={label}><span>{label}</span><strong>{value}</strong></article>)}</div><section className="content-section"><div className="section-heading"><h2>Recent complaints</h2><Link to="/resident/complaints">View all</Link></div>{data.complaints.length ? <ComplaintList complaints={data.complaints.slice(0, 5)} /> : <p className="muted">No complaints yet.</p>}</section><section className="content-section"><div className="section-heading"><h2>Recent notices</h2><Link to="/resident/notices">View all</Link></div>{data.notices.length ? <NoticeList notices={data.notices} /> : <p className="muted">No notices available.</p>}</section></>
}
