export function StatusBadge({ status }) { return <span className={`badge status-${status?.toLowerCase().replace('_', '-')}`}>{status?.replace('_', ' ')}</span> }
export function PriorityBadge({ priority }) { return <span className={`badge priority-${priority?.toLowerCase()}`}>{priority}</span> }
