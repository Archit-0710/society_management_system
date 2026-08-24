export function LoadingSpinner({ label = 'Loading...' }) { return <p className="loading-state" role="status">{label}</p> }
export function ErrorMessage({ message, onRetry }) { return <div className="error-state" role="alert"><span>{message}</span>{onRetry && <button type="button" className="text-button" onClick={onRetry}>Try again</button>}</div> }
export function EmptyState({ title, message }) { return <section className="empty-state"><h2>{title}</h2><p>{message}</p></section> }
