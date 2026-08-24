from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func, case, desc, and_, or_

from app.core.config import settings
from app.models.complaint import Complaint, ComplaintStatus, ComplaintPriority
from app.models.complaint_history import ComplaintStatusHistory
from app.models.category import Category
from app.models.user import User
from app.schemas.complaint import ComplaintCreate, ComplaintStatusUpdate, ComplaintPriorityUpdate


def create_complaint(db: Session, category_id: int, description: str, photo_url: str | None, resident_id: int) -> Complaint:
    """Create a new complaint and initial status history."""
    # Verify category exists and is active
    category = db.query(Category).filter(
        Category.id == category_id,
        Category.is_active == True
    ).first()
    if not category:
        raise ValueError("Category not found or inactive")
    
    # Create complaint
    complaint = Complaint(
        resident_id=resident_id,
        category_id=category_id,
        description=description,
        photo_url=photo_url,
        status=ComplaintStatus.OPEN,
        priority=ComplaintPriority.LOW,
    )
    db.add(complaint)
    db.flush()  # Get complaint ID before creating history
    
    # Create initial status history
    history = ComplaintStatusHistory(
        complaint_id=complaint.id,
        old_status=None,
        new_status=ComplaintStatus.OPEN,
        changed_by=resident_id,
        note="Complaint created",
    )
    db.add(history)
    
    db.commit()
    db.refresh(complaint)
    return complaint


def get_complaints(
    db: Session,
    resident_id: int | None = None,
    category_id: int | None = None,
    status: str | None = None,
    skip: int = 0,
    limit: int = 50
) -> tuple[list[Complaint], int]:
    """
    Get complaints with basic filters for residents (paginated, sorted newest first).
    
    Returns: (complaints, total_count)
    """
    query = db.query(Complaint)
    
    if resident_id is not None:
        query = query.filter(Complaint.resident_id == resident_id)
    
    if category_id is not None:
        query = query.filter(Complaint.category_id == category_id)
    
    if status is not None:
        try:
            status_enum = ComplaintStatus(status.upper())
            query = query.filter(Complaint.status == status_enum)
        except ValueError:
            # If invalid status, query returns nothing or ignores it to be safe
            return [], 0
    
    # Get total count
    total = query.count()
    
    # Apply pagination and ordering
    complaints = query.order_by(Complaint.created_at.desc()).offset(skip).limit(limit).all()
    
    return complaints, total


def get_admin_complaints(
    db: Session,
    status: str | None = None,
    category_id: int | None = None,
    priority: str | None = None,
    overdue: bool | None = None,
    from_date: datetime | None = None,
    to_date: datetime | None = None,
    skip: int = 0,
    limit: int = 50
) -> tuple[list[Complaint], int]:
    """
    Get complaints for admins with extensive filtering and default ordering.
    Ordering: overdue complaints first (if unresolved and created_at < threshold), then older complaints first.
    """
    query = db.query(Complaint)
    
    # Apply filters
    if category_id is not None:
        query = query.filter(Complaint.category_id == category_id)
        
    if status is not None:
        try:
            status_enum = ComplaintStatus(status.upper())
            query = query.filter(Complaint.status == status_enum)
        except ValueError:
            return [], 0
            
    if priority is not None:
        try:
            priority_enum = ComplaintPriority(priority.upper())
            query = query.filter(Complaint.priority == priority_enum)
        except ValueError:
            return [], 0

    # Overdue threshold calculations
    now_utc = datetime.now(timezone.utc)
    threshold_date = now_utc - timedelta(days=settings.OVERDUE_THRESHOLD_DAYS)

    # Condition for overdue
    overdue_cond = and_(
        Complaint.status != ComplaintStatus.RESOLVED,
        Complaint.created_at < threshold_date
    )

    if overdue is True:
        query = query.filter(overdue_cond)
    elif overdue is False:
        query = query.filter(~overdue_cond)

    if from_date is not None:
        query = query.filter(Complaint.created_at >= from_date)
        
    if to_date is not None:
        query = query.filter(Complaint.created_at <= to_date)

    total = query.count()

    # Default ordering: overdue complaints first, then older complaints first
    # We use a case statement where overdue = 0 (high priority order) and others = 1
    # created_at in ascending order (older first)
    is_overdue_expr = case(
        (overdue_cond, 0),
        else_=1
    )
    
    complaints = (
        query.order_by(is_overdue_expr.asc(), Complaint.created_at.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    
    return complaints, total


def get_complaint_by_id(db: Session, complaint_id: int) -> Complaint | None:
    """Get complaint by ID."""
    return db.query(Complaint).filter(Complaint.id == complaint_id).first()


def check_complaint_ownership(complaint: Complaint, user_id: int, user_role: str) -> bool:
    """Check if user owns the complaint or is an admin."""
    return user_role == "ADMIN" or complaint.resident_id == user_id


def validate_status_transition(current_status: ComplaintStatus, new_status: ComplaintStatus) -> bool:
    """
    Validate if status transition is allowed.
    Valid transitions:
    - OPEN -> IN_PROGRESS
    - OPEN -> RESOLVED
    - IN_PROGRESS -> RESOLVED
    """
    if current_status == new_status:
        return False
    
    if current_status == ComplaintStatus.RESOLVED:
        return False
    
    valid_transitions = {
        ComplaintStatus.OPEN: [ComplaintStatus.IN_PROGRESS, ComplaintStatus.RESOLVED],
        ComplaintStatus.IN_PROGRESS: [ComplaintStatus.RESOLVED],
    }
    
    allowed = valid_transitions.get(current_status, [])
    return new_status in allowed


def update_complaint_status(
    db: Session,
    complaint_id: int,
    request: ComplaintStatusUpdate,
    admin_id: int
) -> Complaint:
    """Update complaint status (admin only)."""
    complaint = get_complaint_by_id(db, complaint_id)
    if not complaint:
        raise ValueError("Complaint not found")
    
    new_status = ComplaintStatus(request.status.upper())
    
    # Validate transition
    if not validate_status_transition(complaint.status, new_status):
        raise ValueError(
            f"Invalid status transition from {complaint.status.value} to {new_status.value}"
        )
    
    old_status = complaint.status
    complaint.status = new_status
    
    # Set resolved_at if transitioning to RESOLVED
    if new_status == ComplaintStatus.RESOLVED:
        complaint.resolved_at = datetime.now(timezone.utc)
    
    # Create history record
    history = ComplaintStatusHistory(
        complaint_id=complaint.id,
        old_status=old_status,
        new_status=new_status,
        changed_by=admin_id,
        note=request.note,
    )
    db.add(history)
    
    # Create notification for the resident
    from app.services.notification_service import create_complaint_status_notification
    create_complaint_status_notification(
        db=db,
        complaint_id=complaint.id,
        recipient_id=complaint.resident_id,
        old_status=old_status.value,
        new_status=new_status.value
    )
    
    db.commit()
    db.refresh(complaint)
    return complaint


def update_complaint_priority(
    db: Session,
    complaint_id: int,
    request: ComplaintPriorityUpdate,
    admin_id: int
) -> Complaint:
    """Update complaint priority (admin only)."""
    complaint = get_complaint_by_id(db, complaint_id)
    if not complaint:
        raise ValueError("Complaint not found")
    
    # Can't change priority of resolved complaints
    if complaint.status == ComplaintStatus.RESOLVED:
        raise ValueError("Cannot change priority of resolved complaint")
    
    new_priority = ComplaintPriority(request.priority.upper())
    complaint.priority = new_priority
    
    db.commit()
    db.refresh(complaint)
    return complaint


def is_complaint_overdue(complaint: Complaint) -> bool:
    """Check if complaint is overdue based on creation date and current status."""
    if complaint.status == ComplaintStatus.RESOLVED:
        return False
    
    threshold_days = settings.OVERDUE_THRESHOLD_DAYS
    threshold_date = datetime.now(timezone.utc) - timedelta(days=threshold_days)
    
    return complaint.created_at < threshold_date


def escalate_priority_if_needed(db: Session, complaint: Complaint) -> bool:
    """
    Escalate complaint priority based on age.
    """
    if complaint.status == ComplaintStatus.RESOLVED:
        return False
    
    now = datetime.now(timezone.utc)
    age_days = (now - complaint.created_at).days
    
    escalated = False
    
    if complaint.priority == ComplaintPriority.LOW and age_days >= settings.LOW_TO_MEDIUM_DAYS:
        complaint.priority = ComplaintPriority.MEDIUM
        escalated = True
    elif complaint.priority == ComplaintPriority.MEDIUM and age_days >= settings.MEDIUM_TO_HIGH_DAYS:
        complaint.priority = ComplaintPriority.HIGH
        escalated = True
    
    if escalated:
        db.commit()
        db.refresh(complaint)
    
    return escalated