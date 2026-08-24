"""Create, deliver, and track notification emails."""
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.notification import Notification, NotificationStatus, NotificationType
from app.models.user import User, UserRole
from app.services.email_service import email_service


def _deliver_notification(db: Session, notification: Notification) -> bool:
    """Deliver one persisted notification and record its outcome."""
    try:
        recipient = notification.recipient
        if notification.type == NotificationType.COMPLAINT_STATUS_CHANGED:
            complaint = notification.complaint
            if not complaint:
                raise ValueError("Complaint not found")
            history = complaint.status_history
            old_status = history[-2].new_status.value if len(history) >= 2 else None
            success, error = email_service.send_complaint_status_email(
                to_email=recipient.email,
                resident_name=recipient.name,
                complaint_id=complaint.id,
                old_status=old_status,
                new_status=complaint.status.value,
                note=history[-1].note if history else None,
            )
        elif notification.type == NotificationType.IMPORTANT_NOTICE:
            notice = notification.notice
            if not notice:
                raise ValueError("Notice not found")
            success, error = email_service.send_important_notice_email(
                to_email=recipient.email,
                resident_name=recipient.name,
                notice_title=notice.title,
                notice_content=notice.content,
            )
        else:
            raise ValueError("Unsupported notification type")

        if success:
            notification.status = NotificationStatus.SENT
            notification.sent_at = datetime.now(timezone.utc)
            notification.error_message = None
        else:
            notification.status = NotificationStatus.FAILED
            notification.error_message = error or "Email delivery failed"
        db.commit()
        return success
    except Exception as exc:
        notification.status = NotificationStatus.FAILED
        notification.error_message = str(exc)
        db.commit()
        return False


def create_complaint_status_notification(
    db: Session, complaint_id: int, recipient_id: int, old_status: str | None, new_status: str
) -> Notification:
    notification = Notification(
        recipient_id=recipient_id,
        complaint_id=complaint_id,
        type=NotificationType.COMPLAINT_STATUS_CHANGED,
        status=NotificationStatus.PENDING,
        subject=f"Complaint #{complaint_id} Status Updated",
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    _deliver_notification(db, notification)
    db.refresh(notification)
    return notification


def create_important_notice_notifications(db: Session, notice_id: int, notice_title: str) -> list[Notification]:
    residents = db.query(User).filter(User.role == UserRole.RESIDENT).all()
    notifications = [
        Notification(
            recipient_id=resident.id,
            notice_id=notice_id,
            type=NotificationType.IMPORTANT_NOTICE,
            status=NotificationStatus.PENDING,
            subject=f"IMPORTANT: {notice_title}",
        )
        for resident in residents
    ]
    db.add_all(notifications)
    db.commit()
    for notification in notifications:
        db.refresh(notification)
        _deliver_notification(db, notification)
    return notifications


def send_pending_notifications(db: Session) -> int:
    pending = db.query(Notification).filter(Notification.status == NotificationStatus.PENDING).all()
    for notification in pending:
        _deliver_notification(db, notification)
    return len(pending)


def get_notifications(
    db: Session,
    status: NotificationStatus | None = None,
    type_filter: NotificationType | None = None,
    skip: int = 0,
    limit: int = 50,
) -> tuple[list[Notification], int]:
    query = db.query(Notification)
    if status is not None:
        query = query.filter(Notification.status == status)
    if type_filter is not None:
        query = query.filter(Notification.type == type_filter)
    total = query.count()
    return query.order_by(Notification.created_at.desc()).offset(skip).limit(limit).all(), total
