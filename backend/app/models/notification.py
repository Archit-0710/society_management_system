import enum
from datetime import datetime

from sqlalchemy import String, Text, ForeignKey, DateTime, Enum as SAEnum, func, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class NotificationType(str, enum.Enum):
    COMPLAINT_STATUS_CHANGED = "COMPLAINT_STATUS_CHANGED"
    IMPORTANT_NOTICE = "IMPORTANT_NOTICE"


class NotificationStatus(str, enum.Enum):
    PENDING = "PENDING"
    SENT = "SENT"
    FAILED = "FAILED"


class Notification(Base):
    __tablename__ = "notifications"
    __table_args__ = (
        Index("ix_notifications_status", "status"),
        Index("ix_notifications_type", "type"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    recipient_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )
    complaint_id: Mapped[int | None] = mapped_column(
        ForeignKey("complaints.id"), nullable=True
    )
    notice_id: Mapped[int | None] = mapped_column(
        ForeignKey("notices.id", ondelete="SET NULL"), nullable=True
    )
    type: Mapped[NotificationType] = mapped_column(
        SAEnum(NotificationType, name="notificationtype", create_constraint=True),
        nullable=False,
    )
    status: Mapped[NotificationStatus] = mapped_column(
        SAEnum(NotificationStatus, name="notificationstatus", create_constraint=True),
        nullable=False,
        default=NotificationStatus.PENDING,
    )
    subject: Mapped[str | None] = mapped_column(String(255), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    recipient: Mapped["User"] = relationship(back_populates="notifications", lazy="selectin")  # noqa: F821
    complaint: Mapped["Complaint | None"] = relationship(lazy="selectin")  # noqa: F821
    notice: Mapped["Notice | None"] = relationship(lazy="selectin")  # noqa: F821