import { useEffect, useState } from 'react'
import { ErrorMessage, EmptyState, LoadingSpinner } from '../../components/common/Feedback'
import { PageHeader } from '../../components/common/PageTools'
import { NoticeList } from '../../components/notices/NoticeList'
import { getNotices } from '../../services/noticeService'

export function NoticesPage() { const [notices, setNotices] = useState(null), [error, setError] = useState(''); const load = () => { setError(''); getNotices().then(setNotices).catch((err) => setError(err.message)) }; useEffect(load, []); return <>{<PageHeader title="Notice board" description="Important notices are pinned first." />}{error ? <ErrorMessage message={error} onRetry={load} /> : !notices ? <LoadingSpinner label="Loading notices..." /> : notices.length ? <NoticeList notices={notices} /> : <EmptyState title="No notices available" message="Check back later for society updates." />}</> }
