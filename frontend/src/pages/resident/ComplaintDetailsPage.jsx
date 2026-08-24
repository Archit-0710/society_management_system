import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { ComplaintDetail } from '../../components/complaints/ComplaintDetail'
import { ErrorMessage, LoadingSpinner } from '../../components/common/Feedback'
import { PageHeader } from '../../components/common/PageTools'
import { getComplaint } from '../../services/complaintService'

export function ComplaintDetailsPage() { const { id } = useParams(); const [complaint, setComplaint] = useState(null), [error, setError] = useState(''); const load = () => { setComplaint(null); getComplaint(id).then(setComplaint).catch((err) => setError(err.message)) }; useEffect(load, [id]); if (error) return <ErrorMessage message={error} onRetry={load} />; if (!complaint) return <LoadingSpinner label="Loading complaint..." />; return <><PageHeader title={`Complaint #${complaint.id}`} description="Track the current maintenance progress." /><ComplaintDetail complaint={complaint} /></> }
