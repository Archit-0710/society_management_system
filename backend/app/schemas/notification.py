from datetime import datetime
from pydantic import BaseModel


class NotificationResponse(BaseModel):
    id: int
    recipient_id: int
    complaint_id: int | None
    notice_id: int | None
    type: str
    status: str
    subject: str | None
    error_message: str | None
    created_at: datetime
    sent_at: datetime | None
    
    # Include related data
    recipient_email: str | None = None

    class Config:
        from_attributes = True


class NotificationListResponse(BaseModel):
    """Paginated notification list response."""
    notifications: list[NotificationResponse]
    total: int
    page: int
    limit: int