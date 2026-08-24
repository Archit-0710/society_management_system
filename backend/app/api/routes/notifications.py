from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.api.dependencies import require_admin
from app.core.database import get_db
from app.models.user import User
from app.schemas.notification import NotificationResponse, NotificationListResponse
from app.services import notification_service

router = APIRouter(tags=["Notifications"])


@router.get("/admin/notifications", response_model=NotificationListResponse)
def get_notifications(
    status_filter: str | None = Query(None, alias="status"),
    type_filter: str | None = Query(None, alias="type"),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Get all notifications (admin only)."""
    skip = (page - 1) * limit
    notifications, total = notification_service.get_notifications(
        db=db,
        status=status_filter,
        type_filter=type_filter,
        skip=skip,
        limit=limit
    )
    
    return NotificationListResponse(
        notifications=[
            NotificationResponse(
                id=n.id,
                recipient_id=n.recipient_id,
                complaint_id=n.complaint_id,
                notice_id=n.notice_id,
                type=n.type.value,
                status=n.status.value,
                subject=n.subject,
                error_message=n.error_message,
                created_at=n.created_at,
                sent_at=n.sent_at,
                recipient_email=n.recipient.email,
            )
            for n in notifications
        ],
        total=total,
        page=page,
        limit=limit,
    )


@router.post("/admin/notifications/send", status_code=status.HTTP_200_OK)
def send_pending_notifications(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Process and send all pending notifications (admin only)."""
    count = notification_service.send_pending_notifications(db)
    return {"message": f"Processed {count} notifications"}