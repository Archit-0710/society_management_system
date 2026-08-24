from pydantic import BaseModel


class DashboardStats(BaseModel):
    """Dashboard statistics response."""
    total_complaints: int
    open_complaints: int
    in_progress_complaints: int
    resolved_complaints: int
    overdue_complaints: int
    
    complaints_by_category: dict[str, int]
    complaints_by_priority: dict[str, int]
    
    total_residents: int
    total_categories: int
    total_notices: int
    
    pending_notifications: int
    failed_notifications: int