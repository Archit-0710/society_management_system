"""Dashboard service for computing statistics."""
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.config import settings
from app.models.complaint import Complaint, ComplaintStatus, ComplaintPriority
from app.models.category import Category
from app.models.notice import Notice
from app.models.notification import Notification, NotificationStatus
from app.models.user import User, UserRole


def get_dashboard_stats(db: Session) -> dict:
    """Compute dashboard statistics for admin."""
    
    # Complaint counts by status
    total_complaints = db.query(Complaint).count()
    open_complaints = db.query(Complaint).filter(Complaint.status == ComplaintStatus.OPEN).count()
    in_progress_complaints = db.query(Complaint).filter(Complaint.status == ComplaintStatus.IN_PROGRESS).count()
    resolved_complaints = db.query(Complaint).filter(Complaint.status == ComplaintStatus.RESOLVED).count()
    
    # Overdue complaints
    threshold_date = datetime.now(timezone.utc) - timedelta(days=settings.OVERDUE_THRESHOLD_DAYS)
    overdue_complaints = db.query(Complaint).filter(
        Complaint.status != ComplaintStatus.RESOLVED,
        Complaint.created_at < threshold_date
    ).count()
    
    # Complaints by category
    category_stats = db.query(
        Category.name,
        func.count(Complaint.id)
    ).join(Complaint, Category.id == Complaint.category_id).group_by(Category.name).all()
    
    complaints_by_category = {name: count for name, count in category_stats}
    
    # Complaints by priority
    priority_stats = db.query(
        Complaint.priority,
        func.count(Complaint.id)
    ).group_by(Complaint.priority).all()
    
    complaints_by_priority = {priority.value: count for priority, count in priority_stats}
    
    # Other counts
    total_residents = db.query(User).filter(User.role == UserRole.RESIDENT).count()
    total_categories = db.query(Category).count()
    total_notices = db.query(Notice).count()
    
    # Notification stats
    pending_notifications = db.query(Notification).filter(
        Notification.status == NotificationStatus.PENDING
    ).count()
    failed_notifications = db.query(Notification).filter(
        Notification.status == NotificationStatus.FAILED
    ).count()
    
    return {
        "total_complaints": total_complaints,
        "open_complaints": open_complaints,
        "in_progress_complaints": in_progress_complaints,
        "resolved_complaints": resolved_complaints,
        "overdue_complaints": overdue_complaints,
        "complaints_by_category": complaints_by_category,
        "complaints_by_priority": complaints_by_priority,
        "total_residents": total_residents,
        "total_categories": total_categories,
        "total_notices": total_notices,
        "pending_notifications": pending_notifications,
        "failed_notifications": failed_notifications,
    }