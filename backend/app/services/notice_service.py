from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.notice import Notice
from app.schemas.notice import NoticeCreate, NoticeUpdate


def get_notices(db: Session, skip: int = 0, limit: int = 50) -> list[Notice]:
    """
    Get all notices ordered by importance and creation date.
    Important notices appear first, then ordered by newest first.
    """
    return (
        db.query(Notice)
        .order_by(desc(Notice.is_important), desc(Notice.created_at))
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_notice_by_id(db: Session, notice_id: int) -> Notice | None:
    """Get notice by ID."""
    return db.query(Notice).filter(Notice.id == notice_id).first()


def create_notice(db: Session, request: NoticeCreate, admin_id: int) -> Notice:
    """Create a new notice (admin only)."""
    notice = Notice(
        title=request.title,
        content=request.content,
        is_important=request.is_important,
        created_by=admin_id,
    )
    db.add(notice)
    db.commit()
    db.refresh(notice)
    
    # Create notifications for all residents if this is an important notice
    if request.is_important:
        from app.services.notification_service import create_important_notice_notifications
        create_important_notice_notifications(db, notice.id, notice.title)
    
    return notice


def update_notice(db: Session, notice_id: int, request: NoticeUpdate) -> Notice:
    """Update a notice (admin only)."""
    notice = get_notice_by_id(db, notice_id)
    if not notice:
        raise ValueError("Notice not found")
    
    was_important = notice.is_important
    
    # Update fields
    if request.title is not None:
        notice.title = request.title
    if request.content is not None:
        notice.content = request.content
    if request.is_important is not None:
        notice.is_important = request.is_important
    
    db.commit()
    db.refresh(notice)
    
    # Create notifications if notice became important
    if not was_important and notice.is_important:
        from app.services.notification_service import create_important_notice_notifications
        create_important_notice_notifications(db, notice.id, notice.title)
    
    return notice


def delete_notice(db: Session, notice_id: int) -> bool:
    """Delete a notice (admin only)."""
    notice = get_notice_by_id(db, notice_id)
    if not notice:
        raise ValueError("Notice not found")
    
    db.delete(notice)
    db.commit()
    return True