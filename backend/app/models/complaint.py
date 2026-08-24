import enum
from datetime import datetime

from sqlalchemy import String, Text, ForeignKey, DateTime, Enum as SAEnum, func, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ComplaintStatus(str, enum.Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"


class ComplaintPriority(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class Complaint(Base):
    __tablename__ = "complaints"
    __table_args__ = (
        Index("ix_complaints_status", "status"),
        Index("ix_complaints_priority", "priority"),
        Index("ix_complaints_created_at", "created_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    resident_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    photo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[ComplaintStatus] = mapped_column(
        SAEnum(ComplaintStatus, name="complaintstatus", create_constraint=True),
        nullable=False,
        default=ComplaintStatus.OPEN,
    )
    priority: Mapped[ComplaintPriority] = mapped_column(
        SAEnum(ComplaintPriority, name="complaintpriority", create_constraint=True),
        nullable=False,
        default=ComplaintPriority.LOW,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    resident: Mapped["User"] = relationship(back_populates="complaints", lazy="selectin")  # noqa: F821
    category: Mapped["Category"] = relationship(back_populates="complaints", lazy="selectin")  # noqa: F821
    status_history: Mapped[list["ComplaintStatusHistory"]] = relationship(  # noqa: F821
        back_populates="complaint", lazy="selectin", order_by="ComplaintStatusHistory.created_at"
    )