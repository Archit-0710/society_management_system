from datetime import datetime

from sqlalchemy import String, Text, ForeignKey, DateTime, Enum as SAEnum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.complaint import ComplaintStatus


class ComplaintStatusHistory(Base):
    __tablename__ = "complaint_status_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    complaint_id: Mapped[int] = mapped_column(
        ForeignKey("complaints.id"), nullable=False, index=True
    )
    old_status: Mapped[ComplaintStatus | None] = mapped_column(
        SAEnum(ComplaintStatus, name="complaintstatus", create_constraint=False),
        nullable=True,
    )
    new_status: Mapped[ComplaintStatus] = mapped_column(
        SAEnum(ComplaintStatus, name="complaintstatus", create_constraint=False),
        nullable=False,
    )
    changed_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    complaint: Mapped["Complaint"] = relationship(back_populates="status_history", lazy="selectin")  # noqa: F821
    changed_by_user: Mapped["User"] = relationship(lazy="selectin")  # noqa: F821